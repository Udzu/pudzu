import sys
sys.path.append('..')
import pandas as pd
from pillar import *

def generate_photoset(path, size=(600,200), credit_fonts=None, credit_overlay=False):
    df = pd.read_csv(path)
    dirname = "output/{}".format(os.path.splitext(os.path.basename(path))[0])
    os.makedirs(dirname, exist_ok=True)
    for i,(_,d) in enumerate(df.iterrows(), 1):
        urls = d.image.split('|')
        aligns = tmap(float, str(d['align']).split('|')) if get_non(d, 'align') else [(0.5, 0.25)]*len(urls)
        imgs = []
        for j, (url, align) in  enumerate(zip_equal(urls, aligns)):
            img = Image.from_url_with_cache(url)
            sz = ((size[0]*(j+1))//len(urls)-(size[0]*j)//len(urls), size[1])
            imgs.append( img.cropped_resize(sz, align=align, upsize=False) )
        img = Rectangle(size, "white").place(Image.from_row(imgs, yalign=0), align=0) 
        if credit_fonts:
            credit = "**Source{}**: {}".format("s"*(len(urls)>1), ", ".join(urlparse(url).netloc.split(".", int(urlparse(url).netloc.count(".") > 1))[-1] for url in urls))
            img = img.place(Image.from_markup(credit, credit_fonts, "white", "black", padding=(3,1), beard_line=True), align=(0,1))
        img.convert("RGB").save("{}/{}. {}.jpg".format(dirname, i, d.label))
