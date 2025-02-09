from matplotlib.offsetbox import AnnotationBbox
from matplotlib.ticker import MultipleLocator, FuncFormatter, NullFormatter
from pudzu.charts import *
from pudzu.dates import *
import dateparser
import matplotlib.pyplot as plt
from pudzu.pillar import sans
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/leadersage.csv")
TODAY = Date()

def dateparse(date: str) -> Date:
    return Date(dateparser.parse(date, locales=["en-GB"]))

def parse(leaders: str) -> pd.DataFrame:
    df = pd.DataFrame([{"leader": a, "dob": dateparse(b), "dos": dateparse(c)} for x in leaders.split(";") for a,b,c in [x.split(":")]])
    df["doe"] = df.dos[1:].reset_index(drop=True)
    df.doe[df.index[-1]] = TODAY
    assert df.dos.min() == Date((2000, 1, 1))
    return df

def youngest(parsed):
    name = parsed.iloc[np.argmin(parsed.dos - parsed.dob)].leader
    age = np.min(parsed.dos - parsed.dob)
    return f"{name}\n({int(age / 365.2425)})", age

def oldest(parsed):
    name = parsed.iloc[np.argmax(parsed.doe - parsed.dob)].leader
    age = np.max(parsed.doe - parsed.dob)
    return f"{name}\n({int(age / 365.2425)})", age

def average(d):
    return sum(((d.dos - d.dob) + (d.doe - d.dob)) * ((d.doe - d.dob) - (d.dos - d.dob) + 1) / 2) / (d.doe.max() - d.dos.min())

df["parsed"] = df.leaders.apply(parse)
df["average"] = df.parsed.apply(average)
df["youngest"] = df.parsed.apply(youngest)
df["oldest"] = df.parsed.apply(oldest)
df["yerr_low"] = df["average"] - df["youngest"].apply(lambda x: x[-1])
df["yerr_high"] = df["oldest"].apply(lambda x: x[-1]) - df["average"]

df = df.sort_values("average")

width, height = 850, 1000
padding = Padding((100, 50, 100, 100))

fig, ax = plt.subplots()
plots = ax.bar(df.country, df.average, yerr=(df["yerr_low"], df["yerr_high"]), capsize=6)
# TODO: annotate extremes

for bar, (name, val) in zip(plots.patches, df["oldest"]):
    ax.annotate(
        name,
        (bar.get_x() + bar.get_width() / 2, val),
        xytext=(0, 16),
        ha='center', va='center', size=9, textcoords='offset points'
    )
for bar, (name, val) in zip(plots.patches, df["youngest"]):
    ax.annotate(
        name,
        (bar.get_x() + bar.get_width() / 2, val),
        xytext=(0, -16),
        ha='center', va='center', size=9, textcoords='offset points'
    )

ax.yaxis.set_major_locator(MultipleLocator(3652.425))
ax.yaxis.set_major_formatter(FuncFormatter(lambda a, b: f"{round(a / 365.2425)}"))
ax.set_ylim(30 * 365.2425, None)
ax.yaxis.grid(color="gray", linewidth=0.5)
ax.set_ylabel("average age (years)")

ax.xaxis.set_major_formatter(NullFormatter())
flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").explode('country').set_index('country').flag
for loc, country in zip(ax.xaxis.get_ticklocs(), df.country):
    label = Image.from_text(country, sans(16), "black", beard_line=True, align="center")
    flag = Image.from_url_with_cache(flags[country]).convert("RGBA")
    flag = flag.resize((round(36*1.7), 36)).trim(1).pad(1, "grey")
    img = Image.from_column([flag, label], padding=(0,2))
    im = img.to_offsetimage()
    abox = AnnotationBbox(
        im,
        (loc, ax.get_ylim()[0]),
        frameon=False,
        xybox=(0, -24),
        boxcoords="offset points",
    )
    ax.add_artist(abox)

fig.subplots_adjust(
    left=padding.l / width, bottom=padding.d / height, right=1 - padding.r / width,
    top=1 - padding.u / height
)

chart = Image.from_figure(fig, (width, height), 120)

title = Image.from_text_bounded("average ages of G7 leaders".upper(), chart.size, 80, partial(sans, bold=True), padding=(20, 0))
subtitle = Image.from_text_bounded("average ages since 1/1/2000, and the oldest and youngest in that period", (round(chart.width * 0.95), chart.height), 60, partial(sans, italics=False), padding=(20,10,20,20))
img = Image.from_column([title, subtitle, chart], bg="white")
img.place(Image.from_text("/u/Udzu", sans(12), fg="black", bg="white", padding=5).pad((1, 1, 0, 0), "black"), align=1, padding=5, copy=False)
img.save(f"output/leadersage.png")
