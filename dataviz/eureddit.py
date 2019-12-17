from pudzu.charts import *
from pudzu.experimental.bamboo import *

FONT = verdana

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country').flag
flags["Sealand (current post)"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Flag_of_Sealand.svg/1024px-Flag_of_Sealand.svg.png"
df = pd.read_csv("datasets/eureddit.csv").set_index("country")
df["controversy"] = df["comments"] / df["upvotes"]

def flag(f): return Image.from_url_with_cache(f).to_rgba().resize((80,60)).trim(1).pad(1, "grey")
def clabel(c,r,v): return Image.from_text(str(abs(v)), FONT(16), "white")

upvotes = bar_chart(df[['upvotes']], 60, 600, ymax=500, grid_interval=50, label_interval=100, clabels={BarChartLabelPosition.INSIDE: clabel}, label_font=FONT(16), horizontal=True, spacing=1, rlabels=lambda r: flag(flags[df.index[r]]), ylabel=Image.from_text("number of votes", FONT(24), padding=2), colors=VegaPalette10.ORANGE)
comments = bar_chart(-df[['comments']], 60, 600, ymin=-1500, grid_interval=100, label_interval=500, clabels={BarChartLabelPosition.INSIDE: clabel}, ylabels=lambda v: str(abs(v)), label_font=FONT(16), horizontal=True, spacing=1, ylabel=Image.from_text("number of comments", FONT(24), padding=2), colors=VegaPalette10.BLUE)
chart = Image.from_row([comments, upvotes], yalign=1, bg="white")

def sorted_flags(col): return [flag(flags[c]) for c,_ in df.sort_values(col, ascending=False).iterrows()]
headers = [None] + [Image.from_text(s, FONT(12, bold=True), align="center") for s in ["interest\n(comments)", "popularity\n(votes)", "controversy\n(c/v)"]]
array = [sorted_flags(c) for c in ["comments", "upvotes", "controversy"]]
array = [[Image.from_text("{}. ".format(i+1), FONT(24)) for i in range(len(df))]] + array
array = list(zip(*array))
grid = Image.from_array([headers] + array, padding=1, bg="white", xalign=[1] + [0.5]*(len(headers)-1))
grid = Image.from_column([Image.from_text("sorted by", FONT(24), padding=2), grid], xalign=0.65, bg="white")

missing = pd.read_csv("datasets/eureddit2.csv").set_index("country")
miss = Image.from_column([flag(get_non(flags, c, if_non(d.flag, flags["UK"]))) for c,d in missing.iterrows()], padding=1)
miss = Image.from_column([Image.from_text("still to do?", FONT(24), padding=(0,10,0,2)),
                         Image.from_text("[TRIGGER WARNING]", FONT(16), padding=(0,2,0,5)),
                         miss], bg="white")

combined = Image.from_row([chart, grid, miss], yalign=0, bg="white", padding=50)
title = Image.from_text("/r/europe's \"What Do You Know about ...\" series", FONT(60, bold=True))
subtitle = Image.from_text("weekly sticky posts about European countries, starting January 2017", FONT(48, italics=True))

img = Image.from_column([title, subtitle, combined], padding=5, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eureddit.png")