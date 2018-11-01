from pudzu.charts import *
from pudzu.dates import *

df = pd.read_csv("datasets/timeline_palermo.csv").split_columns("type", "|")

START, END = -1000, 2000
INTERVAL = 500
COLORS = { 
"classical": "#984ea3", 
"italian": "#e41a1c",
"spanish": "#ff7f00",
"french": "#377eb8",
"german": "#999999", 
"semitic": "#4daf4a"
 }
PHOTOS = ["http://cdn-image.travelandleisure.com/sites/default/files/videos/gettyimages-557663623_0.jpg", "https://pbs.twimg.com/media/C3kUcTRWEAEpwXN.jpg"]

def stripes(colors): return Image.from_column([Image.new("RGBA", (100, 4), c) for c in colors])

def labelfn(d, w):
    if "Ostro" in d['period'] and w < 70: return "..."
    if "of Aragon" in d['period'] and w < 50: return "..."
    return d['period'].replace("\\n", "\n")
    
colorfn = lambda d, w, h: Image.from_pattern(stripes([COLORS[t] for t in d['type']]), (w, h))
labeld = {frozenset({TimeChartLabelPosition.ABOVE, TimeChartLabelPosition.INSIDE, TimeChartLabelPosition.BELOW}): labelfn,
          TimeChartLabelPosition.ABOVE: lambda: " ", TimeChartLabelPosition.BELOW: lambda: " "}
data = [df.filter_rows("start<{} and end>{}".format(start+INTERVAL, start)).update_columns(start=lambda v: v-start, end=lambda v: v-start) for start in range(START, END, INTERVAL)]
llabels = ["{} BC".format(-start) if start< 0 else "AD {}".format(start+int(start==0)) for start in range(START, END, INTERVAL)]
chart = time_chart(800, 40, data, "start", "end", colorfn, interval_label_key=labeld, label_font=arial(10), 
                   xmin=0, xmax=INTERVAL, grid_font=arial(10), grid_labels=lambda v: "+{}".format(v), grid_interval=100, labels_left=llabels).pad(2, bg="black")

# # Title, etc

images = Image.from_column([Image.from_url_with_cache(u).crop_to_aspect(320,200).resize((320,200)) for u in PHOTOS], bg="black")

def box(t): return Image.new("RGBA", (20,20), COLORS[t])
def label(s): return Image.from_text(s, arial(12), fg="white", bg="black", padding=(0,0,10,0))

footer = Image.from_row([
    Image.from_text("ruling power: ", arial(12, bold=True), fg="white"),
    box("semitic"), label("Semitic"),
    box("classical"), label("Graeco-Roman"),
    box("german"), label("Germanic"),
    box("french"), label("Gallic"),
    box("spanish"), label("Hispanic"),
    box("italian"), label("Italic")
    ], padding=3, bg="black")
    
chart = Image.from_column([chart, footer.pad((0,10))], bg="black")

title = Image.from_column([
    Image.from_text("Palermo: most conquered city(?)".upper(), arial(36, bold=True), fg="white", bg="black"),
    Image.from_text("a political chronology of Sicily's ancient, oft conquered capital", arial(24), fg="white", bg="black")
    ], bg="black")

img = Image.from_column([title.pad((0,10)), Image.from_row([chart, images], bg="black", padding=5)], bg="black")
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="white", bg="black", padding=3).pad((1,1,0,0), "white"), align=1, padding=(5,10), copy=False)
img.save("output/timeline_palermo.png")
