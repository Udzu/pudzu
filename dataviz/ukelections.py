import sys
sys.path.append('..')
from charts import *
from bamboo import *

# ------------
# UK elections
# ------------

records = pd.read_csv("datasets/ukelections.csv").sort_values("year").filter_rows(lambda d: int(d["year"][:4]) >= 1966)

groups = OrderedDict()
for i in map(str, range(1,4)):
    groups[i] = [{ "year": d["year"], "votes": d["votes"+i], "seats": d["seats"+i], "party": d["party"+i] } for _,d in records.iterrows()]
groups["rest"] = [{ "year": d["year"], "votes": d["votestotal"] - d["votes1"] - d["votes2"] - d["votes3"],
                    "seats": d["seatstotal"] - d["seats1"] - d["seats2"] - d["seats3"], "party": "other" } for _,d in records.iterrows()]
groups["noshow"] = [{ "year": d["year"], "votes": int(d["votestotal"] / (d["turnout"]/100)) - d["votestotal"], "seats": 0, "party": "noshow" } for _,d in records.iterrows()]

vote_data = pd.DataFrame(groups, index=records['year']).applymap(lambda d: d['votes'])
seat_data = pd.DataFrame(groups, index=records['year']).applymap(lambda d: d['seats'])
party_data = pd.DataFrame(groups, index=records['year']).applymap(lambda d: d['party'])

def colorfn(c,r,v):
    return {"L": "#d62728", "C": "#393b79", "LD": "#e7ba52", "LB": "#e7ba52", "SLA": "#e7ba52", "UKIP": "#7b4173", "other": "grey", "noshow": "#bdbdbd"}[party_data[party_data.columns[c]][party_data.index[r]]]
    
def clabelfn(c,r,v):
    seats = seat_data[party_data.columns[c]][party_data.index[r]]
    if c == 4: label = "({:.0%})".format(v / sum(vote_data[xx][party_data.index[r]] for xx in party_data.columns))
    else: label = str(seat_data[party_data.columns[c]][party_data.index[r]])
    return Image.from_text(label, arial(10), bg=colorfn(c,r,v))
    
chart = bar_chart(vote_data, 40, 400, type=BarChartType.STACKED, colors=colorfn,
                  spacing=5, rlabels=arial(12), ylabels=arial(12), clabels=clabelfn,
                  yformat=lambda v: str(v)[0:2]+" million" if v > 0 else "0",
                  grid_interval=10000000, tick_interval=5000000)

def legend_row(label, color):
    return [Image.new("RGBA", (20,15), color), Image.from_text(label, arial(12), "black", bg="white")]
    
legend = Image.from_array([legend_row("Conservative", "#393b79"),
                           legend_row("Labour", "#d62728"),
                           legend_row("Liberal/LibDem/\nSDP-Lib Alliance", "#e7ba52"),
                           legend_row("UKIP", "#7b4173"),
                           legend_row("other parties", "grey"),
                           legend_row("did not vote", "#bdbdbd")
                           ], xalign=(0.5,0), padding=(2,5))
                           
title = Image.from_text("Votes versus seats at UK general elections (1966-2017)", font("arial", 28, bold=True), "black", bg="white").pad((0,0,0,15), bg="white")
text = Image.from_text("Chart highlights the top three parties by popular vote share. The number of seats is printed on each bar.\n\nData is from Wikipedia.", arial(12), "black", bg="white", max_width=140)
legendtext = Image.from_column([legend, text], padding=(0,10), xalign=0)
img = Image.from_row([chart, legendtext], bg="white", yalign=0, padding=(10,0))
img = Image.from_column([title, img], bg="white").pad((0,5), "white")
img.save("output/ukelections.png")
