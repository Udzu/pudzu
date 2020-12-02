from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from scipy.stats.mstats import gmean

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')
df = pd.read_csv("datasets/eudisproportion.csv").set_index("country").fillna("n")
df["index123"] = gmean([df.index1, df.index2, df.index3]) / 100
df = df.sort_values("index123", ascending=True)

ylabel = Image.from_text("Gallagher disproprtionality index", sans(24), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)


def rlabel(r):
    return Image.from_column([
Image.from_url_with_cache(atlas.flag[df.index[r].rstrip("*")]).to_rgba().resize((80,50)).pad(1, "grey").pad((0,5), "white"),
Image.from_text(df.index[r], sans(16, bold=True), "black", align="center", padding=1),
Image.from_text(f"{df.year1[r]}\n{df.year2[r]}\n{df.year3[r]}", sans(14, italics=True), "black", align="center", padding=1),
])

def clabel(c,r,v): return Image.from_text("{:.1%}".format(v), sans(18, bold=False), "white") if v > 0 else None
def clabel_overflow(c,r,v): return None if v > 0 else "0%"

def colfn(c,r,v): return {"y": VegaPalette10.RED, "n": "#003399", "b": VegaPalette10.PURPLE}[df.g7[r]]
    
chart = bar_chart(df[['index123']], 90, 1000, 
    spacing=5, ymax=0.20, colors=colfn, rlabels=rlabel, clabels={ BarChartLabelPosition.INSIDE : clabel, BarChartLabelPosition.OUTSIDE : clabel_overflow},
    grid_interval=0.01, label_interval=0.01, label_font=sans(14, bold=False), ylabels="{:.0%}", ylabel=ylabel)


legend = generate_legend(["#003399", VegaPalette10.PURPLE, VegaPalette10.RED ], ["EU", "EU & G7", "G7" ], box_sizes=40, header="Member of...", font_family=partial(sans, 24))
chart = chart.place(legend, align=(0,0), padding=(130,30))

title = Image.from_column([
Image.from_text("electoral system disproportionality in the EU and G7".upper(), sans(80, bold=True), padding=(5,10,5,2)),
Image.from_text("measured using the Gallagher index, based on the difference between votes received and seats allotted, averaged over the last 3 elections", sans(40, bold=False), padding=(5,2,5,10))], bg="white")

footer = Image.from_markup("Data taken from [[https:/\/www.tcd.ie/Political_Science/people/michael_gallagher/ElSystems/Docts/ElectionIndices.pdf]] (last updated October 2019)                 * House elections", partial(sans, 32), "black", padding=(0,40,0,20))

img = Image.from_column([title, chart, footer], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 18), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eudisproportion.png")


"""
Fair elections? Electoral system disproportionality in the EU and G7 [OC]

The [Gallagher index](https://en.wikipedia.org/wiki/Gallagher_index) "measures an electoral system's relative disproportionality between votes received and seats allotted in a legislature". It is computed by taking the square root of half the sum of the squares of the difference between percent of votes and percent of seats for each of the political parties. This gives an index whose value ranges from 0% (perfectly proportional) and 100% (totally disproportional). The chart shows the value of the index for EU and G7 countries, averaged over the last 3 years using the geometric mean.

The data is taken from [Michael Gallagher's page](https://www.tcd.ie/Political_Science/people/michael_gallagher/ElSystems/Docts/ElectionIndices.pdf) which was last updated at the end of 2019. Two values that I've found since then are [11.7 for the 2019 UK elections](https://www.instituteforgovernment.org.uk/explainers/electoral-systems-uk), and a historically low [2.22 for the 2020 Irish elections](https://www.tcd.ie/Political_Science/people/michael_gallagher/Election2020.php). These have not been included in the chart in case their calculation methodology differs.

The highest value in the dataset is 21.12 for [France's 2017 elections](https://en.wikipedia.org/wiki/2017_French_legislative_election), where En Marche! received 28% of the (first round) votes and 53% of the seats, while the populist left and right (La France insoumise and FN) received 24% of the vote and 4.3% of the seats.

The lowest value in the dataset is 0.63 for [Sweden's 2018 elections](https://en.wikipedia.org/wiki/2018_Swedish_general_election), where the Social Democrats got 28.26% of the vote and 28.65% of the seats, the Moderates got 19.84% of the vote and 20.06% of the seats, and the Democrats got 17.53% of the vote and 17.77% of the seats.

The chart was generated using Python and [pudzu-charts](https://github.com/Udzu/pudzu-packages).
"""


