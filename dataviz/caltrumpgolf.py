from pudzu.charts import *

def parse_date(d): return Date(tmap(int, (d[0:4], d[5:7], d[8:10])))
df = pd.read_csv("datasets/trumpgolfcountoutings.csv")[["Golf Date", "Sighted?"]].update_columns(**{"Golf Date": parse_date})

INAUGURATION = Date((2017,1,20))
ABROAD = (DateRange((2017,5,20),(2017,5,27)), DateRange((2017,7,5),(2017,7,8)), DateRange((2017,7,13),(2017,7,14)), DateRange((2017,11,5),(2017,11,14)))
ORDER = ["Yes", "Likely", "Maybe", "Probably Not"]
INBG = { "Yes": "#006d2c", "Likely": "#74c476", "Maybe": "#bae4b3" }
INFG = { "Yes": "white" }
IMAGE_URLS = [
"https://static01.nyt.com/images/2017/01/21/universal/21inaugurationphotos10/20trumptomaposesionEs-superJumbo.jpg",
"https://scontent-frt3-1.cdninstagram.com/t51.2885-15/s640x640/sh0.08/e35/16583110_1807640375928963_3013102781448847360_n.jpg",
"http://theproudliberal.org/wp-content/uploads/2017/03/trumpgolf-e1490626294697.jpg",
"https://cmgpbppostonpolitics.files.wordpress.com/2017/04/040817-trump-golf.jpg",
"https://pbs.twimg.com/media/C_LXAsMXoAAOKB_.jpg",
"https://cdn-s3.si.com/images/trump-5.jpg",
"https://scontent-frt3-1.xx.fbcdn.net/v/t1.0-9/20228433_10101265952747417_2811039708191607081_n.jpg?oh=d1a781d2d7c864da28d5d8f7ceab508b&oe=5AB567AD",
"http://cdn.washingtonexaminer.biz/cache/1060x600-d58c3fbd29f39c6567858acf701676d9.jpg",
"https://static.independent.co.uk/s3fs-public/styles/story_large/public/thumbnails/image/2017/08/04/07/trump-golf.jpg",
"https://cdn20.patchcdn.com/users/22859473/20171001/011244/styles/raw/public/processed_images/1506877964-1506877964-3039.jpg",
"https://pbs.twimg.com/media/DN2UvNjU8AAR6xP.jpg",
"http://thehill.com/sites/default/files/styles/thumb_small_article/public/blogs/trumpdonaldgolf12102015getty.jpg"
]
IMAGES = [Image.from_url_with_cache(i).crop_to_aspect(3,2, align=(0.5,0.65)) for i in IMAGE_URLS]

def shape(*args, **kwargs):
    return Ellipse(*args, **kwargs)
    
def bgfn(d, w, h, sightings=None):
    base = Image.new("RGBA", (w,h), "#ffffcc" if any(d in v for v in ABROAD) else "white")
    if not sightings:
        sightings = list(df["Sighted?"][df["Golf Date"] == d])
    if sightings:
        mark = MaskIntersection(..., INBG["Yes"], masks=(shape(35), shape(31, invert=True).pad(2, "black")))
        topsighting = next(x for x in ORDER if x in sightings)
        if topsighting in INBG: mark = shape(35, INBG[topsighting]).place(mark)
        base = base.place(mark)
    elif d == INAUGURATION:
        base = base.place(shape(35, "#a50f15"))
    return base
    
def labelfn(d):
    fg = "black" 
    sightings = list(df["Sighted?"][df["Golf Date"] == d])
    if d <= INAUGURATION:
        fg = "white" if d == INAUGURATION else "grey"
    elif sightings:
        topsighting = next(x for x in ORDER if x in sightings)
        if topsighting in INFG: fg = INFG[topsighting]
    return Image.from_text(d.date_format("{D}"), arial(16, italics=d<INAUGURATION), fg, padding=(0,0,2,0))

month_imgs = [month_chart(Date((2017,m,1)), day_start=1, day_bg=bgfn, day_label=labelfn, month_image=IMAGES[m-1], month_label="{M}", month_bg="#E0E0E0") for m in range(1,13)]
#month_imgs = [month_chart(Date((1438+(m//12),m%12 + 12*int(m==12),1), calendar=islamic), day_start=0, day_bg=bgfn, day_label=labelfn, month_image=IMAGES[(m-4)], month_label="{M}", month_bg="#E0E0E0") for m in range(4,4+12)]
#month_imgs = [month_chart(Date((5777+(m//12),m%12 + 12*int(m==12),1), calendar=hebrew), day_start=0, day_bg=bgfn, day_label=labelfn, month_image=IMAGES[(m-4)], month_label="{M}", month_bg="#E0E0E0") for m in range(4,4+12)]
months = Image.from_array(list(generate_batches(month_imgs, 4)), padding=10, bg="white", yalign=0)

key_info = [
[bgfn(INAUGURATION, 42, 40), "Inauguration"],
[Rectangle((40,40), "#ffffcc").pad(1, "black").pad((5,0), 0), "Abroad"],
[bgfn(..., 42, 40, ["Yes"]), "Played golf"],
[bgfn(..., 42, 40, ["Likely"]), "Probably played golf"],
[bgfn(..., 42, 40, ["Maybe"]), "Possibly played golf"],
[bgfn(..., 42, 40, ["Probably Not"]), "Visited golf club but probably didn't play"]]
key = Image.from_row([Image.from_row([k, Image.from_text(v, arial(16))]) for k,v in key_info], padding=(5,0))
key = Image.from_row([Image.from_text("Source: http://trumpgolfcount.com/", arial(16, bold=True)), key], padding=(5,0))

title = Image.from_column([
Image.from_text("TRUMP GOLF COUNT: golf club visits since his inauguration", arial(48, bold=True)),
Image.from_text("“Can you believe that,with all of the problems and difficulties facing the U.S., President Obama spent the day playing golf.Worse than Carter” —  @realDonaldTrump, 2014", arial(24, italics=True), max_width=1000, padding=(0,5))])

img = Image.from_column([title, months, key], bg="white", padding=(0,10))
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.convert("RGB").save("output/caltrumpgolf.jpg")

