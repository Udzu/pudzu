from pudzu.charts import *

def parse_date(d): return Date(datetime.datetime.strptime(f"{d} 2020", "%d %B %Y"))
df = pd.read_csv("datasets/calnewyear.csv").update_columns(date=parse_date)

IMAGE_URLS = [
"https://cdn.cnn.com/cnnnext/dam/assets/191231074412-07-new-years-celebration-0101.jpg",
"http://tibetpedia.com/wp-content/uploads/2016/05/Losar-Religious-Festival-Tibet-862x595.jpg",
"https://media.timeout.com/images/105166497/image.jpg",
"https://static.independent.co.uk/s3fs-public/thumbnails/image/2019/04/09/14/vaisakhi-hero.jpg?w968h681",
"https://previews.123rf.com/images/blankstock/blankstock1904/blankstock190402243/123562351-no-or-stop-balloons-icon-amusement-park-or-birthday-party-sign-prohibited-ban-stop-symbol-no-balloon.jpg",
"https://www.bolivianlife.com/wp-content/uploads/2014/06/aymara-new-year-bolivia-41.jpg",
"https://resources.stuff.co.nz/content/dam/images/1/5/i/i/d/a/image.related.StuffLandscapeSixteenByNine.710x400.15hr35.png/1435277718297.jpg",
"https://img.jakpost.net/c/2018/09/11/2018_09_11_53495_1536684337._large.jpg",
"https://static01.nyt.com/images/2017/09/20/opinion/20weissWeb/20weissWeb-superJumbo.jpg",
"https://img.huffingtonpost.com/asset/55a5d7c91200002c001347fa.jpeg?ops=scalefit_630_400_noupscale",
"https://cdn.telanganatoday.com/wp-content/uploads/2019/10/ECODIWALI-600x400-600x400-1.jpg",
"https://www.adotrip.com/public/images/festivals/5c3f0b54b6475-Losoong%20Festival%20Sight%20Seeing%20Tour.jpg",
]
IMAGES = [Image.from_url_with_cache(i).crop_to_aspect(3,2, align=(0.5,0.65)) for i in IMAGE_URLS]

def bgfn(d, w, h, sightings=None):
    return "#ffcccc" if d in list(df.date) else "white" 

month_imgs = [month_chart(Date((2020,m,1)), cell_width=120, cell_height=80, cell_padding=2, month_height=60, weekday_height=40, day_start=1, day_bg=bgfn, month_image=IMAGES[m-1], month_label="{M}", month_bg="#E0E0E0", fonts=partial(sans, 32)) for m in range(1,13)]
months = Image.from_array(list(generate_batches(month_imgs, 4)), padding=20, bg="white", yalign=0)

label_text = [[row.date.date_format("{d} {M}: "), row.celebrations.replace("(","(//").replace(")","//)")] for _,row in df.iterrows()]
labels = Image.from_array(tmap_leafs(lambda s: Image.from_markup(s, partial(sans, 64), beard_line=True, padding=4), label_text), xalign=(1,0), bg="white")
legend = Image.from_column([Image.from_text("SELECTED NEW YEARS", sans(80, bold=True)), labels, Image.from_text("*celebrated from the previous evening", sans(64, italics=True))], padding=(0,40))

grid = Image.from_row([months, legend], bg="white", padding=20)
title = Image.from_text_justified("Different New Year's Days to celebrate in 2020".upper(), int(grid.width*0.9), 160, partial(sans, bold=True))
img = Image.from_column([title, grid], padding=20, bg="white")

img = img.place(Image.from_text("μαλάκας", sans(32), fg="black", bg="white", padding=10).pad((2,2,0,0), "black"), align=1, padding=20)
img.save("output/calnewyear.png")
img.convert("RGB").save("output/calnewyear.jpg")

