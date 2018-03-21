import sys
sys.path.append('..')
import pandas as pd
from pillar import *

def generate_photo(filepath, url, align=None, size=(600,200), credit_fonts=partial(verdana, 16), credit_bg="black", credit_fg="white", credit_overlay=True):
    urls = url.split('|')
    aligns = tmap(float, str(align).split('|')) if align else [(0.5, 0.25)]*len(urls)
    imgs = []
    for j, (url, align) in  enumerate(zip_equal(urls, aligns)):
        img = Image.from_url_with_cache(url).to_rgba()
        sz = ((size[0]*(j+1))//len(urls)-(size[0]*j)//len(urls), size[1])
        imgs.append( img.cropped_resize(sz, align=align, upsize=False) )
    img = Rectangle(size, "white").place(Image.from_row(imgs, yalign=0), align=0) 
    if credit_fonts:
        sources = [urlparse(url).netloc.split(".", int(urlparse(url).netloc.count(".") > 1))[-1] for url in urls]
        if len(set(sources)) == 1: sources = sources[:1]
        credit = "**Source{}**: {}".format("s"*(len(urls)>1), ", ".join(sources))
        credit_img = Image.from_markup(credit, credit_fonts, credit_fg, credit_bg, padding=(3,1), beard_line=True)
        img = img.place(credit_img, align=(0,1)) if credit_overlay else img.pin(credit_img, (0,img.height), align=0, bg=credit_bg)
    img.convert("RGB").save(filepath)

def generate_temp(url, label="__temp__", **kwargs):
    os.makedirs("output/__temp__", exist_ok=True)
    generate_photo("output/__temp__/{}.jpg".format(label), url, **kwargs)

def generate_photoset(datapath, **kwargs):
    df = pd.read_csv(datapath)
    dirname = "output/{}".format(os.path.splitext(os.path.basename(datapath))[0])
    os.makedirs(dirname, exist_ok=True)
    for i,(_,d) in enumerate(df.iterrows(), 1):
        generate_photo("{}/{}. {}.jpg".format(dirname, i, d.label), d.image, align=get_non(d, 'align'), **kwargs)

