import re
import os
import os.path
import logging
import abc as ABC

from collections import namedtuple
from functools import partial
from io import BytesIO
from itertools import zip_longest
from numbers import Real, Integral
from urllib.parse import urlparse
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps
from utils import *

pyphen = optional_import("pyphen")
requests = optional_import("requests")
np = optional_import("numpy")

# Various pillow utilities, monkey patched onto the Image, ImageDraw and ImageColor classes

logger = logging.getLogger('pillar')
logger.setLevel(logging.DEBUG)

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

    @property
    def x(self): return self.xy[0]
    @property
    def y(self): return self.xy[1]
        
class Padding():
    """Padding class, initialized from one, two or four integers."""
    
    def __init__(self, padding):
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
        
    def __init__(self, box, padding=None):
        padding = Padding(padding)
        if isinstance(box, Image.Image):
            self.corners = (0, 0, box.width-1, box.height-1)
        elif non_string_sequence(box, Integral) and len(box) == 4:
            self.corners = tuple(box)
        elif non_string_sequence(box) and all(non_string_sequence(point, Integral) and len(point) == 2 for point in box):
            self.corners = (min(x for x,y in box), min(y for x,y in box), max(x for x,y in box), max(y for x,y in box))
        else:
            raise TypeError("Box expects four coordinates or a collection of points: got {}".format(box))
        self.corners = (self.l - padding.l, self.u - padding.u, self.r + padding.r, self.d + padding.d)        
            
    def __repr__(self):
        return "Box(l={}, u={}, r={}, d={})".format(self.l, self.u, self.r, self.d)

    def __iter__(self):
        return iter(self.corners)
        
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
    def center(self): return ((self.l + self.r + 1) // 2, (self.u + self.d + 1) // 2)
            
    def __contains__(self, other):
        if non_string_sequence(other, Integral) and len(other) == 2:
            return self.l <= other[0] <= self.r and self.u <= other[1] <= self.d
        else:
            return NotImplemented
            
    
def whitespace_span_tokenize(text):
    """Whitespace span tokenizer."""
    return ((m.start(), m.end()) for m in re.finditer(r'\S+', text))

def language_hyphenator(lang='en_EN'):
    """pyphen-based position hyphenator."""
    return pyphen.Pyphen(lang=lang).positions

class _ImageDraw():

    _emptyImage = Image.new("RGBA", (0,0))
    _emptyDraw = ImageDraw.Draw(_emptyImage)
    
    @classmethod
    def textsize(cls, *kargs, **kwargs):
        """Return the size of the given string, in pixels."""
        return cls._emptyDraw.textsize(*kargs, **kwargs)

    @classmethod
    def multiline_textsize(cls, *kargs, **kwargs):
        """Return the size of the given string, in pixels."""
        return cls._emptyDraw.multiline_textsize(*kargs, **kwargs)
        
    @classmethod
    def word_wrap(cls, text, font, max_width, tokenizer=whitespace_span_tokenize, hyphenator=None):
        """Returns a word-wrapped string from text that would fit inside the given max_width with
        the given font. Uses a span-based tokenizer and optional position-based hyphenator."""
        spans = list(tokenizer(text))
        line_start, line_end = 0, spans[0][0]
        output = text[line_start:line_end]
        hyphens = lambda s: ([] if hyphenator is None else hyphenator(s)) + [len(s)]
        for (tok_start, tok_end) in spans:
            if cls.textsize(text[line_start:tok_end], font)[0] < max_width:
                output += text[line_end:tok_end]
                line_end = tok_end
            else: 
                hyphen_start = tok_start
                for hyphen in hyphens(text[tok_start:tok_end]):
                    hopt = '' if text[tok_start+hyphen-1] == '-' else '-'
                    if cls.textsize(text[line_start:tok_start+hyphen]+hopt, font)[0] < max_width:
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

ImageDraw.textsize = _ImageDraw.textsize
ImageDraw.multiline_textsize = _ImageDraw.multiline_textsize
ImageDraw.word_wrap = _ImageDraw.word_wrap

RGBA = namedtuple('RGBA', ['red', 'green', 'blue', 'alpha'])

class _ImageColor():

    @classmethod
    def getrgba(cls, color):
        """Convert color to an RGBA named tuple."""
        color = tuple(color) if non_string_iterable(color) else ImageColor.getrgb(color)
        if len(color) not in (3, 4) or not all(0 <= x <= 255 for x in color): 
            raise ValueError("Invalid RGB(A) color.")
        if len(color) == 3: color += (255,)
        return RGBA(*color)
        
    @classmethod
    def to_hex(cls, color):
        """Convert a color to a hex string. Ignores alpha channel."""
        return "#" + "".join("{:02x}".format(c) for c in cls.getrgba(color)[:3])
            
    @classmethod
    def to_linear(cls, srgb):
        """Convert a single sRGB color value between 0 and 255 to a linear value between 0 and 1."""
        c = srgb / 255
        return c / 12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4 
        
    @classmethod
    def from_linear(cls, lrgb):
        """Convert a single linear RGB value between 0 and 1 to an sRGB value between 0 and 255."""
        c = 12.92 * lrgb if lrgb <= 0.0031308 else (1.055)*lrgb**(1/2.4)-0.055
        return round(c * 255)
            
    @classmethod
    def blend(cls, color1, color2, p=0.5):
        """Blend two colours with gamma correction."""
        color1, color2 = cls.getrgba(color1), cls.getrgba(color2)
        return RGBA(*[fl(tl(c1) + (tl(c2)-tl(c1))*p) for c1,c2,fl,tl in zip_longest(color1,color2,[cls.from_linear]*3,[cls.to_linear]*3,fillvalue=round)])
        
    @classmethod
    def brighten(cls, color, p):
        """Brighten a color. Same as blending with white (but preserving alpha)."""
        color = cls.getrgba(color)
        white = cls.getrgba("white")._replace(alpha=color.alpha)
        return cls.blend(color, white, p)
            
    @classmethod
    def darken(cls, color, p):
        """Darken a color. Same as blending with black (but preserving alpha)."""
        color = cls.getrgba(color)
        white = cls.getrgba("black")._replace(alpha=color.alpha)
        return cls.blend(color, white, p)
            
    @classmethod
    def from_floats(cls, color):
        """Convert a 0-1 float color tuple (or a list of such tuples) to 0-255 ints."""
        if non_string_sequence(color, Real):
            return cls.getrgba([int(x*255) for x in color])
        else:
            return [cls.getrgba([int(x*255) for x in c]) for c in color]
            
ImageColor.getrgba = _ImageColor.getrgba
ImageColor.from_floats = _ImageColor.from_floats
ImageColor.to_hex = _ImageColor.to_hex
ImageColor.to_linear = _ImageColor.to_linear
ImageColor.from_linear = _ImageColor.from_linear
ImageColor.blend = _ImageColor.blend
ImageColor.brighten = _ImageColor.brighten
ImageColor.darken = _ImageColor.darken

RGBA.to_hex = papply(ImageColor.to_hex)
RGBA.blend = papply(ImageColor.blend)
RGBA.brighten = papply(ImageColor.brighten)
RGBA.darken = papply(ImageColor.darken)

class _Image(Image.Image):

    @classmethod
    def from_text(cls, text, font, fg="black", bg=None, padding=0,
                  max_width=None, line_spacing=0, align="left",
                  tokenizer=whitespace_span_tokenize, hyphenator=None):
        """Create image from text. If max_width is set, uses the tokenizer and optional hyphenator
        to split text across multiple lines."""
        padding = Padding(padding)
        if bg is None:
            bg = ImageColor.getrgba(fg)._replace(alpha=0)
        if max_width is not None:
            text = ImageDraw.word_wrap(text, font, max_width, tokenizer, hyphenator)
        w,h = ImageDraw.textsize(text, font, spacing=line_spacing)
        if max_width is not None and w > max_width:
            logger.warning("Text cropped as too wide to fit: {}".format(text))
            w = max_width
        img = Image.new("RGBA", (w + padding.x, h + padding.y), bg)
        draw = ImageDraw.Draw(img)
        draw.text((padding.l, padding.u), text, font=font, fill=fg, spacing=line_spacing, align=align)
        return img

    @classmethod
    def from_text_bounded(cls, text, bbox, max_font_size, font_fn, *args, min_font_size = 6, **kwargs):
        """Create image from text, reducing the font size until it fits. Inefficient."""
        if isinstance(bbox, Integral): bbox = (bbox, bbox)
        for size in range(max_font_size, min_font_size-1, -1):
            img = cls.from_text(text, font_fn(size), *args, **kwargs)
            if img.width <= bbox[0] and img.height <= bbox[1]: return img
        return None
        
    @classmethod
    def from_pattern(cls, pattern, size, align=0, scale=(False,False), preserve_aspect=False, resample=Image.LANCZOS):
        """Create an image using a background pattern, either scaled or tiled."""
        align = Alignment(align)
        img = Image.new("RGBA", size)
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
    def from_array(cls, array, xalign=0.5, yalign=0.5, padding=0, bg=0):
        """Create an image from an array of images."""
        if not non_string_iterable(xalign): xalign = [xalign] * max(len(r) for r in array)
        if not non_string_iterable(yalign): yalign = [yalign] * len(array)
        align = [[Alignment((xalign[c], yalign[r])) for c,_ in enumerate(row)] for r,row in enumerate(array)]
        padding = Padding(padding)
        heights = [max(img.height if img is not None else 0 for img in row) + padding.y for row in array]
        widths = [max(img.width if img is not None else 0 for img in column) + padding.x for column in zip_longest(*array)]
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
        """Create an image from a row of images."""
        return cls.from_array([row], **kwargs)
        
    @classmethod
    def from_column(cls, column, **kwargs):
        """Create an image from a column of images."""
        return cls.from_array([[img] for img in column], **kwargs)
    
    @classmethod
    def from_url(cls, url, filepath=None):
        """Create an image from a url, optionally saving it to a filepath."""
        HEADERS = {'User-Agent': 'Mozilla/5.0'}
        uparse = urlparse(url)
        if uparse.scheme == '':
            raise TypeError("from_url expects url, got {}".format(url))
        logger.debug("Reading image from {}".format(url))
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
        uparse = urlparse(url)
        filepath = os.path.join(cache_dir, filename or url_to_filepath(url))
        if os.path.isfile(filepath):
            logger.debug("Loading cached image at {}".format(filepath))
            img = Image.open(filepath)
        else:
            img = cls.from_url(url, filepath)
        return img
        
    def to_rgba(self):
        """Return an RGBA copy of the image (or leave unchanged if it already is)."""
        return self if self.mode == "RGBA" else self.convert("RGBA")
        
    def overlay(self, img, box=(0,0), mask=None, copy=False):
        """Paste an image respecting alpha channels (unlike Image.paste)."""
        if isinstance(box, BoundingBox): box = box.corners
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
        
    def pad(self, padding, bg="black", offsets=None):
        """Return a padded image. Updates optional offset structure."""
        padding = Padding(padding)
        if offsets is not None: offsets.update(offsets + padding)
        if padding.x == padding.y == 0: return self
        img = Image.new("RGBA", (self.width + padding.x, self.height + padding.y), bg)
        return img.overlay(self, (padding.l, padding.u), None)
        
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
            
    def replace_color(self, color1, color2, ignore_alpha=False):
        """Return an image with color1 replaced by color2. Requires numpy."""
        if 'RGB' not in self.mode:
            raise NotImplementedError("replace_color expects RGB/RGBA image")
        n = 3 if (self.mode == 'RGB' or ignore_alpha) else 4
        color1 = ImageColor.getrgba(color1)[:n]
        color2 = ImageColor.getrgba(color2)[:n]
        data = np.array(self)
        mask = _nparray_mask_by_color(data, color1, n)
        data[:,:,:n][mask] = color2
        return Image.fromarray(data)

    def select_color(self, color):
        """Return a transparency mask selecting a color in an image. Requires numpy."""
        if 'RGB' not in self.mode:
            raise NotImplementedError("replace_color expects RGB/RGBA image")
        data = np.array(self)
        color = ImageColor.getrgba(color)[:data.shape[-1]]
        mask = _nparray_mask_by_color(data, color)
        return Image.fromarray(mask * 255).convert("1")
        
    def remove_transparency(self, bg="white"):
        """Return an image with the transparency removed"""
        if not self.mode.endswith('A'): return self
        bg = ImageColor.getrgba(bg)._replace(alpha=255)
        alpha = self.convert("RGBA").split()[-1]
        img = Image.new("RGBA", self.size, bg)
        img.paste(self, mask=alpha)
        return img
        
    def invert_mask(self):
        """Invert image for use as a mask"""
        return ImageOps.invert(self.split()[-1].convert("L"))
        
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

def _nparray_mask_by_color(nparray, color, num_channels=None):
    if len(nparray.shape) != 3: raise NotImplementedError
    n = nparray.shape[-1] if num_channels is None else num_channels
    channels = [nparray[...,i] for i in range(n)]
    mask = np.ones(nparray.shape[:-1], dtype=bool)
    for c,channel in zip(color, channels):
        mask = mask & (channel == c)
    return mask

Image.from_text = _Image.from_text
Image.from_text_bounded = _Image.from_text_bounded
Image.from_array = _Image.from_array
Image.from_row = _Image.from_row
Image.from_column = _Image.from_column
Image.from_pattern = _Image.from_pattern
Image.from_gradient = _Image.from_gradient
Image.from_vertical_pattern = _Image.from_vertical_pattern
Image.from_horizontal_pattern = _Image.from_horizontal_pattern
Image.from_url = _Image.from_url
Image.from_url_with_cache = _Image.from_url_with_cache
Image.EMPTY_IMAGE = Image.new("RGBA", (0,0))

Image.Image.to_rgba = _Image.to_rgba
Image.Image.overlay = _Image.overlay
Image.Image.place = _Image.place
Image.Image.pad = _Image.pad
Image.Image.trim = _Image.trim
Image.Image.pin = _Image.pin
Image.Image.crop_to_aspect = _Image.crop_to_aspect
Image.Image.pad_to_aspect = _Image.pad_to_aspect
if not hasattr(Image.Image, 'resize_nonempty'):
    Image.Image.resize_nonempty=Image.Image.resize
Image.Image.resize = _Image.resize
Image.Image.resize_fixed_aspect = _Image.resize_fixed_aspect
Image.Image.replace_color = _Image.replace_color
Image.Image.select_color = _Image.select_color
Image.Image.remove_transparency = _Image.remove_transparency
Image.Image.invert_mask = _Image.invert_mask
Image.Image.add_grid = _Image.add_grid

def font(name, size, bold=False, italics=False, **kwargs):
    """Return a truetype font object."""
    variants = [["", "i"], ["bd", "bi"]]
    return ImageFont.truetype("{}{}.ttf".format(name, variants[bold][italics]), size, **kwargs)

arial = partial(font, "arial")

class Shape(object):
    """Abstract base class for generating simple geometric shapes."""
    __metaclass__ = ABC.ABCMeta
    
    @classmethod
    @ABC.abstractmethod
    def mask(cls, size, **kwargs):
        """Generate a mask of the appropriate shape and size. Additional parameters should be size-independent."""
    
    def __new__(cls, size, fg, bg=0, alias=4, **kwargs): # TODO: transpose
        """Generate an image of the appropriate shape, size and color."""
        if isinstance(size, Integral): size = (size, size)
        asize = tuple(round(s * alias) for s in size)
        base = Image.new("RGBA", asize, bg)
        fore = Image.new("RGBA", asize, fg)
        mask = cls.mask(asize, **kwargs)
        return base.overlay(fore, mask=mask).resize(size, resample=Image.LANCZOS if alias > 2 else Image.NEAREST)
        
class Rectangle(Shape):
    @classmethod
    def mask(cls, size):
        return Image.new("L", size, 255)
    
class Ellipse(Shape):
    @classmethod
    def mask(cls, size):
        x, y = size
        rx, ry = (x-1)/2, (y-1)/2
        array = np.fromfunction(lambda j, i: ((rx-i)**2/rx**2+(ry-j)**2/ry**2 <= 1), (y,x))
        return Image.fromarray(255 * array.view('uint8'))
        
# TODO: Rhombus/kite, Paralellogram, Triangle, Ring
