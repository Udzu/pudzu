from pudzu.charts import *
from pudzu.sandbox.bamboo import *

arial = sans

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country")
df = pd.read_csv("datasets/g7diedinoffice.csv").set_index("country")
df["fatality"] = (df.natural + df.homicide + df.suicide) / df.years * 100
df["natural_pc"] = df.natural / df.years * 100
df["homicide_pc"] = df.homicide / df.years * 100
df["suicide_pc"] = df.suicide / df.years * 100

df = df.sort_values("fatality", ascending=False)

H=750
W=100
S=6

DIO = [
["aTakashi 1921", "Tomosaburō 1923", "Takaaki 1924", "aTsuyoshi 1932", "Ōhira 1980"],
["Harrison 1841", "Taylor 1850", "aLincoln 1865", "aGarfield 1881", "aMcKinley 1901", "Harding 1923", "Roosevelt 1945", "aKennedy 1963"],
["aCarnot 1894", "Faure 1899", "aDoumer 1932", "Pompidou 1974"],
["Wilmington 1743", "Pelham 1754", "Rockingham 1782", "Pitt 1806", "aPerceval 1812", "Canning 1827", "Palmerston 1865"],
["sHitler 1945", "sGoebbels 1945"],
["Macdonald 1891", "Thompson 1894"],
["Benso 1861", "Depretis 1887"]
]

def rlabel(r):
    return Image.from_column([
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((W,round(W*0.6))).trim(1).pad(1, "grey"),
        Image.from_text(f"{df.years[r]} years", arial(12, bold=True)),
        Image.from_text(f"{df.total[r]+1} {df.job[r]}", arial(12, bold=True)),
        *[Image.from_text(s[1:] if s[0] in "as" else s, arial(12), fg=VegaPalette10.RED if s[0]=="a" else VegaPalette10.ORANGE if s[0]=="s" else VegaPalette10.BLUE) for s in DIO[r]],
    ], bg="white", padding=(0,2))


chart = bar_chart(df[["homicide_pc", "suicide_pc", "natural_pc"]], W, H, type=BarChartType.STACKED, spacing=S, label_font=arial(14),
    colors=[VegaPalette10.RED, VegaPalette10.ORANGE, VegaPalette10.BLUE],
    clabels=lambda c,r,v: Image.from_text(str([df.homicide, df.suicide, df.natural][c][r]), arial(16)),
    rlabels=rlabel, grid_interval=0.5, label_interval=1, ylabels="{}%",
    legend_position=(1,0), legend_fonts=papply(arial, 14), legend_box_sizes=30, legend_args={"header": "Cause of death".upper(), "labels": ["Assassinated", "Suicide", "Natural causes"]},
    ylabel=Image.from_text("annual chance of dying in office", arial(16), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90))
    
title = Image.from_column([
    Image.from_text("Fatality rates for G7 national leaders".upper(), arial(36, bold=True), padding=5),
    Image.from_text("annual chance of dying in office, based on past deaths", arial(24, italics=True), padding=5),
    ], bg="white", padding=2)
#footer = Image.from_markup("data is from a variety of sources and should be viewed as approximate; cities marked with * are second-largest cities that had a significantly larger Jewish population than the largest one", partial(arial, 14))

img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)
img.save("output/g7diedinoffice.png")
