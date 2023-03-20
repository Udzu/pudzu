import seaborn as sns
from matplotlib import pyplot as plt, rcParams
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from pudzu.charts import *
from pudzu.sandbox.bamboo import *

for rel in ["muslim", "jew"]:

    df = pd.read_csv("datasets/pewminorities.csv").set_index("country")
    df[f"{rel}_pc"] = df[f"{rel}_pop"] / df["total_pop"]
    df = df.sort_values(f"{rel}_neg", ascending=False)

    flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']

    def make_flag(country):
        icon = Image.from_url_with_cache(flags[country]).to_rgba().resize((60,40)).pad(1, "black")
        flag = icon
        flag.save(f"cache/icons/{country}.png")

    for c in df.index: make_flag(c)

    def get_flag(country):
        im = plt.imread(f"cache/icons/{country}.png")
        return OffsetImage(im, zoom=0.5)

    rcParams['figure.figsize'] = 9,6
    g = sns.scatterplot(data=df, x=f"{rel}_neg", y=f"{rel}_pc")
    g.set(yscale="log", ylim=(None, 1), xlim=(0,100))

    def maybe_int(x): return int(x) if x == int(x) else x
    g.set_yticklabels(["{}%".format(maybe_int(y*100)) for y in g.get_yticks()])
    g.set_xticklabels(["{}%".format(maybe_int(x)) for x in g.get_xticks()])
    g.set_xlabel("% of population with negative views of {}".format("Muslims" if rel=="muslim" else "Jews"))
    g.set_ylabel("% of population that is {}".format("Muslim" if rel=="muslim" else "Jewish"))
    g.grid()

    for c, d in df.iterrows():
        ab = AnnotationBbox(get_flag(c), (d[f"{rel}_neg"], d[f"{rel}_pc"]), frameon=False)
        g.add_artist(ab)

    plt.savefig(f"output/pewminorities_{rel}.png", dpi='figure')
    plt.close()

graphs = Image.from_row([Image.open(f"output/pewminorities_{rel}.png").trim((30 if rel=="jew" else 0,20,30 if rel=="muslim" else 0,0)) for rel in ["muslim", "jew"]])

title = Image.from_text("European attitudes towards Muslims and Jews".upper()+"\n(a.k.a. absence doesn't make the heart grow fonder)", sans(48, bold=True), align="center", padding=(0,20,0,0))
subtitle = Image.from_markup("//Source//: [[https:\//www.pewresearch.org/global/2019/10/14/minority-groups/]] (and Wikipedia for population figures).", partial(sans, 20), padding=10)

img = Image.from_column([title, subtitle, graphs], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/pewminorities.png")
