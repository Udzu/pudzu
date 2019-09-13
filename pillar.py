import re
import os
import os.path
import logging
import abc as ABC
import numpy as np

from collections import namedtuple
from enum import Enum
from functools import partial, reduce
from io import BytesIO
from itertools import zip_longest
from numbers import Real, Integral
from urllib.parse import urlparse
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps, ImageFilter, ImageChops
from pudzu.utils import *

pyphen = optional_import("pyphen")
requests = optional_import("requests")
ndimage = optional_import("scipy.ndimage")
bidi_layout = optional_import_from("bidi.algorithm", "get_display", identity)
arabic_reshape = optional_import_from("arabic_reshaper", "reshape", identity)

# Various pillow utilities, mostly monkey patched onto the Image, ImageDraw and ImageColor classes

logger = logging.getLogger('pillar')
logger.setLevel(logging.DEBUG)

# Alignment and padding

class Alignment():
    """Alignment class, initialized from one or two floats between 0 and 1."""
    
    def __init__(self, align):
        if isinstance(align, Real):
            return self.__init__((align, align))
        elif non_string_sequence(align, Real) and len(align) == 2:
            if not all(0 <= x <= 1 for x in align):
                raise ValueError("Alignment values should be between 0 and 1: got {}".format(align))
            self.xy = align
        elif isinstance(align, Alignment):
            self.xy = align.xy
        else:
            raise TypeError("Alignment expects one or two floats between 0 and 1: got {}".format(align))
            
    def __repr__(self):
        return "Alignment(x={:.0f}%, y={:.0f}%)".format(self.x * 100, self.y * 100)
        
    def __getitem__(self, key):
        return self.xy[key]
        
    def __len__(self):
        return 2

    @property
    def x(self): return self.xy[0]
    @property
    def y(self): return self.xy[1]
        
class Padding():
    """Padding class, initialized from one, two or four integers."""
    
    def __init__(self, padding=0):
        if padding is None:
            return self.__init__((0,0,0,0))
        elif isinstance(padding, Integral):
            return self.__init__((padding, padding, padding, padding))
        elif non_string_sequence(padding, Integral) and len(padding) == 2:
            return self.__init__((padding[0], padding[1], padding[0], padding[1]))
        elif non_string_sequence(padding, Integral) and len(padding) == 4:
            if not all(0 <= x for x in padding):
                raise ValueError("Padding values should be positive: got {}".format(padding))
            self.padding = list(padding)
        elif isinstance(padding, Padding):
            self.padding = list(padding.padding)
        else:
            raise TypeError("Padding expects one, two or four integers: got {}".format(padding))
            
    def __repr__(self):
        return "Padding(l={}, u={}, r={}, d={})".format(self.l, self.u, self.r, self.d)
        
    def __getitem__(self, key):
        return self.padding[key]
        
    def __len__(self):
        return 4
        
    def __add__(self, other):
        if isinstance(other, Padding):
            return Padding([x + y for x,y in zip(self.padding, other.padding)])
        else:
            return NotImplemented

    def update(self, other):
        if isinstance(other, Padding):
            self.padding = list(other.padding)
        else:
            raise TypeError("update expects another Padding object: got {}".format(padding))
        
    @property
    def l(self): return self.padding[0]
    @property
    def u(self): return self.padding[1]
    @property
    def r(self): return self.padding[2]
    @property
    def d(self): return self.padding[3]
    @property
    def x(self): return self.l + self.r
    @property
    def y(self): return self.u + self.d

class BoundingBox():
    """Bounding box class initialized from 4 LURD coordinates or a collection of points with optional padding. Not used much at the moment."""
        
    def __init__(self, box):
        if isinstance(box, Image.Image):
            self.corners = (0, 0, box.width-1, box.height-1)
        elif non_string_sequence(box, Integral) and len(box) == 4:
            self.corners = tuple(box)
        elif non_string_sequence(box) and all(non_string_sequence(point, Integral) and len(point) == 2 for point in box):
            self.corners = (min(x for x,y in box), min(y for x,y in box), max(x for x,y in box), max(y for x,y in box))
        else:
            raise TypeError("BoundingBox expects four coordinates or a collection of points: got {}".format(box))
            
    def __repr__(self):
        return "BoundingBox(l={}, u={}, r={}, d={})".format(self.l, self.u, self.r, self.d)

    def __getitem__(self, key):
        return self.corners[key]
        
    def __len__(self):
        return 4
        
    def __contains__(self, other):
        if non_string_sequence(other, Integral) and len(other) == 2:
            return self.l <= other[0] <= self.r and self.u <= other[1] <= self.d
        else:
            return NotImplemented
            
    @property
    def l(self): return self.corners[0]
    @property
    def u(self): return self.corners[1]
    @property
    def r(self): return self.corners[2]
    @property
    def d(self): return self.corners[3]
    @property
    def width(self): return self.r - self.l + 1
    @property
    def height(self): return self.d - self.u + 1
    @property
    def size(self): return (self.width, self.height)
    @property
    def center(self): return self.point(0.5)
            
    def point(self, align):
        """Return the point at a specific alignment."""
        align = Alignment(align)
        x = ceil(self.l + align.x * (self.r - self.l))
        y = ceil(self.u + align.y * (self.d - self.u))
        return (x, y)

    def pad(self, padding):
        """Return a padded bounding box."""
        padding = Padding(padding)
        return BoundingBox((self.l - padding.l, self.u - padding.u, self.r + padding.r, self.d + padding.d))
        
# RGBA and palettes
 
class RGBA(namedtuple('RGBA', ['red', 'green', 'blue', 'alpha'])):
    """Named tuple representing RGBA colors. Can be initialised by name, integer values, float values or hex strings."""
    def __new__(cls, *color, red=None, green=None, blue=None, alpha=None):
        if any([red, green, blue, alpha]):
            if color:
               raise ValueError("Invalid RGBA parameters: specify either positional or keyword arguments, not both")
            elif not all([red, green, blue]):
               raise ValueError("Invalid RGBA parameters: missing R/G/B value")
            color = [c for c in (red, green, blue, alpha) if c]
        rgba = color
        if len(rgba) == 1:
            if not rgba[0]:
                rgba = (0,0,0,0)
            elif isinstance(rgba[0], str) and rgba[0].startswith("#") and len(rgba[0]) in {7, 9}:
                rgba = [int("".join(rgba[0][i:i+2]), 16) for i in range(1, len(rgba[0]), 2)]
            elif isinstance(rgba[0], str):
                rgba = ImageColor.getrgb(rgba[0])
            elif isinstance(rgba[0], abc.Sequence) and 3 <= len(rgba[0]) <= 4:
                rgba = rgba[0]
        if all(isinstance(x, float) for x in rgba):
            rgba = [int(round(x*255)) for x in rgba]
        if len(rgba) == 3 and all(isinstance(x, Integral) and 0 <= x <= 255 for x in rgba):
            return super().__new__(cls, *rgba, 255)
        elif len(rgba) == 4 and all(isinstance(x, Integral) and 0 <= x <= 255 for x in rgba):
            return super().__new__(cls, *rgba)
        else:
            raise ValueError("Invalid RGBA parameters: {}".format(", ".join(map(repr, color))))

class NamedPalette(abc.Sequence):
    """Named color palettes. Behaves like a sequence, but also allows palette lookup by (case-insensitive) name."""
    
    def __init__(self, colors):
        self._colors_ = ValueMappingDict(colors, value_mapping=lambda d,k,v: raise_exception(KeyError("{} already present in named palette".format(k))) if k in d else RGBA(v), base_factory=partial(CaseInsensitiveDict, base_factory=OrderedDict))
        for c, v in self._colors_.items():
             setattr(self, c, v)
        
    def __iter__(self):
        return iter(self._colors_.values())
    def __len__(self):
        return len(self._colors_)
    def __getitem__(self, key):
        return self._colors_[key] if isinstance(key, str) else list(self._colors_.values())[key]
    def __getattr__(self, name):
        return self._colors_[name] if name in self._colors_ else raise_exception(AttributeError(name))
    @property
    def names(self):
        return list(self._colors_)
    def __repr__(self):
        return "NamedPalette[{}]".format(", ".join(self.names))

class NamedPaletteMeta(type):
    """Metaclass for defining named color palettes."""

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()
        
    def __new__(metacls, name, bases, classdict):
        colors = [(c, v) for c, v in classdict.items() if c not in dir(type(name, (object,), {})) and not c.startswith("_")]
        return NamedPalette(colors)

class VegaPalette10(metaclass=NamedPaletteMeta):
    BLUE = "#1f77b4"
    ORANGE = "#ff7f0e"
    GREEN = "#2ca02c"
    RED = "#d62728"
    PURPLE = "#9467bd"
    BROWN = "#8c564b"
    PINK = "#e377c2"
    GREY = "#7f7f7f"
    LIGHTGREEN = "#bcbd22"
    LIGHTBLUE = "#17becf"
 
class Set1Class9(metaclass=NamedPaletteMeta):
    RED = "#e41a1c"
    BLUE = "#377eb8"
    GREEN = "#4daf4a"
    PURPLE = "#984ea3"
    ORANGE = "#ff7f00"
    YELLOW = "#ffff33"
    BROWN = "#a65628"
    PINK = "#f781bf"
    GREY = "#999999"
    
class PairedClass12(metaclass=NamedPaletteMeta):
    LIGHTBLUE = "#a6cee3"
    BLUE = "#1f78b4"
    LIGHTGREEN = "#b2df8a"
    GREEN = "#33a02c"
    PINK = "#fb9a99"
    RED = "#e31a1c"
    LIGHTORANGE = "#fdbf6f"
    ORANGE = "#ff7f00"
    LIGHTPURPLE = "#cab2d6"
    PURPLE = "#6a3d9a"
    YELLOW = "#ffff99"
    BROWN = "#b15928"
    
# ImageDraw

def whitespace_span_tokenize(text):
    """Whitespace span tokenizer."""
    return ((m.start(), m.end()) for m in re.finditer(r'[^\s-]+[-]*', text))

def language_hyphenator(lang='en_EN'):
    """pyphen-based position hyphenator."""
    return pyphen.Pyphen(lang=lang).positions

class _ImageDraw():

    _emptyImage = Image.new("RGBA", (0,0))
    _emptyDraw = ImageDraw.Draw(_emptyImage)
    _textsize = _emptyDraw.textsize
    
    @classmethod
    def text_size(cls, text, font, beard_line=False, *args, **kwargs):
        """Return the size of a given string in pixels. Same as ImageDraw.Draw.textsize but doesn't
        require a drawable object, and handles descenders on multiline text and negative horizontal offsets.
        Setting beard_line makes the height include the beard line even if there are no descenders."""
        x, y = cls._textsize(text, font, *args, **kwargs)
        lines = text.split("\n")
        last_height = cls._textsize(lines[-1], font, *args, **kwargs)[1] 
        if len(lines) > 1: y += last_height - cls._textsize("A", font)[1]
        if beard_line: y += cls._textsize("y", font)[1] - last_height
        x += -min(0, min(font.getoffset(line)[0] for line in lines))
        return x, y 
        
    @classmethod
    def word_wrap(cls, text, font, max_width, tokenizer=whitespace_span_tokenize, hyphenator=None):
        """Returns a word-wrapped string from text that would fit inside the given max_width with
        the given font. Uses a span-based tokenizer and optional position-based hyphenator."""
        spans = list(tokenizer(text))
        line_start, line_end = 0, spans[0][0]
        output = text[line_start:line_end]
        hyphens = lambda s: ([] if hyphenator is None else hyphenator(s)) + [len(s)]
        for (tok_start, tok_end) in spans:
            if cls.text_size(text[line_start:tok_end], font)[0] < max_width:
                output += text[line_end:tok_end]
                line_end = tok_end
            else: 
                hyphen_start = tok_start
                for hyphen in hyphens(text[tok_start:tok_end]):
                    hopt = '' if text[tok_start+hyphen-1] == '-' else '-'
                    if cls.text_size(text[line_start:tok_start+hyphen]+hopt, font)[0] < max_width:
                        output += text[line_end:tok_start+hyphen] # no hyphen yet
                        line_end = tok_start+hyphen
                    else:
                        if line_end <= tok_start:
                            output += text[line_end:tok_start] if '\n' in text[line_end:tok_start] else '\n'
                            line_start = tok_start
                        else:
                            output += '\n' if text[line_end-1] == '-' else '-\n'
                            line_start = line_end
                        output += text[line_start:tok_start+hyphen]
                        line_end = tok_start+hyphen
        return output

ImageDraw.text_size = _ImageDraw.text_size
ImageDraw.word_wrap = _ImageDraw.word_wrap

# ImageColor

class _ImageColor():

    @classmethod
    def to_linear(cls, srgb):
        """Convert a /single/ sRGB color value between 0 and 255 to a linear value between 0 and 1. Numpy-aware."""
        c = srgb / 255
        return np.where(c <= 0.04045, c / 12.92, ((c+0.055)/1.055)**2.4)

    @classmethod
    def from_linear(cls, lrgb):
        """Convert a /single/ linear RGB value between 0 and 1 to an sRGB value between 0 and 255. Numpy-aware."""
        c = np.where(lrgb <= 0.0031308, 12.92 * lrgb, (1.055)*lrgb**(1/2.4)-0.055)
        return np.round(c * 255).astype(int)
        
    @classmethod
    def to_hex(cls, color, alpha=False):
        """Convert a color to a hex string."""
        return "#" + "".join("{:02x}".format(c) for c in RGBA(color)[:3+int(alpha)])
            
    @classmethod
    def blend(cls, color1, color2, p=0.5, linear_conversion=True):
        """Blend two colours with sRGB gamma correction."""
        color1, color2 = RGBA(color1), RGBA(color2)
        srgb_dims = 3 * int(linear_conversion)
        return RGBA(*[fl(tl(c1) + (tl(c2)-tl(c1))*p) for c1,c2,fl,tl in zip_longest(color1,color2,[cls.from_linear]*srgb_dims,[cls.to_linear]*srgb_dims,fillvalue=round)])

    @classmethod
    def brighten(cls, color, p, linear_conversion=True):
        """Brighten a color. Same as blending with white (but preserving alpha)."""
        color = RGBA(color)
        white = RGBA("white")._replace(alpha=color.alpha)
        return cls.blend(color, white, p, linear_conversion=linear_conversion)
            
    @classmethod
    def darken(cls, color, p, linear_conversion=True):
        """Darken a color. Same as blending with black (but preserving alpha)."""
        color = RGBA(color)
        white = RGBA("black")._replace(alpha=color.alpha)
        return cls.blend(color, white, p, linear_conversion=linear_conversion)
        
    @classmethod
    def alpha_composite(cls, bg, *fgs):
        """Alpha composite multiple colors."""
        if not fgs: return bg
        fg, *fgs = fgs
        c = RGBA(Rectangle(1, bg).place(Rectangle(1, fg)).getcolors()[0][-1])
        return cls.alpha_composite(c, *fgs)
            
    @classmethod
    def alpha_blend(cls, bg, *fgs, linear_conversion=True):
        """Alpha blend multiple colors. Like alpha_composite but sRGB-aware."""
        if not fgs: return bg
        fg, *fgs = fgs
        fg, bg = RGBA(fg), RGBA(bg)
        falpha, balpha = fg.alpha / 255, bg.alpha / 255
        srgb_dims = 3 * int(linear_conversion)
        alpha = falpha + balpha * (1 - falpha)
        rgb = [fl((tl(f)*falpha + tl(b)*balpha*(1-falpha))/alpha) if alpha>0 else 0
               for f,b,fl,tl in zip_longest(fg[:3],bg[:3],[cls.from_linear]*srgb_dims,[cls.to_linear]*srgb_dims,fillvalue=round) ]
        c = RGBA(*(rgb + [round(alpha*255)]))
        return cls.alpha_blend(c, *fgs, linear_conversion=linear_conversion)
            
ImageColor.to_linear = _ImageColor.to_linear
ImageColor.from_linear = _ImageColor.from_linear
ImageColor.to_hex = _ImageColor.to_hex
ImageColor.blend = _ImageColor.blend
ImageColor.brighten = _ImageColor.brighten
ImageColor.darken = _ImageColor.darken
ImageColor.alpha_composite = _ImageColor.alpha_composite
ImageColor.alpha_blend = _ImageColor.alpha_blend

RGBA.to_hex = papply(ImageColor.to_hex)
RGBA.blend = papply(ImageColor.blend)
RGBA.brighten = papply(ImageColor.brighten)
RGBA.darken = papply(ImageColor.darken)
RGBA.alpha_blend = papply(ImageColor.alpha_blend)

# Colormaps

class SequenceColormap():
    """A matplotlib colormap generated from a sequence of other colormaps and optional spacing intervals."""

    def __init__(self, *cmaps, intervals=None):
        if intervals is None: 
            intervals = [1] * len(cmaps)
        if len(intervals) != len(cmaps): 
            raise ValueError("Wrong number of colormap intervals: got {}, expected {}".format(len(intervals), len(cmaps)))
        if any(i <= 0 for i in intervals): 
            raise ValueError("Colormap intervals must be positive")
        self.cmaps = cmaps
        self.intervals = [x/sum(intervals) for x in intervals]
        self.accumulated = [0] + list(itertools.accumulate(self.intervals))
        
    def __repr__(self):
        return "SequenceColormap({})".format(", ".join("{:.0%}-{:.0%}={}".format(p, q, c) for p,q,c in zip(self.accumulated, self.accumulated[1:], self.cmaps)))
    
    def __call__(self, p, bytes=False):
        condlist = [p <= self.accumulated[i+1] for i in range(len(self.intervals))]
        choices = [np.array(self.cmaps[i]((p-self.accumulated[i])/self.intervals[i], bytes=bytes)) for i in range(len(self.intervals))]
        channel_choices = [[c[...,i] for c in choices] for i in range(4)]
        channel_cols = [np.select(condlist, choices) for choices in channel_choices]
        cols = np.stack(channel_cols, -1)
        return np.uint8(cols) if bytes else cols

class BlendColormap():
    """A matplotlib colormap generated from blending two colormaps."""
    
    def __init__(self, start, end, blend_fn=identity, linear_conversion=True):
        self.start = start
        self.end = end
        self.blend = blend_fn
        self.linear_conversion = linear_conversion
        
    def __repr__(self):
        return "BlendColormap({}-{})".format(self.start, self.end)
        
    def __call__(self, p, bytes=False):
        channels = zip_longest(np.rollaxis(np.array(self.start(p, bytes=True)), -1),
                               np.rollaxis(np.array(self.end(p, bytes=True)), -1),
                               [ImageColor.from_linear]*3*int(self.linear_conversion),
                               [ImageColor.to_linear]*3*int(self.linear_conversion),
                               fillvalue=lambda a: np.round(a).astype(int))
        cols = [fl(tl(cs)+(tl(ce)-tl(cs))*self.blend(p)) for cs,ce,fl,tl in channels]
        return np.uint8(np.stack(cols, -1)) if bytes else np.stack(cols, -1) / 255

class ConstantColormap():
    """A matplotlib colormap consisting of a single color."""
    
    def __init__(self, color):
        self.color = RGBA(color)
        
    def __repr__(self):
        return "ConstantColormap({})".format(self.color.to_hex(True))
        
    def __call__(self, p, bytes=False):
        cols = [np.full_like(p, c) for c in self.color]
        return np.uint8(np.stack(cols, -1)) if bytes else np.stack(cols, -1) / 255

class PaletteColormap():
    """A matplotlib colormap generated from constant colors and optional spacing intervals. Can also be used as a discrete cycling colormap."""
    
    def __init__(self, *colors, intervals=None):
        self.colors = tmap(RGBA, colors)
        self.cmap = SequenceColormap(*tmap(ConstantColormap, self.colors), intervals=intervals)
        
    def __repr__(self):
        return "PaletteColormap({})".format(", ".join("{:.0%}-{:.0%}={}".format(p, q, c.to_hex(True)) for p,q,c in zip(self.cmap.accumulated, self.cmap.accumulated[1:], self.colors)))
        
    def __call__(self, p, bytes=False):
        if isinstance(p, Integral) or getattr(getattr(p, 'dtype', None), 'kind', None) == 'i':
            cols = [np.select([np.mod(p, len(cs)) == i for i in range(len(cs))], cs) for cs in zip(*self.colors)]
            return np.uint8(np.stack(cols, -1)) if bytes else np.stack(cols, -1) / 255
        else:
            return self.cmap(p, bytes=bytes)
            
    def __getitem__(self, p): 
        if not isinstance(p, Integral):
            raise TypeError("Colormap index is not an integer. Did you mean application?")
        return RGBA(self(p, bytes=True))

class GradientColormap(SequenceColormap):
    """A matplotlib colormap generated from a sequence of colors and optional spacing intervals."""
    
    def __init__(self, *colors, intervals=None, linear_conversion=True):
        if len(colors) == 1: colors = colors * 2
        self.colors = tmap(RGBA, colors)
        gradients = [BlendColormap(ConstantColormap(c1), ConstantColormap(c2), linear_conversion=linear_conversion) 
                     for c1,c2 in zip(self.colors, self.colors[1:])]
        super().__init__(*gradients, intervals=intervals)
        
    def __repr__(self):
        return "GradientColormap({})".format(", ".join("{:.0%}={}".format(p, c.to_hex(True)) for p,c in zip(self.accumulated, self.colors)))

class FunctionColormap():
    """A matplotlib colormap generated from numpy-aware channel functions (either in RGBA or HSLA)."""
    
    def __init__(self, red_fn, green_fn, blue_fn, alpha_fn=np.ones_like, hsl=False):
        self.functions = [fn if callable(fn) else artial(np.full_like, fn) for fn in (red_fn, green_fn, blue_fn, alpha_fn)]
        self.hsl = hsl
        
    def __repr__(self):
        return "FunctionColormap({})".format(", ".join(fn.__name__ for fn in self.functions))
        
    def __call__(self, p, bytes=False):
        if self.hsl:
            h,s,l,a = [fn(p) for fn in self.functions]
            h_ = h * 6
            c = (1 - np.abs(2*l - 1)) * s
            x = c * (1 - np.abs(np.mod(h_, 2) - 1))
            m = l - c / 2
            h_conds = [h_ <= i+1 for i in range(6)]
            r = np.select(h_conds, [c,x,c*0,c*0,x,c]) + m
            g = np.select(h_conds, [x,c,c,x,c*0,c*0]) + m
            b = np.select(h_conds, [c*0,c*0,x,c,c,x]) + m
        else:
            r,g,b,a = [fn(p) for fn in self.functions]
        cols = np.stack([r,g,b,a], -1)
        return np.uint8(np.round(cols * 255)) if bytes else cols

# Image

class _Image(Image.Image):

    @classmethod
    def from_text(cls, text, font, fg="black", bg=None, padding=0, line_spacing=0, beard_line=False, align="left",
                  max_width=None, tokenizer=whitespace_span_tokenize, hyphenator=None, bidi_reshape=True):
        """Create image from text. If max_width is set, uses the tokenizer and optional hyphenator
        to split text across multiple lines."""
        padding = Padding(padding)
        if bidi_reshape:
            text = bidi_layout(arabic_reshape(text))
        if bg is None:
            bg = RGBA(fg)._replace(alpha=0)
        if max_width is not None:
            text = ImageDraw.word_wrap(text, font, max_width, tokenizer, hyphenator)
        w,h = ImageDraw.text_size(text, font, spacing=line_spacing, beard_line=beard_line)
        if max_width is not None and w > max_width:
            logger.warning("Text cropped as too wide to fit: {}".format(text))
            w = max_width
        img = Image.new("RGBA", (w + padding.x, h + padding.y), bg)
        draw = ImageDraw.Draw(img)
        draw.text((padding.l, padding.u), text, font=font, fill=fg, spacing=line_spacing, align=align)
        return img

    @classmethod
    def from_multitext(cls, texts, fonts, fgs="black", bgs=None, underlines=0, strikethroughs=0, img_offset=0, beard_line=False, bidi_reshape=True):
        """Create image from multiple texts, lining up the baselines. Only supports single-line texts.
        For multline texts, combine images with Image.from_column (with equal_heights set to True).
        The texts parameter can also include images, which are lined up to sit on the baseline+img_offset."""
        texts = make_iterable(texts)
        if not non_string_iterable(fonts): fonts = [fonts] * len(texts)
        if not non_string_iterable(fgs): fgs = [fgs] * len(texts)
        if not non_string_iterable(bgs): bgs = [bgs] * len(texts)
        if not non_string_iterable(underlines): underlines = [underlines] * len(texts)
        if not non_string_iterable(strikethroughs): strikethroughs = [strikethroughs] * len(texts)
        lengths = ( len(fonts), len(fgs), len(bgs), len(underlines), len(strikethroughs) )
        if not all(l == len(texts) for l in lengths):
            raise ValueError("Number of fonts, fgs, bgs, underlines or strikethroughs is inconsistent with number of texts: got {}, expected {}".format(lengths, len(texts)))
        bgs = [bg if bg is not None else RGBA(fg)._replace(alpha=0) for fg, bg in zip(fgs, bgs)]
        imgs = [cls.from_text(text, font, fg, bg, beard_line=beard_line, bidi_reshape=bidi_reshape) if isinstance(text, str) else text.remove_transparency(bg) for text, font, fg, bg in zip(texts, fonts, fgs, bgs)]
        ascents = [font.getmetrics()[0] if isinstance(text, str) else text.height+img_offset for text, font in zip(texts, fonts)]
        max_ascent = max(ascents)
        imgs = [img.pad((0,max_ascent-ascent,0,0), bg) for img, ascent, bg in zip(imgs, ascents, bgs)]
        max_height = max(img.height for img in imgs)
        imgs = [img.pad((0,0,0,max_height-img.height), bg) for img, bg in zip(imgs, bgs)]
        imgs = [img if not underline else img.overlay(Rectangle((img.width, underline), fg), (0, max_ascent)) for img, fg, underline in zip(imgs, fgs, underlines)]
        imgs = [img if not strikethrough else img.overlay(Rectangle((img.width, strikethrough), fg), (0, max_ascent - round(ascent*0.4))) for img, fg, ascent, strikethrough in zip(imgs, fgs, ascents, strikethroughs)]
        return Image.from_row(imgs)
        
    @classmethod
    def from_markup(cls, markup, font_family, fg="black", bg=None, highlight="#0645AD", overline_widths=(2,1), line_spacing=0, align="left",
                    max_width=None, tokenizer=whitespace_span_tokenize, hyphenator=None, padding=0, beard_line=False, bidi_reshape=True):
        """Create image from simle markup. See MarkupExpression for details. Max width uses normal font to split text so is not precise."""
        if isinstance(overline_widths, Integral):
            overline_widths = (overline_widths, overline_widths)
        if bidi_reshape:
            markup = bidi_layout(arabic_reshape(markup))
        mexpr = MarkupExpression(markup)
        if max_width is not None:
            text = ImageDraw.word_wrap(mexpr.get_text(), font_family(), max_width, tokenizer, hyphenator)
            mexpr.reparse_wrapped_text(text)
        rows = []
        for line in mexpr.get_parsed():
            texts = [s for s,m in line]
            fonts = [font_family(bold=("b" in m), italics=("i" in m)) for s,m in line]
            fgs = [highlight if "c" in m else fg for s,m in line]
            underlines = [overline_widths[0] if "u" in m else 0 for s,m in line]
            strikethroughs = [overline_widths[1] if "s" in m else 0 for s,m in line]
            rows.append(cls.from_multitext(texts, fonts, fgs, bg, underlines=underlines, strikethroughs=strikethroughs, beard_line=beard_line, bidi_reshape=False))
        return Image.from_column(rows, yalign=0, equal_heights=True, bg=bg, xalign=["left","center","right"].index(align)/2).pad(padding, bg)
        
    @classmethod
    def from_pattern(cls, pattern, size, align=0, scale=(False,False), preserve_aspect=False, resample=Image.LANCZOS):
        """Create an image using a background pattern, either scaled or tiled."""
        align = Alignment(align)
        img = Image.new("RGBA", size)
        if size[0] * size[1] == 0: return img
        if preserve_aspect:
            if scale[0] and scale[1]: raise ValueError("Cannot preserve aspect when scaling in both dimensions.")
            elif scale[0]: pattern = pattern.resize_fixed_aspect(width=size[0], resample=resample)
            elif scale[1]: pattern = pattern.resize_fixed_aspect(height=size[1], resample=resample)
        else:
            if scale[0]: pattern = pattern.resize((size[0], pattern.height), resample=resample)
            if scale[1]: pattern = pattern.resize((pattern.width, size[1]), resample=resample)
        xover = (pattern.width - size[0] % pattern.width) % pattern.width
        yover = (pattern.height - size[1] % pattern.height) % pattern.height
        for i in range(ceil(size[0] / pattern.width)):
            for j in range(ceil(size[1] / pattern.height)):
                x = int(i*pattern.width-xover*align.x)
                y = int(j*pattern.height-yover*align.y)
                img.overlay(pattern, (x,y))
        return img
        
    @classmethod
    def from_vertical_pattern(cls, pattern, size, **kwargs):
        """Create an image using a background pattern, scaled to the image width."""
        return cls.from_pattern(pattern, size, scale=(True,False), preserve_aspect=True, **kwargs)
        
    @classmethod
    def from_horizontal_pattern(cls, pattern, size, **kwargs):
        """Create an image using a background pattern, scaled to the image height."""
        return cls.from_pattern(pattern, size, scale=(False,True), preserve_aspect=True, **kwargs)
        
    @classmethod
    def from_gradient(cls, colormap, size, direction=(1,0)):
        """Create a gradient image using a matplotlib color map. Requires numpy."""
        size = list(reversed(size)) # numpy ordering
        valmin = min((x * direction[0] + y * direction[1]) for x in (0, size[1]-1) for y in (0, size[0]-1))
        valrange = max((x * direction[0] + y * direction[1]) for x in (0, size[1]-1) for y in (0, size[0]-1)) - valmin
        grad_array = np.fromfunction(lambda y, x: ((x * direction[0] + y * direction[1]) - valmin) / valrange, size, dtype=float)
        return Image.fromarray(colormap(grad_array, bytes=True))
        
    @classmethod
    def from_array(cls, array, xalign=0.5, yalign=0.5, equal_heights=False, equal_widths=False, padding=0, bg=0):
        """Create an image from an array of images."""
        if not non_string_iterable(xalign): xalign = [xalign] * max(len(r) for r in array)
        if not non_string_iterable(yalign): yalign = [yalign] * len(array)
        align = [[Alignment((xalign[c], yalign[r])) for c,_ in enumerate(row)] for r,row in enumerate(array)]
        padding = Padding(padding)
        heights = [max(img.height if img is not None else 0 for img in row) + padding.y for row in array]
        widths = [max(img.width if img is not None else 0 for img in column) + padding.x for column in zip_longest(*array)]
        if equal_heights: heights = [max(heights)] * len(heights)
        if equal_widths: widths = [max(widths)] * len(widths)
        aimg = Image.new("RGBA", (sum(widths), sum(heights)), bg)
        for r,row in enumerate(array):
            for c,img in enumerate(row):
                if img is None: continue
                x = sum(widths[0:c]) + padding.l + int(align[r][c].x * (widths[c] - (img.width + padding.x)))
                y = sum(heights[0:r]) + padding.u + int(align[r][c].y * (heights[r] - (img.height + padding.y)))
                aimg.overlay(img, (x,y))
        return aimg
        
    @classmethod
    def from_row(cls, row, **kwargs):
        """Create an image from a row of images. See Image.from_array for passthrough parameters."""
        return cls.from_array([row], **kwargs)
        
    @classmethod
    def from_column(cls, column, **kwargs):
        """Create an image from a column of images. See Image.from_array for passthrough parameters."""
        return cls.from_array([[img] for img in column], **kwargs)
    
    @classmethod
    def from_url(cls, url, filepath=None):
        """Create an image from a url, optionally saving it to a filepath."""
        HEADERS = {'User-Agent': 'Mozilla/5.0'}
        uparse = urlparse(url)
        logger.debug("Reading image from {}".format(url))
        if uparse.scheme == '':
            with open(url, 'rb') as f:
                content = f.read()
        else:
            content = requests.get(url, headers=HEADERS).content if requests else urlopen(url).read()
        if filepath is None:
            fh = BytesIO(content)
            return Image.open(fh)
        else:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            logger.debug("Saving image to {}".format(filepath))
            with open(filepath, 'wb') as f:
                f.write(content)
            with open(filepath + ".source", "w", encoding="utf-8") as f:
                print(url, file=f)
            return Image.open(filepath)

    @classmethod
    def from_url_with_cache(cls, url, cache_dir='cache', filename=None):
        """Create an image from a url, using a file cache."""
        filepath = os.path.join(cache_dir, filename or url_to_filepath(url))
        if os.path.isfile(filepath):
            logger.debug("Loading cached image at {}".format(filepath))
            img = Image.open(filepath)
        else:
            img = cls.from_url(url, filepath)
        return img
        
    @classmethod
    def generate_bounded(cls, box_size, parameters, generator):
        """Return the first parametrised image that fits within the box_size."""
        return first(img for p in parameters for img in [generator(p)] if img.width <= box_size[0] and img.height <= box_size[1])
        
    @classmethod
    def from_text_bounded(cls, text, box_size, max_font_size, font_fn, *args, min_font_size=6, **kwargs):
        """Create image from text, reducing the font size until it fits. Inefficient."""
        return cls.generate_bounded(box_size, range(max_font_size, min_font_size-1, -1), lambda size: cls.from_text(text, font_fn(size), *args, **kwargs))
        
    @classmethod
    def from_markup_bounded(cls, text, box_size, max_font_size, font_fn, *args, min_font_size=6, **kwargs):
        """Create image from markup, reducing the font size until it fits. Inefficient."""
        return cls.generate_bounded(box_size, range(max_font_size, min_font_size-1, -1), lambda size: cls.from_markup(text, font_fn(size), *args, **kwargs))

    @classmethod
    def from_text_justified(cls, text, width, max_font_size, font_fn, *args, bg=None, padding=0, line_spacing=0, **kwargs):
        """Create image from multiple lines of text, fitting each line in the given width. Inefficient."""
        return cls.from_column([cls.from_text_bounded(line, (width, max_font_size * 10), max_font_size, font_fn, *args, bg=bg, **kwargs) for line in text.split("\n")],
                               bg=bg, padding=line_spacing).pad(padding, bg=bg)
    
    def to_rgba(self):
        """Return an RGBA copy of the image (or leave unchanged if it already is)."""
        return self if self.mode == "RGBA" else self.convert("RGBA")
        
    def to_palette(self, palette, dither=False):
        """Return a P-mode copy of the image with a given palette."""
        rgb_img = self.convert("RGB")
        pal_img = Image.new("P", self.size, 0)
        pal = list(generate_leafs(RGBA(col)[:3] for col in list(palette) + [palette[0]]*(256-len(palette))))
        pal_img.putpalette(pal)
        return rgb_img._new(rgb_img.im.convert("P", int(dither), pal_img.im))
        
    def overlay(self, img, box=(0,0), mask=None, copy=False):
        """Paste an image using alpha compositing (unlike Image.paste)."""
        if img.mode.endswith('A'):
            if len(box) == 2: box = (box[0], box[1], min(self.width, box[0]+img.width), min(self.height, box[1]+img.height))
            img = Image.alpha_composite(self.crop(box).to_rgba(), img.crop((0, 0, box[2]-box[0], box[3]-box[1])))
        base = self.copy() if copy else self
        base.paste(img, box, mask)
        return base
        
    def place(self, img, align=0.5, padding=0, mask=None, copy=True):
        """Overlay an image using the given alignment and padding."""
        align, padding = Alignment(align), Padding(padding)
        x = int(padding.l + align.x * (self.width - (img.width + padding.x)))
        y = int(padding.u + align.y * (self.height - (img.height + padding.y)))
        return self.overlay(img, (x, y), mask=mask, copy=copy)
        
    def pad(self, padding, bg, offsets=None):
        """Return a padded image. Updates optional offset structure."""
        padding = Padding(padding)
        if offsets is not None: offsets.update(offsets + padding)
        if padding.x == padding.y == 0: return self
        img = Image.new(self.mode, (self.width + padding.x, self.height + padding.y), bg)
        img.paste(self, (padding.l, padding.u))
        return img
        
    def trim(self, padding):
        """Return a cropped image."""
        padding = Padding(padding)
        if padding.x == padding.y == 0: return self
        return self.crop((padding.l, padding.u, self.width-padding.r, self.height-padding.d))
        
    def pin(self, img, position, align=0.5, bg=(0,0,0,0), offsets=None):
        """Pin an image onto another image, copying and if necessary expanding it. Uses and updates optional offset structure."""
        align = Alignment(align)
        if offsets is None: offsets = Padding(0)
        x = offsets.l + int(position[0] - align.x * img.width)
        y = offsets.u + int(position[1] - align.y * img.height)
        padded = self.pad((max(0, -x), max(0, -y), max(0, x+img.width-self.width), max(0, y+img.height-self.height)), bg=bg, offsets=offsets)
        return padded.overlay(img, (max(0, x), max(0, y)))
        
    def crop_to_aspect(self, aspect, divisor=1, align=0.5):
        """Return a cropped image with the given aspect ratio."""
        align = Alignment(align)
        if self.width * divisor > self.height * aspect:
            newwidth = int(self.height * (aspect / divisor))
            newheight = self.height
        else:
            newwidth = self.width
            newheight = int(self.width * (divisor / aspect))
        img = self.crop((align.x * (self.width - newwidth),
                         align.y * (self.height - newheight),
                         align.x * (self.width - newwidth) + newwidth,
                         align.y * (self.height - newheight) + newheight))
        return img

    def pad_to_aspect(self, aspect, divisor=1, align=0.5, bg="black", offsets=None):
        """Return a padded image with the given aspect ratio. Updates optional offset structure."""
        if aspect == self.width == 0 or divisor == self.height == 0:
            return self
        align = Alignment(align)
        if self.width * divisor > self.height * aspect:
            newwidth = self.width
            newheight = int(self.width * (divisor / aspect))
        else:
            newwidth = int(self.height * (aspect / divisor))
            newheight = self.height
        img = Image.new("RGBA", (newwidth, newheight), bg)
        x = int(align.x * (newwidth - self.width))
        y = int(align.y * (newheight - self.height))
        if offsets is not None:
            padding = Padding((x, y, img.width-self.width-x, img.height-self.height-y))
            offsets.update(offsets + padding)
        return img.overlay(self, (x, y), None)

    def resize(self, size, resample=Image.LANCZOS, *args, **kwargs):
        """Return a resized copy of the image, handling zero-width/height sizes and defaulting to LANCZOS resampling."""
        if size[0] == 0 or size[1] == 0:
            return Image.new(self.mode, size)
        else:
            return self.resize_nonempty(size, resample, *args, **kwargs)
        
    def resize_fixed_aspect(self, *, width=None, height=None, scale=None, resample=Image.LANCZOS):
        """Return a resized image with an unchanged aspect ratio."""
        if all(x is None for x in (width, height, scale)):
            raise ValueError("Resize expects either width/height or scale.")
        elif any(x is not None for x in (width, height)) and scale is not None:
            raise ValueError("Resize expects just one of width/height or scale.")
        elif scale is not None:
            return self.resize((int(self.width * scale), int(self.height * scale)), resample=resample)
        elif height is None or width is not None and self.width / self.height > width / height:
            return self.resize((width, int(width * (self.height / self.width))), resample=resample)
        else:
            return self.resize((int(height * (self.width / self.height)), height), resample=resample)

    def cropped_resize(self, size, align=0.5, upsize=True, pad_up=False, pad_align=0.5, pad_bg="black", **kwargs):
        """Return a resized image, after first cropping it to the right aspect ratio. 
        If upsize is False then avoid upscaling images that are too small. If pad_up is True
        then pad those instead."""
        if not upsize and not pad_up and (self.width < size[0] or self.height < size[1]):
            return self.crop_to_aspect(min(self.width, size[0]), min(self.height, size[1]), align)
        if not upsize and pad_up and (self.width < size[0] or self.height < size[1]):
            self = Image.new("RGBA", (max(self.width, size[0]), max(self.height, size[1])), pad_bg).place(self, align=pad_align)
        return self.crop_to_aspect(size[0], size[1], align).resize(size, **kwargs)
        
    def padded_resize(self, size, align=0.5, bg="black", no_pad_ratio=1, **kwargs):
        """Return a resized image, after first padding it to the right aspect ratio.
        Images whose aspect ratio is less than a factor of no_pad_ratio away from the target ratio
        are not padded, just resized."""
        ratio = (self.width / self.height) / (size[0] / size[1])
        if max(ratio, 1 / ratio) > no_pad_ratio:
            self = self.pad_to_aspect(size[0], size[1], align, bg)
        return self.resize(size, **kwargs)
    
    def select_color(self, color, ignore_alpha=False):
        """Return a transparency mask selecting a color in an image. Requires numpy."""
        if 'RGB' not in self.mode:
            raise NotImplementedError("select_color expects RGB/RGBA image")
        n = 3 if (self.mode == 'RGB' or ignore_alpha) else 4
        color = RGBA(color)[:n]
        data = np.array(self)
        mask = _nparray_mask_by_color(data, color, n)
        return Image.fromarray(mask.astype('uint8') * 255).convert("1")
        
    def replace_colors(self, mapping, ignore_alpha=False):
        """Return an image with the colors specified by the mapping keys replaced by the colors
        or patterns specified by the mapping values. Requires numpy."""
        if 'RGB' not in self.mode:
            raise NotImplementedError("replace_colors expects RGB/RGBA image")
        n = 3 if (self.mode == 'RGB' or ignore_alpha) else 4
        original = np.array(self)
        output = self.copy()
        for c1, c2 in mapping.items():
            color1 = RGBA(c1)[:n]
            mask = _nparray_mask_by_color(original, color1, n)
            if isinstance(c2, Image.Image):
                mask = Image.fromarray(mask.astype('uint8') * 255).convert("1")
                pattern = Image.from_pattern(c2, self.size)
                if ignore_alpha and "A" in self.mode:
                    pattern.putalpha(self.getchannel(3))
                output.paste(pattern, (0, 0), mask)
            else:
                color2 = RGBA(c2)[:n]
                data = np.array(output)
                data[:,:,:n][mask] = color2
                output = Image.fromarray(data.astype('uint8'))
        return output
                
    def replace_color(self, color, to, ignore_alpha=False):
        """Return an image with a color replace by a color or pattern. Requires numpy."""
        return self.replace_colors({ color: to }, ignore_alpha=ignore_alpha)

    def remove_transparency(self, bg="white"):
        """Return an image with the transparency removed"""
        if not self.mode.endswith('A'): return self
        elif bg is None: return self.convert("RGB").convert("RGBA")
        else: return Image.new("RGBA", self.size, RGBA(bg)).overlay(self)
        
    def as_mask(self):
        """Convert image for use as a mask"""
        if self.mode in ["1", "L"]: return self.convert("L")
        elif "A" in self.mode: return self.split()[-1].convert("L")
        else: raise TypeError("Image with mode {} cannot be used as mask".format(self.mode))
        
    def invert_mask(self):
        """Invert image for use as a mask"""
        return ImageOps.invert(self.as_mask())
        
    def blend(self, img, p=0.5, linear_conversion=True):
        """Blend two images with sRGB gamma correction. Requires numpy."""
        if self.size != img.size or self.mode != img.mode: raise NotImplementedError
        arrays1 = [np.array(a) for a in self.split()]
        arrays2 = [np.array(a) for a in img.split()]
        dims = int(linear_conversion)* (len(arrays1) - int("A" in self.mode))
        blended = [fl(tl(c1) + (tl(c2)-tl(c1))*p) for c1,c2,fl,tl in zip_longest(arrays1,arrays2,[ImageColor.from_linear]*dims,[ImageColor.to_linear]*dims,fillvalue=lambda a: np.round(a).astype(int))]
        return Image.fromarray(np.uint8(np.stack(blended, axis=-1)))
        
    def brighten(self, p, linear_conversion=True):
        """Brighten an image. Same as blending with white (but preserving alpha)."""
        other = Image.new(self.mode, self.size, "white")
        if 'A' in self.mode: other.putalpha(self.split()[-1])
        return self.blend(other, p, linear_conversion=linear_conversion)

    def darken(self, p, linear_conversion=True):
        """Darken an image. Same as blending with black (but preserving alpha)."""
        other = Image.new(self.mode, self.size, "black")
        if 'A' in self.mode: other.putalpha(self.split()[-1])
        return self.blend(other, p, linear_conversion=linear_conversion)

    def alpha_blend(self, *fgs, linear_conversion=True):
        """Alpha blend images onto this image. Like alpha_composite but sRGB aware (and a fair bit slower)."""
        if not fgs: return self
        fg, *fgs = fgs
        if self.size != fg.size or self.mode != fg.mode or self.mode != "RGBA": raise NotImplementedError
        fg_arrays = [np.array(a) for a in fg.split()]
        bg_arrays = [np.array(a) for a in self.split()]
        falpha, balpha = fg_arrays[-1] / 255, bg_arrays[-1] / 255
        srgb_dims = 3 * int(linear_conversion)
        alpha = falpha + balpha * (1 - falpha)
        rgb = [np.where(alpha>0, fl((tl(f)*falpha + tl(b)*balpha*(1-falpha))/alpha), 0)
               for f,b,fl,tl in zip_longest(fg_arrays[:3],bg_arrays[:3],[ImageColor.from_linear]*srgb_dims,[ImageColor.to_linear]*srgb_dims,fillvalue=lambda a: np.round(a).astype(int))]
        img = Image.fromarray(np.uint8(np.stack(rgb + [alpha], axis=-1)))
        return img.alpha_blend(*fgs, linear_conversion=linear_conversion)
        
    def to_heatmap(self, colormap):
        """Create a heatmap image from a mask using a matplotlib color map. Mask is either a mode L image or the image's alpha channel. Requires numpy."""
        array = np.array(self.as_mask()) / 255
        return Image.fromarray(colormap(array, bytes=True))
        
    def add_grid(self, lines, width=1, bg="black", copy=True):
        """Add grid lines to an image"""
        if isinstance(lines, Integral): lines = (lines, lines)
        base = self.copy() if copy else self
        draw = ImageDraw.Draw(base)
        for x in range(lines[0] and lines[0]+1):
            draw.line([((base.width-1) * x // lines[0], 0), ((base.width-1) * x // lines[0], base.height)], fill=bg, width=width)
        for y in range(lines[1] and lines[1]+1):
            draw.line([(0, (base.height-1) * y // lines[1]), (base.width, (base.height-1) * y // lines[1])], fill=bg, width=width)
        return base
        
    def add_shadow(self, color="black", blur=2, offset=(0,0), resize=True, shadow_only=False):
        """Add a drop shadow to an image"""
        if not self.mode.endswith('A'): return self
        shadow = Image.from_pattern(color, self.size) if isinstance(color, Image.Image) else Image.new("RGBA", self.size, color)
        shadow.putalpha(ImageChops.multiply(self.split()[-1], shadow.split()[-1]))
        shadow = shadow.pad(blur, 0)
        if blur: shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        offsets = Padding(0)
        img = Image.new("RGBA", self.size, 0)
        img = img.pin(shadow, (offset[0]-blur,offset[1]-blur), align=0, offsets=offsets)
        if not shadow_only: img = img.pin(self, (0,0), align=0, offsets=offsets)
        if not resize: img = img.crop((offsets[0], offsets[1], img.width-offsets[2], img.height-offsets[3]))
        return img

def _nparray_mask_by_color(nparray, color, num_channels=None):
    if len(nparray.shape) != 3: raise NotImplementedError
    n = nparray.shape[-1] if num_channels is None else num_channels
    channels = [nparray[...,i] for i in range(n)]
    mask = np.ones(nparray.shape[:-1], dtype=bool)
    for c,channel in zip(color, channels):
        mask = mask & (channel == c)
    return mask

Image.from_text = _Image.from_text
Image.from_multitext = _Image.from_multitext
Image.from_markup = _Image.from_markup
Image.from_array = _Image.from_array
Image.from_row = _Image.from_row
Image.from_column = _Image.from_column
Image.from_pattern = _Image.from_pattern
Image.from_gradient = _Image.from_gradient
Image.from_vertical_pattern = _Image.from_vertical_pattern
Image.from_horizontal_pattern = _Image.from_horizontal_pattern
Image.from_url = _Image.from_url
Image.from_url_with_cache = _Image.from_url_with_cache
Image.generate_bounded = _Image.generate_bounded
Image.from_text_bounded = _Image.from_text_bounded
Image.from_markup_bounded = _Image.from_markup_bounded
Image.from_text_justified = _Image.from_text_justified
Image.EMPTY_IMAGE = Image.new("RGBA", (0,0))

Image.Image.to_rgba = _Image.to_rgba
Image.Image.to_palette = _Image.to_palette
Image.Image.overlay = _Image.overlay
Image.Image.place = _Image.place
Image.Image.pad = _Image.pad
Image.Image.trim = _Image.trim
Image.Image.pin = _Image.pin
Image.Image.crop_to_aspect = _Image.crop_to_aspect
Image.Image.cropped_resize = _Image.cropped_resize
Image.Image.pad_to_aspect = _Image.pad_to_aspect
Image.Image.padded_resize = _Image.padded_resize
if not hasattr(Image.Image, 'resize_nonempty'):
    Image.Image.resize_nonempty=Image.Image.resize
Image.Image.resize = _Image.resize
Image.Image.resize_fixed_aspect = _Image.resize_fixed_aspect
Image.Image.select_color = _Image.select_color
Image.Image.replace_color = _Image.replace_color
Image.Image.replace_colors = _Image.replace_colors
Image.Image.remove_transparency = _Image.remove_transparency
Image.Image.as_mask = _Image.as_mask
Image.Image.invert_mask = _Image.invert_mask
Image.Image.blend = _Image.blend
Image.Image.brighten = _Image.brighten
Image.Image.darken = _Image.darken
Image.Image.alpha_blend = _Image.alpha_blend
Image.Image.to_heatmap = _Image.to_heatmap
Image.Image.add_grid = _Image.add_grid
Image.Image.add_shadow = _Image.add_shadow

# Fonts

def font(name, size, bold=False, italics=False, **kwargs):
    """Return a truetype font object. Name is either a sequence of 4 names representing
    normal, italics, bold and bold-italics variants, or just a single name (in which the
    suffixes i, b/bd and z/bi are added for the variants)."""
    SUFFIXES = [["","i","bd","bi"],
                ["", "i", "b", "z"],
                ["","Oblique","Bold","BoldOblique"],
                ["","_Oblique","_Bold","_BoldOblique"]]
    variants = [name] if non_string_sequence(name) else [[name+suffix for suffix in suffixes] for suffixes in SUFFIXES]
    names = [list(generate_batches(variants, 2))[bold][italics] for variants in variants]
    for name in names:
        try:
            return ImageFont.truetype("{}.ttf".format(name), size, **kwargs)
        except OSError:
            continue
    raise OSError("Could not find TTF font: tried {}".format(", ".join(sorted(set("{}.ttf".format(n) for n in names)))))

def font_family(*names):
    """Return a font function supporting optional bold and italics parameters."""
    for name in names:
        try:
            family = partial(font, name)
            family(16)
            return family
        except OSError:
            continue
    return None

arial = font_family("arial")
calibri = font_family("calibri")
verdana = font_family("verdana")
sans = font_family("arial", "/usr/share/fonts/truetype/freefont/FreeSans")

# Shapes

class ImageShape(object):
    """Abstract base class for generating simple geometric shapes."""
    __metaclass__ = ABC.ABCMeta
    
    @classmethod
    @ABC.abstractmethod
    def mask(cls, size, **kwargs):
        """Generate a mask of the appropriate shape and size. Unless cls.antialising is set to False,
        this may be called at a higher size and scaled down. Additional parameters should therefore
        either be size-independent or scale according to the optional _scale parameter."""
        
    antialiasing = True
    
    def __new__(cls, size, fg="black", bg=None, antialias=4, invert=False, **kwargs):
        """Generate an image of the appropriate shape. See mask method for additional shape-specific parameters.
        - size (int/(int,int)): image size
        - fg (color/pattern): image foreground [black]
        - bg (color/pattern): image background [None]
        - antialias (x>0): level of antialiasing (if supported), where 1.0 is none [4.0]
        - invert (boolean): whether to invert the shape mask [False]
        """
        if isinstance(size, Integral): size = (size, size)
        if bg is None and not isinstance(fg, Image.Image) and not callable(fg):
            bg = RGBA(fg)._replace(alpha=0)
        if cls.antialiasing:
            orig_size, size = size, [round(s * antialias) for s in size]
            if isinstance(bg, Image.Image): bg = bg.resize([round(s * antialias) for s in bg.size], Image.NEAREST)
            if isinstance(fg, Image.Image): fg = fg.resize([round(s * antialias) for s in fg.size], Image.NEAREST)
        if "_scale" in names_of_keyword_args(cls.mask): kwargs = merge_dicts({"_scale": antialias}, kwargs)
        mask = cls.mask(size, **kwargs)
        if invert: mask = mask.invert_mask()
        if callable(fg):
            img = mask.to_heatmap(fg)
        else:
            base = Image.from_pattern(bg, mask.size) if isinstance(bg, Image.Image) else Image.new("RGBA", mask.size, bg)
            fore = Image.from_pattern(fg, mask.size) if isinstance(fg, Image.Image) else  Image.new("RGBA", mask.size, fg)
            img = base.overlay(fore, mask=mask)
        if cls.antialiasing:
            img = img.resize(orig_size, resample=Image.LANCZOS if antialias > 1 else Image.NEAREST)
        return img
        
class Rectangle(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, round=0, _scale=1):
        """Rectangular mask with optional rounded corners."""
        m = Image.new("L", size, 255)
        if not non_string_sequence(round): round = (round, round)
        if all(r > 0 for r in round):
            w = int(round[0] * size[0] / 2) if isinstance(round[0], float) else int(round[0] * _scale)
            h = int(round[1] * size[1] / 2) if isinstance(round[1], float) else int(round[1] * _scale)
            m.place(Quadrant.mask((w,h)), align=(0,0), copy=False)
            m.place(Quadrant.mask((w,h)).transpose(Image.FLIP_LEFT_RIGHT), align=(1,0), copy=False)
            m.place(Quadrant.mask((w,h)).transpose(Image.FLIP_TOP_BOTTOM), align=(0,1), copy=False)
            m.place(Quadrant.mask((w,h)).transpose(Image.ROTATE_180), align=(1,1), copy=False)
        return m
    
class Ellipse(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size):
        """Elliptical mask."""
        w, h = size
        rx, ry = (w-1)/2, (h-1)/2
        array = np.fromfunction(lambda j, i: ((rx-i)**2/rx**2+(ry-j)**2/ry**2 <= 1), (h,w))
        return Image.fromarray(255 * array.view('uint8'))

class Quadrant(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size):
        """Top-left quadrant mask."""
        m = Ellipse.mask((max(0,size[0]*2-1),max(size[1]*2-1,0))).crop((0,0,size[0],size[1]))
        return m

class Triangle(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, p=0.5, _scale=1.):
        """Triangular mask with 2 vertices at the bottom and one on top, with p > 0 
        for how far along the top the top vertex is, or p < 0 for how far along
        the bottom the bottom-left vertex is."""
        w, h = size
        x, y, n = w-1, h-1, (abs(p*(w-1)) if isinstance(p, float) else p*_scale)
        if p >= 0:
            left = np.fromfunction(lambda j,i: j*n >= y*(n-i), (h,w))
            right = np.fromfunction(lambda j,i: j*(x-n) >= y*(i-n), (h,w))
        else:
            left = np.fromfunction(lambda j,i: (y-j)*n >= y*(n-i), (h,w))
            right = np.fromfunction(lambda j,i: j*x >= y*i, (h,w))
        return Image.fromarray(255 * (left * right).view('uint8'))
        
class Parallelogram(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, p=0.5, _scale=1.):
        """Parallelogram-shaped mask, with p > 0 for how far along the top the top-left vertex is,
        or p < 0 for how far along the bottom the bottom-left vertex is."""
        w, h = size
        x, y, n = w-1, h-1, (abs(p*(w-1)) if isinstance(p, float) else p*_scale)
        left = np.fromfunction(lambda j,i: (j if p > 0 else y-j)*n >= y*(n-i), (h,w))
        right = np.fromfunction(lambda j,i: (j if p < 0 else y-j)*n >= y*(i-(x-n)), (h,w))
        return Image.fromarray(255 * (left * right).view('uint8'))

class Diamond(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, p=0.5, _scale=1.):
        """Diamond-shaped mask with the left-right vertices p down from the top."""
        w, h = size
        x, y, m, n = w-1, h-1, (w-1)/2, (abs(p*(h-1)) if isinstance(p, float) else p*_scale)
        top = np.fromfunction(lambda j, i: j*m >= n*abs(m-i), (h,w))
        bottom = np.fromfunction(lambda j, i: (y-j)*m >= (y-n)*abs(m-i), (h,w))
        return Image.fromarray(255 * (top * bottom).view('uint8'))
        
class Trapezoid(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, p=0.5, _scale=1.):
        """Trapezoid-shaped mask, for p > 0 for how close to the center the top vertices
        are, or p < 0 for how close to the center the bottom vertices are."""
        w, h = size
        x, y, n = w-1, h-1, (abs(p*(w-1)/2) if isinstance(p, float) else p*_scale)
        if p >= 0:
            left = np.fromfunction(lambda j,i: j*n >= y*(n-i), (h,w))
            right = np.fromfunction(lambda j,i: j*n >= y*(n-(x-i)), (h,w))
        else:
            left = np.fromfunction(lambda j,i: (y-j)*n >= y*(n-i), (h,w))
            right = np.fromfunction(lambda j,i: (y-j)*n >= y*(n-(x-i)), (h,w))
        return Image.fromarray(255 * (left * right).view('uint8'))

class Stripe(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, intervals=2):
        """Tilable diagonal stripe mask occupying p of the tile."""
        if isinstance(intervals, Integral): intervals = [1] * intervals
        if len(intervals) == 1: return Rectangle.mask(size)
        intervals = [x/sum(intervals) for x in intervals]
        accumulated = list(itertools.accumulate(intervals))
        w, h = size
        x, y = w-1, h-1
        horizontal_p = np.fromfunction(lambda j,i: np.mod(i/x + j/y, 1), (h,w))
        condlist = [ horizontal_p <= p for p in accumulated ]
        choices = [ np.full_like(horizontal_p, i) for i in range(len(accumulated)) ]
        pattern = np.select(condlist, choices)
        return Image.fromarray(np.round(255 * pattern / (len(accumulated)-1)).astype('uint8'))
        
class Checkers(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, shape=2, colors=2):
        """Checker grid pattern. Shape can be an integer or a pair."""
        if colors == 1: return Rectangle.mask(size)
        if isinstance(shape, Integral): shape=(shape,shape)
        m, n = shape
        w, h = size
        pattern = np.fromfunction(lambda j,i: ((i//(w/m) + j//(h/n)) % colors), (h,w))
        return Image.fromarray(np.round(255 * pattern / (colors-1)).astype('uint8'))
    antialiasing = False

class MaskUnion(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, masks):
        """A union of superimposed masks. Size is automatically calculated if set to ..."""
        masks = make_iterable(masks)
        if size == ...:
            size = (max((m.width for m in masks), default=0), max((m.height for m in masks), default=0))
        img = Image.new("L", size, 0)
        for m in masks:
            img = img.place(Image.new("L", m.size, 255), mask=m)
        return img
    antialiasing = False
        
class MaskIntersection(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, masks, include_missing=False):
        """An intersection of superimposed masks. Size is automatically calculated if set to ..."""
        masks = make_iterable(masks)
        if size == ...:
            size = (max(m.width for m in masks), max(m.height for m in masks))
        img = Image.new("L", size, 255)
        for m in masks:
            mask = Image.new("L", size, 255 if include_missing else 0).place(m.as_mask())
            img = img.place(Image.new("L", size, 0), mask=mask.invert_mask())
        return img
    antialiasing = False

class MaskBorder(ImageShape):
    __doc__ = ImageShape.__new__.__doc__
    @classmethod
    def mask(cls, size, mask, width):
        """Edge border of a given mask. Requires scipy. Size is automatically calculated if set to ..."""
        w = width / 2
        if size == ...: size = tmap(lambda x: ceil(x+w), mask.size)
        mask = Image.new("L", size, 0).place(Image.new("L", mask.size, 255), mask=mask.as_mask()).pad(1, 0)
        a = np.round(np.array(mask) / 255)
        d = ndimage.distance_transform_edt(a) + ndimage.distance_transform_edt(1-a)
        b = np.select([d<=w, d<=w+1], [np.ones_like(d), 1-(d-w)], np.zeros_like(d))
        m = Image.fromarray(np.round(255 * b).astype('uint8'))
        return m.trim(1)
    antialiasing = False
    
# Text markup expressions (used by Image.Image.from_markup)

class MarkupExpression:
    """Simple markup syntax for use in Image.Image.from_markup. Supports
    **bold**, //italics//, __underline__, ~~strikethrough~~ and [[color]].
    Attributes can be nested. Attributes (and \'s) can be escaped with a \."""

    MARKDOWN = { "u": "__", "i": "//", "b": "**", "s": "~~", "c": ("[[", "]]") }
    MARKDOWN = { m : (v, v) if isinstance(v, str) else v for m,v in MARKDOWN.items() }
    START_MODE = { s: m for m,(s,_) in MARKDOWN.items() }
    START_END = { s: e for _,(s,e) in MARKDOWN.items() }

    def __init__(self, text):
        self.text = text
        
    def __repr__(self):
        return "MarkupExpression({})".format(self.text)
        
    @classmethod
    def first_unescaped_match_regex(cls, strings):
        # syntax is simple enough to be regular
        strings = make_iterable(strings)
        regex = "(^|.*?[^\\\\])({})(.*)".format("|".join([re.escape(s) for s in strings]))
        return re.compile(regex, flags=re.S)

    @classmethod
    def parse_markup(cls, text, mode=""):
        parsed = []
        match = ValueBox()
        while match << re.match(cls.first_unescaped_match_regex(cls.START_MODE.keys()), text):
            pre, start, post = match().groups()
            if pre: parsed.append((re.sub(r"\\(.)", r"\1", pre), mode))
            if not match << re.match(cls.first_unescaped_match_regex(cls.START_END[start]), post):
                raise ValueError("Unmatch ending for {} in {}".format(start, post))
            content, end, text = match().groups()
            parsed += cls.parse_markup(content, mode+cls.START_MODE[start])
        if text: parsed.append((re.sub(r"\\(.)", r"\1", text), mode))
        return parsed
        
    @classmethod
    def split_lines(cls, parsed):
        lines = [[]]
        for text, mode in parsed:
            while "\n" in text:
                pre, text = text.split("\n", 1)
                lines[-1].append((pre, mode))
                lines.append([])
            lines[-1].append((text, mode))
        return lines
                
    def get_parsed(self):
        return self.split_lines(self.parse_markup(self.text))
    
    def get_text(self):
        return "".join(s for s,_ in self.parse_markup(self.text))
    
    def reparse_wrapped_text(self, wrapped_text):
        # text wrapping uses raw text so need to merge the result back in
        x = ValueBox()
        old, new, merged = self.text, wrapped_text, ""
        while old or new:
            if old and new and old[0] == new[0]:
                merged, old, new = merged + old[0], old[1:], new[1:]
            elif x << first(m for m in itertools.chain(self.START_END.keys(), self.START_END.values()) if old.startswith(m)):
                merged, old = merged + x(), old[len(x()):]
            elif new and new[0] in "\n-":
                merged, new = merged + new[0], new[1:]
            elif old and old[0] in "\\":
                merged, old = merged + old[0], old[1:]
            elif old and old[0] in " ":
                old = old[1:]
            else:
                raise RuntimeError("Failed to merge {} with {}: difference at {} and {}".format(wrapped_text, self.text, new, old))
        self.text = merged
