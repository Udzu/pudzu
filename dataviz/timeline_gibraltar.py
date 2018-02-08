import sys
sys.path.append('..')
from charts import *
from dates import *
from collections import defaultdict

df = pd.read_csv("datasets/timeline_gibraltar.csv")
df_events = pd.read_csv("datasets/timeline_gibraltar_events.csv")

START, END, INTERVAL = 1000, 2000, 250
PHOTOS = ["http://www.kindredgroup.com/wp-content/uploads/2016/11/gibralta.jpg", "http://www.visitgibraltar.gi/images/site_images/HcZOv_gugu.jpg"]
COLORS = { 'm': VegaPalette10.GREEN,
           's': VegaPalette10.ORANGE,
           'u': VegaPalette10.RED }
ICONS = { 's': MaskUnion(..., "white", masks=Image.open("icons/trebuchet.png").to_rgba().resize_fixed_aspect(width=15)) }

# timeline

def colorfn(d, w, h):
    return COLORS[d['type']]
    
def labelfn(d, w):
    s = d['period'].replace("\\n", "\n")
    if "Medina" in d['period'] and w < 20: return None
    if "Medina" in d['period'] and w < 50: s = "MS"
    if "Granada" in d['period'] and w < 50: s = "Gra'da"
    return Image.from_text(s, arial(10), "white", align="center", padding=2, beard_line=True)
    
def eventfn(d):
    return ICONS[d['type']].pad(2,0)
    
ilabels = {(TimeChartLabelPosition.BELOW, TimeChartLabelPosition.INSIDE): labelfn,
           TimeChartLabelPosition.ABOVE: lambda: " ", TimeChartLabelPosition.BELOW: lambda: " "}
llabels = ["AD {}".format(start) for start in range(START, END, INTERVAL)]

data = [df.filter_rows("start<{} and end>{}".format(start+INTERVAL, start)).update_columns(start=lambda v: v-start, end=lambda v: v-start) for start in range(START, END, INTERVAL)]
event_data = [df_events.filter_rows("time<{} and time>={}".format(time+INTERVAL, time)).update_columns(time=lambda v: v-time) for time in range(START, END, INTERVAL)]

chart = time_chart(800, 40, data, "start", "end", colorfn, label_font=arial(10), interval_label_key=ilabels,
                   event_data=event_data, event_label_key={TimeChartLabelPosition.ABOVE: eventfn},
                   xmin=0, xmax=INTERVAL, grid_font=arial(10), grid_labels=lambda v: "+{}".format(v), grid_interval=50, labels_left=llabels).pad(2, bg="black")

# legend

footer_text =  ["control:   ",
 Rectangle(20, COLORS['m']), " Muslim   ", 
 Rectangle(20, COLORS['s']), " Spanish   ",
 Rectangle(20, COLORS['u']), " British   ",
 "     ",
 ICONS['s'].pad((0,0,0,3),0), " under siege"
 ]

footer = Image.from_multitext(footer_text, [arial(12, bold=True)] + [arial(12)]*(len(footer_text)-1), "white", img_offset=-5)
chart = Image.from_column([chart, footer.pad((0,10), 0)], bg="black")

# photos

images = Image.from_column([Image.from_url_with_cache(u).crop_to_aspect(320,200).resize_fixed_aspect(height=180) for u in PHOTOS])

# bar chart

totals = defaultdict(lambda: 0)
for _,d in df.iterrows(): totals[d['type']] += d['end'] - d['start']
tot_data = pd.DataFrame([ totals[c] for c in 'msu' ], index=["Muslim", "Spanish", "British"])
tot_palette = [COLORS[c] for c in 'msu']
tot_bar = bar_chart(tot_data, 40, 300, fg="white", bg="black", label_font=arial(12), clabels=BarChartLabelPosition.INSIDE, grid_interval=100,
                    colors=lambda c,r: tot_palette[r], spacing=5)
tot_title = Image.from_text("# years of control", arial(16, bold=True), "white")
tot_img = Image.from_column([tot_title, tot_bar], padding=5, bg="black")

chart = Image.from_row([chart, images, tot_img], bg="black", padding=5)

title = Image.from_text("The rock + under siege: a political timeline of Gibraltar".upper(), arial(36, bold=True), "white")
    
img = Image.from_column([title.pad((0,10), 0), chart], bg="black")
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="white", bg="black", padding=3).pad((1,1,0,0), "white"), align=1, padding=(5,5), copy=False)
img.save("output/timeline_gibraltar.png")
