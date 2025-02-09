from pudzu.charts import *
from pudzu.pillar import *

df = pd.read_csv("datasets/nobellit.csv")
df["ppc"] = df.prizes / df.population
df = df.sort_values("ppc", ascending=False).set_index("language")
df["ppc"]["Icelandic"] -= 2

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']
flags["Occitan*"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Flag_of_Occitania_%28with_star%29.svg/1280px-Flag_of_Occitania_%28with_star%29.svg.png"
flags["Yiddish*"] = "https://images.forwardcdn.com/image/1300x/center/images/cropped/yiddish-flag-1434390996.png"
flags["Arabic"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Flag_of_the_Arab_League.svg/1280px-Flag_of_the_Arab_League.svg.png"
flags["Bengali"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Bengali_language.svg/1024px-Bengali_language.svg.png"

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: h-(h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray((mask_array * 255).astype('uint8')).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def rlabel(r):
    lang = df.index[r]
    label = Image.from_text(lang.replace("-","-\n"), sans(16), "black", beard_line=True, align="center")
    country = {"Icelandic": "Iceland", "Norwegian": "Norway", "Swedish": "Sweden", "Hungarian": "Hungary", "Chinese": "China", "German": "Germany",
               "Danish": "Denmark", "Finnish": "Finland", "French": "France", "Turkish": "Turkey", "Japanese": "Japan",
               "Greek": "Greece", "Polish": "Poland", "Hebrew": "Israel", "Italian": "Italy", "Portuguese": "Portugal", "Spanish": "Spain",
               "English": "UK", "Czech": "Czechia", "Russian": "Russia", # "Bengali": "Bangladesh",
               }.get(lang, lang)
    if "Serbo" in lang:
        flag = half_and_half(Image.from_url_with_cache(flags["Croatia"]).resize((900, 600)),
                             Image.from_url_with_cache(flags["Serbia"]).resize((900, 600)))
    else:
        flag = Image.from_url_with_cache(flags[country]).convert("RGBA")
    flag = flag.resize((round(48*1.5), 48)).trim(1).pad(1, "grey")
    return Image.from_column([flag, label], padding=(0,2))

chart = bar_chart(
    df[["ppc"]], 80, 800,
    bg="white",
    clabels={ BarChartLabelPosition.INSIDE: lambda c,r,v: None if v <= 0.03 else str(df.prizes[r]),
              BarChartLabelPosition.OUTSIDE: lambda c,r,v: None if v > 0.03 else str(df.prizes[r]), },
    rlabels=rlabel,
    label_font=sans(16),
    ymax=1.049,
    ylabel=Image.from_text("# Nobel literature laureates per million native speakers", sans(18), padding=(5,2,5,10)).transpose(Image.ROTATE_90),
    ylabels=lambda v: "3.0" if v == 1 else format_float(v),
    grid_interval=0.05, tick_interval=0.05, label_interval=0.1,
)

# TODO: better!
pattern = Image.from_column([
    Triangle((10,5), "white", p=1/2),
    Rectangle((10,10), "white"),
    Triangle((10, 5), "white", p=1/2).transpose(Image.FLIP_TOP_BOTTOM),
])
rec = Image.from_pattern(pattern, (chart.width, 20))
#rec = Rectangle((img.width, 20), "white")
chart = chart.place(rec, 0, padding=(0,47))


title = Image.from_text("LITERATURE NOBELS BY LANGUAGE, PER NATIVE SPEAKER", sans(64, bold=True), padding=5)
footer = Image.from_markup("* Yiddish and Occitan values calculated against their early 20th century population highs of ~13 million native speakers; both have well under 1 million native speakers today", partial(sans, 16), "black", "white", padding=(0,10,0,10))

img = Image.from_column([title, chart, footer], bg="white", padding=2)
img = img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1, 1, 0, 0), "black"), align=1, padding=10)
img.save("output/nobelslit2.png")


