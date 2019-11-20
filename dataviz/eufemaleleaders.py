from pudzu.charts import *
from pudzu.bamboo import *
import seaborn as sns

# generate map
FONT = verdana

df = pd.read_csv("datasets/eufemaleleaders.csv")
df = df.assign_rows(assign_if='hosdate:exists or hogdate:exists', date=lambda d: min(get_non(d,'hosdate',2018), get_non(d,'hogdate',2018)))
df = df.set_index('country')

hog = tmap(RGBA, sns.color_palette("Blues", 6))
hos = tmap(RGBA, sns.light_palette((0.7,0.2,0.1)))
both = tmap(RGBA, sns.color_palette("Purples", 6))

def stripe(c1, c2):
    return Image.from_column([Image.new("RGBA", (100,4), c1), Image.new("RGBA", (100,4), c2)])

def colorfn(c):
    if c not in df.index: return "white" if c in ['Sea', 'Borders'] else "grey"
    d = df.loc[c]
    if non(df['date'][c]) : return stripe("grey", hos[-1])
    y = int(df['date'][c]) // 10 - 196
    if non(df['hog'][c]): return hos[y]
    elif non(df['hos'][c]): return hog[y]
    elif non(df['hosdate'][c]): return stripe(hog[y], both[y])
    else: return both[y]
    
chart = map_chart("maps/Europe.png", colorfn, ignoring_exceptions(lambda c: str(int(df["date"][c]))), label_font=FONT(16, bold=True))

# generate legend
font_size = 16
box_size = 30
def box(c): return Image.new("RGBA", (box_size,box_size), c)
def stripebox(c1, c2): return Image.from_pattern(stripe(c1, c2), (box_size,box_size))

type_boxes = ((box(hog[-1]), "premier"), (box(hos[-2]), "president"), (stripebox(hos[-2], "grey"), "monarch*"), (box(both[-2]), "premier & president"), (stripebox(hog[-2], both[-2]), "premier & monarch*"), (box("grey"), "none yet"))
type_arr = Image.from_array([[b, Image.from_text(label, FONT(font_size), padding=(10,0))] for b,label in type_boxes], xalign=0, bg="white")
type_leg = Image.from_column([Image.from_text("Office held", FONT(font_size, bold=True)), type_arr], bg="white", xalign=0, padding=(0,5))

year_arr = Image.from_array([[box(hog[i]), box(hos[i]), box(both[i]), Image.from_text("{}0s".format(i+196), FONT(font_size), padding=(10,0))] for i in range(1,6)], bg="white")
year_leg = Image.from_column([Image.from_text("First elected", FONT(font_size, bold=True)), year_arr], bg="white", xalign=0, padding=(0,5))

note_leg = Image.from_text("*last 40 years only", FONT(font_size), bg="white")

legend = Image.from_column([type_leg, note_leg, year_leg], bg="white", xalign=0, padding=5).pad(1, "black")
chart = chart.place(legend, align=(1,0), padding=10)

# generate image grid
df = pd.read_csv("datasets/eufemaleleaders_timeline.csv")
tdata = pd.DataFrame([[df.loc[i+j] for j in range(13) if i + j < len(df)] for i in range(0,39,13)])

flags = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('tld').set_index('tld')['flag']
flags[".kv"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Kosovo.svg/1024px-Flag_of_Kosovo.svg.png"
flags[".yu"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Flag_of_SFR_Yugoslavia.svg/1000px-Flag_of_SFR_Yugoslavia.svg.png"

def process(d):
    if non(d): return None
    return Image.from_column([
      Image.from_url_with_cache(d["url"]).crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=100),
      Image.from_text(d['name'].split(" ")[-1], FONT(10, bold=True), fg="black", bg="white"),
      Image.from_row([Image.from_url_with_cache(flags[".{}".format(d['country'])]).resize((15,9)),
                      Image.from_text(str(d['year']), FONT(10, bold=True), fg="black", bg="white")], bg="white", padding=3, yalign=1)
      ], bg="white")
    
grid = grid_chart(tdata, process, bg="white", padding=1)

# put it all together
title = Image.from_text("40 Years of Women Leaders in Europe".upper(), FONT(52, bold=True), "black", "white", padding=(0,20))
img = Image.from_column([title, chart, grid], bg="white", padding=2)
img.place(Image.from_text("Uri Granta", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eufemaleleaders.png")

