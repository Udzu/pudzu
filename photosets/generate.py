import sys
sys.path.append('..')
import pandas as pd
from pillar import *

def generate_photoset(path, size=(600,200), credit_fonts=partial(verdana, 16), credit_overlay=True, credit_bg="black", credit_fg="white"):
    df = pd.read_csv(path)
    dirname = "output/{}".format(os.path.splitext(os.path.basename(path))[0])
    os.makedirs(dirname, exist_ok=True)
    for i,(_,d) in enumerate(df.iterrows(), 1):
        urls = d.image.split('|')
        aligns = tmap(float, str(d['align']).split('|')) if get_non(d, 'align') else [(0.5, 0.25)]*len(urls)
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
        img.convert("RGB").save("{}/{}. {}.jpg".format(dirname, i, d.label))
