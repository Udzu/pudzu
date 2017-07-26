import re
import os
import os.path
import logging

from collections import namedtuple
from functools import partial
from io import BytesIO
from itertools import zip_longest
from numbers import Real, Integral
from urllib.parse import urlparse
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFont, ImageColor
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
        if isinstance(padding, Integral):
            return self.__init__((padding, padding, padding, padding))
        elif non_string_sequence(padding, Integral) and len(padding) == 2:
            return self.__init__((padding[0], padding[1], padding[0], padding[1]))
        elif non_string_sequence(padding, Integral) and len(padding) == 4:
            if not all(0 <= x for x in padding):
                raise ValueError("Padding values should be positive: got {}".format(padding))
            self.padding = padding
        elif isinstance(padding, Padding):
            self.padding = padding.padding
        else:
            raise TypeError("Padding expects one, two or four integers: got {}".format(padding))
            
    def __repr__(self):
        return "Padding(l={}, u={}, r={}, d={})".format(self.l, self.u, self.r, self.d)

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

def whitespace_span_tokenize(text):
    """Whitespace span tokenizer."""
    return ((m.start(), m.end()) for m in re.finditer(r'\S+', text))

def language_hyphenator(lang='en_EN'):
    """pyphen-based position hyphenator."""
    return pyphen.Pyphen(lang=lang).positions

class _ImageDraw():

    _emptyImage = Image.new("RGB", (0,0))
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

def _getrgba(color):
    """Convert color to an RGBA named tuple."""
    color = tuple(color) if non_string_sequence(color, Integral) else ImageColor.getrgb(color)
    if len(color) == 3: color += (255,)
    return RGBA(*color)

ImageColor.getrgba = _getrgba

class _Image(Image.Image):

    @classmethod
    def from_text(cls, text, font, fg="white", bg=None, padding=0,
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
        
    def overlay(self, img, box=(0,0), mask=Ellipsis, copy=False):
        """Paste an image. By default this uses its alpha channel as a mask (unlike Image.paste)."""
        if mask is Ellipsis:
            mask = img if 'A' in img.mode else None
        base = self.copy() if copy else self
        base.paste(img, box, mask)
        return base
        
    def place(self, img, align=0.5, padding=0, mask=Ellipsis, copy=True):
        """Overlay an image using the given alignment and padding."""
        align, padding = Alignment(align), Padding(padding)
        x = int(padding.l + align.x * (self.width - (img.width + padding.x)))
        y = int(padding.u + align.y * (self.height - (img.height + padding.y)))
        return self.overlay(img, (x, y), mask=mask, copy=copy)
        
    def pad(self, padding, bg="black"):
        """Return a padded image."""
        padding = Padding(padding)
        if padding.x == padding.y == 0: return self
        img = Image.new("RGBA", (self.width + padding.x, self.height + padding.y), bg)
        return img.overlay(self, (padding.l, padding.u), None)
        
    def pin(self, img, position, align=0.5, bg=(0,0,0,0)):
        """Pin an image onto another image, copying and if necessary expanding it."""
        align = Alignment(align)
        x = int(position[0] - align.x * img.width)
        y = int(position[1] - align.y * img.height)
        padded = self.pad((max(0, -x), max(0, -y), max(0, x+img.width-self.width), max(0, y+img.height-self.height)), bg=bg)
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

    def pad_to_aspect(self, aspect, divisor=1, align=0.5, bg="black"):
        """Return a padded image with the given aspect ratio."""
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
        return img.overlay(self, (x, y), None)

    def resize(self, size, resample=Image.LANCZOS):
        """Return a resized copy of the image, handling zero-width/height sizes."""
        if size[0] == 0 or size[1] == 0:
            return Image.new(self.mode, size)
        else:
            return self.resize_nonempty(size, resample=resample)
        
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

def _nparray_mask_by_color(nparray, color, num_channels=None):
    if len(nparray.shape) != 3: raise NotImplementedError
    n = nparray.shape[-1] if num_channels is None else num_channels
    channels = [nparray[...,i] for i in range(n)]
    mask = np.ones(nparray.shape[:-1], dtype=bool)
    for c,channel in zip(color, channels):
        mask = mask & (channel == c)
    return mask

Image.from_text = _Image.from_text
Image.from_array = _Image.from_array
Image.from_row = _Image.from_row
Image.from_column = _Image.from_column
Image.from_pattern = _Image.from_pattern
Image.from_vertical_pattern = _Image.from_vertical_pattern
Image.from_horizontal_pattern = _Image.from_horizontal_pattern
Image.from_url = _Image.from_url
Image.from_url_with_cache = _Image.from_url_with_cache
Image.EMPTY_IMAGE = Image.new("RGBA", (0,0))

Image.Image.overlay = _Image.overlay
Image.Image.place = _Image.place
Image.Image.pad = _Image.pad
Image.Image.pin = _Image.pin
Image.Image.crop_to_aspect = _Image.crop_to_aspect
Image.Image.pad_to_aspect = _Image.pad_to_aspect
Image.Image.resize_nonempty = Image.Image.resize
Image.Image.resize = _Image.resize
Image.Image.resize_fixed_aspect = _Image.resize_fixed_aspect
Image.Image.replace_color = _Image.replace_color
Image.Image.select_color = _Image.select_color

def font(name, size, bold=False, italics=False):
    """Return a truetype font object."""
    variants = [["", "i"], ["bd", "bi"]]
    return ImageFont.truetype("{}{}.ttf".format(name, variants[bold][italics]), size)

arial = partial(font, "arial")
