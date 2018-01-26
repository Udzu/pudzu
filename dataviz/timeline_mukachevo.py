import sys
sys.path.append('..')
from charts import *
from dates import *

df = pd.read_csv("datasets/timeline_mukachevo.csv")

START, END, INTERVAL = 1000, 2000, 250
PHOTOS = ["https://europebetweeneastandwest.files.wordpress.com/2014/06/palanok-castle-atop-lumkova-hill-and-munkacs1.jpg", "https://discover-ukraine.info/uploads/i/i/4ffa895022f9f9.85138117.799.jpg"]
COLORS = { 'h': VegaPalette10.GREEN,
           'g': VegaPalette10.GREY,
           'w': VegaPalette10.BLUE,
           'e': VegaPalette10.ORANGE,
           'o': VegaPalette10.RED }

# timeline

def stripes(colors):
    return Stripe(10, *((colors*2)[:2]), p=0.6)
    
def colorfn(d, w, h):
    return Image.from_pattern(stripes([COLORS[t] for t in d['type']]), (w, h))

def labelfn(d, w):
    s = d['period'].replace("\\n", "\n")
    if "Kingdom of Hungary" in d['period'] and w < 200: s = "KoH"
    if "Grand" in d['period'] and w < 200: s = "(Grand) Principality\nof Transylvania"
    return Image.from_text(s, arial(10), "white", align="center", padding=2)
    
ilabels = {(TimeChartLabelPosition.ABOVE, TimeChartLabelPosition.INSIDE, TimeChartLabelPosition.BELOW): labelfn,
           TimeChartLabelPosition.ABOVE: lambda: " ", TimeChartLabelPosition.BELOW: lambda: " "}
data = [df.filter_rows("start<{} and end>{}".format(start+INTERVAL, start)).update_columns(start=lambda v: v-start, end=lambda v: v-start) for start in range(START, END, INTERVAL)]
llabels = ["AD {}".format(start) for start in range(START, END, INTERVAL)]

chart = time_chart(800, 40, data, "start", "end", colorfn, label_font=arial(10), interval_label_key=ilabels, 
                   xmin=0, xmax=INTERVAL, grid_font=arial(10), grid_labels=lambda v: "+{}".format(v), grid_interval=50, labels_left=llabels).pad(2, bg="black")

# legend

footer_text =  ["ruling power: ",
 Rectangle(20, COLORS['h']), " hungarian  ", 
 Rectangle(20, COLORS['e']), " east slavic  ",
 Rectangle(20, COLORS['w']), " west slavic  ",
 Rectangle(20, COLORS['g']), " germanic  ",
 Rectangle(20, COLORS['o']), " ottoman"
 ]

footer = Image.from_multitext(footer_text, [arial(12, bold=True)] + [arial(12)]*(len(footer_text)-1), "white", img_offset=-5)
chart = Image.from_column([chart, footer.pad((0,10))], bg="black")

# photos

images = Image.from_column([Image.from_url_with_cache(u).crop_to_aspect(320,200).resize_fixed_aspect(height=180) for u in PHOTOS])

# demographics

demographics = [ { "jews": 48, "ukrainians": 24, "hungarians": 22 },
                 { "ukrainians": 77.1, "russians": 9, "hungarians": 8.5, "jews": 1.1 } ]
demographics = [ { **d, 'other': 100 - sum(d.values()) } for d in demographics ]
dem = pd.DataFrame(demographics, index=["1922", "2001"]).fillna(0)
dem = dem[["jews", "ukrainians", "russians", "hungarians", "other"]]
dem_palette = { "jews": VegaPalette10.BLUE, 'hungarians': VegaPalette10.GREEN, 'ukrainians': VegaPalette10.ORANGE, 'other': VegaPalette10.GREY, 'russians': VegaPalette10.RED }

dembar = bar_chart(dem, 40, 300, BarChartType.STACKED_PERCENTAGE, fg="white", bg="black", clabels=None, label_font=arial(12), grid_interval=0.2, colors=lambda c: dem_palette[dem.columns[c]], spacing=5)
demleg = generate_legend([dem_palette[c] for c in dem.columns], [c.title() for c in dem.columns], 15, fg="white", bg="black", border=False, header="Demographics")
demtitle=Image.from_text("Munkács's Jewish period", arial(16, bold=True), "white")
demimg = Image.from_column([demtitle, Image.from_row([dembar, demleg], padding=5, yalign=0)], padding=5, bg="black")

chart = Image.from_row([chart, images, demimg], bg="black", padding=5)

title = Image.from_column([
 Image.from_text("5 countries in 50 years: a political chronology of Mukachevo".upper(), arial(36, bold=True), "white"),
 Image.from_markup('An old man says he was born in Austria-Hungary, went to school in Czechoslovakia, married in Hungary, worked most of his life in the Soviet Union and now lives in the Ukraine. "//Traveled a lot, then?//" asks his interviewer. "//No, I never moved from Mukachevo.//"', partial(arial, 16), max_width=950, fg="white")], padding=5)
    
img = Image.from_column([title.pad((0,10)), chart], bg="black")
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="white", bg="black", padding=3).pad((1,1,0,0), "white"), align=1, padding=(5,10), copy=False)
img.save("output/timeline_mukachevo.png")
