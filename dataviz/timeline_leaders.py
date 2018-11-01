from pudzu.charts import *
from pudzu.dates import *
import dateparser

def dateparse(s): return dateparser.parse(s).date()

START = dateparse('1 January 1750') # dateparse('14 July 1789')
END = datetime.date.today()
COLORS = { "pm": VegaPalette10.RED, "president": VegaPalette10.BLUE, "monarch": VegaPalette10.PURPLE, "secretary": VegaPalette10.GREEN, "zpower": VegaPalette10.LIGHTGREEN }
DESCRIPTIONS = { "pm": "prime minister/chancellor", "president": "president", "monarch": "monarch/pope", "secretary": "general secretary", "zpower": "period in power" }
    
df = pd.read_csv("datasets/timeline_leaders.csv").split_columns(("starts", "ends"), "|").fillna(str(END))
df = df.update_columns(birth=dateparse, death=dateparse, starts=partial(tmap, dateparse), ends=partial(tmap, dateparse))
df = df.sort_values(["country", "birth"])
groups = df.groupby("country")
data = [groups.get_group(g).reset_index(drop=True) for g in sorted(groups.groups)]
data = [df.assign(n=df.index) for df in data]

# hacky but hey
def alternate(d, img):
    return img.pad((0, d.n%2*(img.height+2), 0, (d.n+1)%2*(img.height+2)), 0)
def colorfn(d, w, h): 
    c = COLORS[d.type]
    img = Rectangle((w,h//2-1), c)
    for start, end in zip(d.starts, d.ends):
        x = round(w * (start - d.birth) / (d.death - d.birth))
        len = round(w * (end - start) /  (d.death - d.birth))
        img = img.overlay(Rectangle((len,h//2-1), COLORS["zpower"]), (x, 0))
    return alternate(d, img)
def labelfn(d, w, h):
    return alternate(d, Rectangle((w-4,h//2-1), RGBA(0)).place(Image.from_text(d.leader, arial(16), "white"))).trim((2,1))
chart = time_chart(1200, 50, data, "birth", "death", colorfn, labelfn, labels_left=sorted(groups.groups), labels_right=[" {} steps".format(len(df)) for df in data], label_font=arial(16), interval_border=0, xmin=START, xmax=END, grid_interval=DateInterval(years=50), grid_font=arial(16), grid_labels=lambda v: str(v.year), timeline_spacing=15)

title = Image.from_column([
    Image.from_text("from 1750 to the present day via national leaders".upper(), arial(36, bold=True), fg="white"),
    Image.from_markup("aka: //a pointless excercise in n degrees-of-separation//", partial(arial, 32), fg="white")])
labels = [Image.from_row([Rectangle(40, COLORS[t]), Image.from_text(DESCRIPTIONS[t], arial(16), fg="white")], padding=3) for t in sorted(COLORS)]
legend = Image.from_column([
    Image.from_row([Image.from_text("Position:", arial(16, bold=True), fg="white"), *labels], bg="black", padding=5),
    Image.from_markup("* //Loubet was also President in 1899-1906 but this was a ceremonial post in the Third Republic// \\** //Stalin and Gorbachev were also briefly premier and president//", partial(arial, 14), fg="white")
], padding=(0,2))

img = Image.from_column([title, chart, legend], bg="black", padding=(0,20))
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="white", bg="black", padding=3).pad((1,1,0,0), "white"), align=1, padding=(5,10), copy=False)
img.save("output/timeline_leaders.png")
