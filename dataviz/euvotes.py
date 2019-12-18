from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/euvotes.csv").set_index('country')

palette = tmap(RGBA, sns.cubehelix_palette(11, start=0.2, rot=-0.75))
ranges = [20000000,10000000,5000000,2000000,1000000,500000,200000,100000,0]

def votecolfn(n):
    return palette[8 - next(i for i,x in enumerate(ranges) if n >= x)]

def colorfn(c):
    if c not in df.index:
        return "white" if c in ['Sea', 'Borders'] else "grey"
    return votecolfn(int(df.loc[c].votes))
    
def labelfn(c):
    if c not in df.index: return None
    dfc = df.loc[c]
    label = "{name} '{year}\n({votes:.2g}M)".format(name=dfc.leader.split(" ")[-1], year=dfc.year[2:], votes=int(dfc.votes) / 1000000)
    return Image.from_text(label, arial(14, bold=True), align="center", padding=2)

map = map_chart("maps/Europe.png", colorfn, labelfn)

# legend
def box(c): 
    return Image.new("RGBA", (30, 30), c).place(Image.from_text("", arial(16, bold=True), "black", bg=c))

vote_arr = Image.from_array([
[box(votecolfn(n)), Image.from_text("<0.1M" if n < 100000 else ">{:.2g}M".format(n/1000000), arial(16), padding=(10,0))] for n in ranges
], bg="white", xalign=0)
vote_leg = Image.from_column([Image.from_text("# votes", arial(16, bold=True)), vote_arr], bg="white", xalign=0, padding=(0,5))
note_leg = Image.from_text("Multi-party national elections for executive head or party.", arial(16), max_width=100, bg="white", padding=(0,2))

legend = Image.from_column([vote_leg, note_leg], bg="white", xalign=0, padding=5).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("EUROPEAN POPULAR VOTE RECORDS", arial(48, bold=True)),
Image.from_text("candidate or party with the highest absolute popular vote", arial(36))],
bg="white")
img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euvotes.png")
