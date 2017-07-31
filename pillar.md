# [pillar.py](pillar.py)

## Summary 
Various Pillow utilities. These are monkey-patched on, allowing continued use of the Image.new factory function. Most have only been tested in RGB/RGBA modes and may not work in other modes.
 
## Dependencies
*Required*: [pillow](http://pillow.readthedocs.io/en/4.2.x/index.html), [toolz](http://toolz.readthedocs.io/en/latest/index.html), [utils](utils.md).

*Optional*: [pyphen](http://pyphen.org/) (for text hyphenation), [requests](http://docs.python-requests.org/en/master/) (for HTTP request headers).

## Documentation

### Helper functions

**Padding**: a class representing box padding, initialized from one, two or four integers. Any function below that has a padding parameter can be passed any of these.

```python
>> Padding(10)
Padding(l=10, u=10, r=10, d=10)
>> Padding((10,0))
Padding(l=10, u=0, r=10, d=0)
>> Padding((10,0,0,5))
Padding(l=10, u=0, r=0, d=5)
```

**Alignment**: a class representing element alignment, initialized from one or two floats between 0 and 1. Any function below that has an element alignment parameter can be passed one of these.

```python
>> Alignment(0.5)
Alignment(x=50%, y=50%)
>> Alignment((0,1))
Alignment(x=0%, y=100%)
```

**BoundingBox**: a class representing a bounding box, initialized from the 4 coordinates or from a collection of points, with optional padding. Not really used at the moment.

```python
>> BoundingBox([(10,10), (15,8), (12,15)])
Box(l=10, u=8, r=15, d=15)
>> _.width
25
>> BoundingBox((5,5,10,10), padding=2)
Box(l=3, u=3, r=12, d=12)
```

**font**: shorthand function for generating a truetype font object with standard variant naming (e.g. arialbd for bold). Also, **arial** is defined explicitly for the Arial family.

```python
>> font("times", 24, italics=True)
<PIL.ImageFont.FreeTypeFont at 0x48e9ad0>
>> [_.font.family, _.font.style, _.size]
['Times New Roman', 'Italic', 24]
>> arial(24, bold=True)
<PIL.ImageFont.FreeTypeFont at 0x4a335f0>
```

### ImageColor

**ImageColor.getrgba**: converts a named color or RGB triple to an RGBA named tuple.

```python
>> ImageColor.getrgba("yellow")
RGBA(red=255, green=255, blue=0, alpha=255)
>> ImageColor.getrgba("yellow")._replace(alpha=0)
RGBA(red=255, green=255, blue=0, alpha=0)
>> ImageColor.getrgba("#fafafa")
RGBA(red=250, green=250, blue=250, alpha=255)
>> ImageColor.getrgba((100,50,50))
RGBA(red=100, green=50, blue=50, alpha=255)
>> ImageColor.getrgba((100,50,50,5))
RGBA(red=100, green=50, blue=50, alpha=5)
```

### ImageDraw

**ImageDraw.textsize**: same as ImageDraw.Draw.textsize but doesn't require a drawable object. Similarly, **ImageDraw.multiline_textsize**.

```python
>> ImageDraw.textsize("The rain", arial(24))
(88, 22)
```

### Image

**Image.from_url**: create an image from a URL. **Image.from_url_with_cache** does the same but uses a file cache (with a default filename structure of cache_directory/hostname/hash_of_path.extension).

```python
>> Image.from_url('https://assets-cdn.github.com/images/modules/logos_page/Octocat.png')
[10:05:03] pillar:DEBUG - Reading image from https://assets-cdn.github.com/images/modules/logos_page/Octocat.png
>> Image.from_url_with_cache('https://assets-cdn.github.com/images/modules/logos_page/Octocat.png')
[10:05:27] pillar:DEBUG - Reading image from https://assets-cdn.github.com/images/modules/logos_page/Octocat.png
[10:05:28] pillar:DEBUG - Saving cached image to cache\assets-cdn.github.com\d4b25973fbbe302e1b486000f43aa25b9c61f9bf.png
>> Image.from_url_with_cache('https://assets-cdn.github.com/images/modules/logos_page/Octocat.png')
[10:05:38] pillar:DEBUG - Loading cached image at cache\assets-cdn.github.com\d4b25973fbbe302e1b486000f43aa25b9c61f9bf.png
```

**Image.from_text**: creates an image from text and font. Supports word-wrapping, alignment, padding and hyphenation. Wrapping can use an arbitrary tokenizer (it uses whitespace splitting by default) and hyphenation requires a hyphenator (the phyphen module is a good source of these).

```python
>> Image.from_text("The rain", arial(16, bold=True), fg="white", bg="#1f5774", padding=10).show()
```

![alt](images/fromtext1.png)

```python
>> Image.from_text("dedicated to the proposition that all men are created equal", arial(16),
                   fg="white", bg="black", max_width=100, align="center", padding=5).show()
```

![alt](images/fromtext2.png)

```python
>> Image.from_text("dedicated to the proposition that all men are created equal", arial(16), 
                   fg="white", bg="black", max_width=100, align="left", padding=5,
                   hyphenator=language_hyphenator("en_EN")).show()
```

![alt](images/fromtext3.png)

**Image.from_array**: create an image from an array of images. Similarly, **Image.from_row** and **Image.from_column** create images form a list of images.

```python
>> Image.from_array([[Image.from_text("{}×{}={}".format(x,y,x*y), arial(16)) for x in (2,4,8)] for y in range(5)],
                    padding=(5,2), xalign=(0,0.5,1), bg="#1f5774").show()
```                    

![alt](images/fromarray1.png)

**Image.from_pattern**: create an image from a background pattern, either scaled or tiled. Similarly, **Image.from_vertical_pattern** and **Image.from_horiztonal_pattern** automatically scale to the image width or height.

```python
>> flag = Image.from_url("https://upload.wikimedia.org/wikipedia/en/thumb/a/ae/Flag_of_the_United_Kingdom.svg/800px-Flag_of_the_United_Kingdom.svg.png")
>> Image.from_pattern(flag.resize_fixed_aspect(width=50), (150,150)).show()
```

![alt](images/frompattern1.png)

```python
>> Image.from_vertical_pattern(flag, (150,150)).show()
```

![alt](images/frompattern2.png)

```python
>> Image.from_horizontal_pattern(flag, (150,150), align=0.5).show()
```

![alt](images/frompattern3.png)

**Image.EMPTY_IMAGE**: an empty "RGBA" image.

```python
>> Image.EMPTY_IMAGE
<PIL.Image.Image image mode=RGBA size=0x0 at 0x497C310>
```

### Image.Image

**Image.Image.overlay**: like Image.Image.paste, but by default uses the pasted image's alpha channel as a mask and supports a copy parameter.

```python
>> base = Image.new("RGB", (100,60), "blue")
>> base.overlay(Image.from_text("red", arial(24)), (0,0), copy=True).show()
```

![alt](images/overlay1.png)

**Image.Image.place**: overlay an image at the given alignment and padding.

```python
>> img = Image.from_text("red", arial(24), bg="grey")
>> base.place(img).show()
```

![alt](images/place1.png)

```python
>> base.place(img, align=(0,1), padding=5).show()
```

![alt](images/place2.png)

**Image.Image.pin**: pin an image on another, expanding the base image if necessary.

```python
>> base.pin(img, (0,30), bg="black").show()
```

![alt](images/pin1.png)

```python
>> base.pin(img, (0,30), align=(1,0.5), bg="black").show()
```

![alt](images/pin2.png)

**Image.Image.pad**: pad an image.

```python
>> base.pad(5, "grey").show()
```

![alt](images/pad1.png)

```python
>> base.pad((10,10,0,0), "grey").show()
```

![alt](images/pad2.png)

**Image.Image.resize**: monkey-patched to handle zero-width/height sizes.

```python
>> flag.resize((0,100))
<PIL.Image.Image image mode=RGBA size=0x100 at 0x4DEDEF0>
```

**Image.Image.resize_fixed_aspect**: resize an image, preserving its aspect ratio.

```python
>> flag.resize_fixed_aspect(scale=0.25).show()
```

![alt](images/resizefixed1.png)

```python
>> smallflag = flag.resize_fixed_aspect(width=100)
>> smallflag.show()
```

![alt](images/resizefixed2.png)

**Image.Image.pad_to_aspect**: pad an image so that it has the given aspect ratio.

```python
>> smallflag.pad_to_aspect(1, bg="grey").show()
```

![alt](images/padtoaspect1.png)

```python
>> smallflag.pad_to_aspect(800, 600, align=0).show()
```

![alt](images/padtoaspect2.png)

**Image.Image.crop_to_aspect**: crop an image so that it has the given aspect ratio.

```python
>> smallflag.crop_to_aspect(1).show()
```

![alt](images/croptoaspect1.png)

```python
>> smallflag.crop_to_aspect(800, 600, align=0).show()
```

![alt](images/croptoaspect2.png)

**Image.Image.replace_color**: return an image with one color replaced by another. Requires numpy.

```python
>> base = Image.new("RGB", (80,40), "blue").pad(5)
>> img = Image.from_text("red", arial(24), "blue")
>> base.replace_color("blue", "grey").place(img.replace_color("blue", "red", ignore_alpha=True)).show()
```

![alt](images/colorreplace.png)

**Image.Image.select_color**: return an image mask selection of a color. Requires numpy.

```python
>> pattern = Image.from_pattern(flag.resize_fixed_aspect(width=30), base.size)
>> mask = base.select_color("blue")
>> base.place(pattern, mask=mask).show()
```
![alt](images/colorselect.png)
