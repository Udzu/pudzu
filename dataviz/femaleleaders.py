import sys
sys.path.append('..')
from charts import *
from records import *
import seaborn as sns
import dateparser

# mappy bit
rs = RecordCSV.load_file("femaleleaders.csv")
rs = update_records(rs, update_if('hosdate:exists or hogdate:exists', update_with(date=lambda d: min(d.get('hosdate',2017), d.get('hogdate',2017)))))
rd = records_to_dict(rs, "country")

hog = ImageColor.from_floats(sns.color_palette("Blues", 6))
hos = ImageColor.from_floats(sns.light_palette((0.7,0.2,0.1)))
both = ImageColor.from_floats(sns.color_palette("Purples", 6))

def stripe(c1, c2):
    return Image.from_column([Image.new("RGBA", (100,4), c1), Image.new("RGBA", (100,4), c2)])

def colorfn(c):
    if c not in rd: return None if c == 'Sea' else "grey"
    d = rd.get(c, {})
    if 'date' not in d : return stripe("grey", hos[-1])
    y = d.get('date') // 10 - 196
    if 'hog' not in d: return hos[y]
    elif 'hos' not in d: return hog[y]
    elif 'hosdate' not in d: return stripe(hog[y], both[y])
    else: return both[y]
    
chart = map_chart("maps/Europe.png", colorfn, ignoring_exceptions(lambda c: str(rd[c]["date"])), label_font=arial(16, bold=True))

box_size = 30
font_size = 16

def box(c): return Image.new("RGBA", (box_size,box_size), c)
def stripebox(c1, c2): return Image.from_pattern(stripe(c1, c2), (box_size,box_size))

type_boxes = ((box(hog[-1]), "premier"), (box(hos[-2]), "president"), (stripebox(hos[-2], "grey"), "queen"), (box(both[-2]), "premier & president"), (stripebox(hog[-2], both[-2]), "premier & queen"), (box("grey"), "none (so far)"))
type_arr = Image.from_array([[b, Image.from_text(label, arial(font_size), padding=(10,0))] for b,label in type_boxes], xalign=0, bg="white")
type_leg = Image.from_column([Image.from_text("Office held", arial(font_size, bold=True)), type_arr], bg="white", xalign=0, padding=(0,5))

year_arr = Image.from_array([[box(hog[i]), box(hos[i]), box(both[i]), Image.from_text("{}0s".format(i+196), arial(font_size), padding=(10,0))] for i in range(1,6)], bg="white")
year_leg = Image.from_column([Image.from_text("First elected", arial(font_size, bold=True)), year_arr], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([type_leg, year_leg], bg="white", xalign=0, padding=5).pad(1, "black")
chart = chart.place(legend, align=(1,0), padding=10)

# griddy bit
trs = RecordCSV.load_file("femaleleaders_timeline.csv")
tdata = pd.DataFrame([trs[i:i+12] for i in range(0,36,12)])
atlas = records_to_dict(RecordCSV.load_file("countries.csv"), "tld")
atlas[".kv"] = { "flag" : "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Kosovo.svg/1024px-Flag_of_Kosovo.svg.png" }
atlas[".yu"] = { "flag" : "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Flag_of_SFR_Yugoslavia.svg/1000px-Flag_of_SFR_Yugoslavia.svg.png" }

def process(img, d):
    return Image.from_column([
      img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=100),
      Image.from_text(d['name'].split(" ")[-1], arial(10, bold=True), fg="black", bg="white"),
      Image.from_row([Image.from_url_with_cache(atlas[".{}".format(d['country'])]['flag']).resize_fixed_aspect(width=10),
                      Image.from_text(str(d['year']), arial(10, bold=True), fg="black", bg="white")], bg="white", padding=3, yalign=1)
      ], bg="white")
    
grid = grid_chart(tdata, lambda d: d and d["url"], process, bg="white", padding=1)

# put it all together
title = Image.from_text("40 Years of Women Leaders in Europe".upper(), arial(56, bold=True), "black", "white", padding=(0,20))
img = Image.from_column([title, chart, grid], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("femaleleaders.png")

