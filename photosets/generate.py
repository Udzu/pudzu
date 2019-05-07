from pudzu.pillar import *
from pudzu.bamboo import *

CREDIT_FONTS = partial(verdana, 16)

def generate_photo(filepath, url, align=None, size=(600,200), crop=True, credit_fonts=None, credit_bg="black", credit_fg="white", credit_overlay=True):
    urls = url.split('|')
    if align is None: align = '|' * url.count('|')
    aligns = [float(a) if a else (0.5, 0.25) for a in str(align).split('|')]
    imgs = []
    for j, (url, align) in  enumerate(zip_equal(urls, aligns)):
        img = Image.from_url_with_cache(url).to_rgba()
        sz = ((size[0]*(j+1))//len(urls)-(size[0]*j)//len(urls), size[1])
        imgs.append( img.cropped_resize(sz, align=align, upsize=False) if crop else img.resize(sz) )
    img = Rectangle(size, "white").place(Image.from_row(imgs, yalign=0), align=0) 
    if credit_fonts:
        sources = [urlparse(url).netloc.split(".", int(urlparse(url).netloc.count(".") > 1))[-1] for url in urls]
        if len(set(sources)) == 1: sources = sources[:1]
        credit = "**Source{}**: {}".format("s"*(len(urls)>1), ", ".join(sources))
        credit_img = Image.from_markup(credit, credit_fonts, credit_fg, credit_bg, padding=(3,1), beard_line=True)
        img = img.place(credit_img, align=(0,1)) if credit_overlay else img.pin(credit_img, (0,img.height), align=0, bg=credit_bg)
    img.convert("RGBA").save(filepath.replace("|", ", "))

def generate_temp(url, label="__temp__", **kwargs):
    os.makedirs("output/__temp__", exist_ok=True)
    generate_photo("output/__temp__/{}.jpg".format(label), url, **kwargs)

def generate_photoset(datapath, batch_size=1, **kwargs):
    df = pd.read_csv(datapath)
    dirname = "output/{}".format(os.path.splitext(os.path.basename(datapath))[0])
    os.makedirs(dirname, exist_ok=True)
    if batch_size > 1:
        df = df.assign_rows(align=lambda d: get_non(d, 'align', '|' * d['image'].count('|')))
        df = df.groupby_rows(lambda r,i: i//batch_size).reduce(lambda c: "|".join(str(x) for x in c))
    for i,(_,d) in enumerate(df.iterrows(), 1):
        generate_photo("{}/{}. {}.png".format(dirname, i, d.label), d.image, align=get_non(d, 'align'), **kwargs)

