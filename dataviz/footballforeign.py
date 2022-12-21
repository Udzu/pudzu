from PIL.Image import Transpose
from pudzu.charts import *

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country').flag
flags["Scotland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1920px-Flag_of_Scotland.svg.png"
flags["England"] = "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1920px-Flag_of_England.svg.png"
flags["USSR"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/1024px-Flag_of_the_Soviet_Union.svg.png"
flags["Czechoslovakia"] = flags["Czech Republic"]
flags["Yugoslavia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Flag_of_Yugoslavia_%281946-1992%29.svg/1024px-Flag_of_Yugoslavia_%281946-1992%29.svg.png"
flags["Zaire"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Flag_of_Zaire_%281971%E2%80%931997%29.svg/1280px-Flag_of_Zaire_%281971%E2%80%931997%29.svg.png"

df = pd.read_csv("datasets/footballforeign.csv").set_index("year")
df["num_foreign"] = df.foreign.apply(lambda s: 0 if non(s) else len(s.split("|")))
df["num_local"] = df["total"] - df["num_foreign"]
df["pc_foreign"] = df["num_foreign"] / df["total"]

counts = df[["num_foreign", "num_local"]]

def rlabel(r):
     year = Image.from_text(str(counts.index[r]), arial(28, bold=True)).pad((0,0,0,10), None)
     b, ct = df.best[counts.index[r]].split(":")
     b = {"quarter-finals": "QF", "semi-finals": "SF", "group stage": "GS", "round of 16": "R16", "final 4": "F4", "final": "F"}[b]
     best = Image.from_text(f"{b}", arial(20)).pad((0,0,0,5), None)
     cs = [Image.from_url_with_cache(flags[c]).to_rgba().resize((20 if c=="Switzerland" else 30,20)).pad(1, "grey") for c in ct.split("|")]
     return Image.from_column([year, best, *cs], padding=(0,2))

def pclabel(c,r,v,w,h):
     if c == 1:
          pc = df.pc_foreign[counts.index[r]]
          txt = Image.from_text(f"{pc:.0%}", arial(24))
          return Image.new("RGBA", (w,h)).place(txt, align=(0.5,1), padding=10)
     else:
          col = []
          for f in sorted(df.foreign[counts.index[r]].split("|")):
              a,b = f.split(":")
              fa = Image.from_url_with_cache(flags[a]).to_rgba().resize((20 if a == "Switzerland" else 30, 20)).pad((5*(a == "Switzerland"),0), None)
              fb = Image.from_url_with_cache(flags[b]).to_rgba().resize((13 if b == "Switzerland" else 20, 13)).pad((3*(b == "Switzerland"),0), None)
              label = Image.from_row([fa, Image.from_text(" < ", arial(16)), fb])
              col.append(Image.new("RGBA", (w, round(h/df.num_foreign[counts.index[r]]))).place(label))
          return Image.from_column(col)

chart = bar_chart(counts, 100, 1620, type=BarChartType.STACKED, colors=[VegaPalette10.BLUE, VegaPalette10.BLUE.brighten(0.5)],
     spacing=5, ymax=36, grid_interval=2, label_interval=4, label_font=arial(16, bold=False),
     rlabels = { BarChartLabelPosition.BELOW: rlabel  },
     ylabel=Image.from_text("# of teams", arial(32)).transpose(Transpose.ROTATE_90).pad(10, None),
     clabels={ BarChartLabelPosition.INSIDE : pclabel },
     legend_fonts=partial(arial, 32), legend_position=(0.04, 0.04), legend_box_sizes=(60,60),
     legend_args={'header': "head coach".upper(),
                  'labels': ['foreign (left flag = team, right flag = coach)', 'native'],
                  'footer': "Flags below each column show best performing foreign-coached team(s). "
                  "The countries that provided the most foreign coaches overall were Brazil (14), France (14), Argentina (13) and England (12). "
                  "The ones that used the most were Cameroon (7), Switzerland (7) and Mexico (6).",
                  'max_width': 700,
                }
)

TITLE = "Foreign coaches at the FIFA World Cup"
SUBTITLE = "foreign coaches make up around 25% of historic participants, though one is yet to win the competition"

title = Image.from_text(TITLE.upper(), arial(80, bold=True)).pad(10, "white")
subtitle = Image.from_text(SUBTITLE, arial(38, italics=True)).pad(10, "white")

img = Image.from_column([title, subtitle, chart.pad(10, "white")], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/footballforeign.png")

#As an aside, even though foreign-coached teams have never won the World Cup (reaching the final twice), they have won every other major men's competition:
#the Euros, the Copa America, Africa Cup of Nations
