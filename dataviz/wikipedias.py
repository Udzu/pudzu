from pudzu.charts import *

dfs = pd.read_html("https://en.wikipedia.org/wiki/List_of_Wikipedias#Statistics_totals")
df = dfs[4].set_index("Language")
df = df[df.Depth != "——"]
df.Depth = df.Depth.apply(float)
df["Non-articles"] = df["Total pages"] - df["Articles"]
df["Weighted count"] = np.exp(sum(np.log(df[x] / df[x]["English"] * df["Articles"]["English"]) for x in ["Articles", "Non-articles", "Edits"]) / 3)
df["Weighted count"] = df["Weighted count"].apply(lambda i: int(round(i)))

df = df.sort_values("Weighted count", ascending=False)
df = df[:15]

FONT = sans
SCALE = 2.25
s = lambda i: round(i * SCALE)
FONTSIZE = s(16)
BIGFONT = s(18)
SMALLFONT = s(14)
SUBTITLEFONT = s(18)
TITLEFONT = s(38)

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country").flag
atlas["England"] = "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1920px-Flag_of_England.svg.png"

flags = {
    "English": "England",
    "Arabic": "Saudi Arabia",
    "Ukrainian": "Ukraine",
    "Russian": "Russia",
    "French": "France",
    "Italian": "Italy",
    "Spanish": "Spain",
    "Vietnamese": "Vietnam",
    "German": "Germany",
    "Chinese": "China",
    "Portuguese": "Portugal",
    "Japanese": "Japan",
    "Persian": "Iran",
    "Swedish": "Sweden",
    "Dutch": "Netherlands",
    "Polish": "Poland",
    "Cebuano": "Philippines",
    "Korean": "South Korea",
    "Serbian": "Serbia",
}
# Bar charts

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: h-(h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray((mask_array * 255).astype('uint8')).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def rlabel(r):
    if "Serbo" in df.index[r]:
        flag = half_and_half(Image.from_url_with_cache(atlas["Croatia"]).resize((900, 600)),
                             Image.from_url_with_cache(atlas["Serbia"]).resize((900, 600)))
    else:
        flag = Image.from_url_with_cache(atlas[flags.get(df.index[r], "Turkey")]).convert("RGBA")
    return Image.from_row([
        Image.from_text(df.index[r].replace("\\n","\n"), FONT(FONTSIZE), "black", align="center"),
        flag.resize((s(48*1.5),s(48))).trim(s(1)).pad(s(1), "grey")
    ], padding=(s(2),0))

def label_if(pred, labeler=lambda c,r,v: f' {v:,}'): # TODO: automate this bit
    return lambda c,r,v: None if not pred(v) else labeler(c,r,v)

chart = bar_chart(df[["Weighted count"]], s(48), s(1000), bg=None, horizontal=True, spacing=s(2), label_font=FONT(FONTSIZE), rlabels=rlabel,
    clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,10_000_000)),
               BarChartLabelPosition.OUTSIDE : label_if(artial(op.lt,10_000_000))},
    ymax=8_000_000, grid_interval=500_000, grid_width=s(0.5), tick_interval=1_000_000, label_interval=1_000_000,
    ylabels=lambda v: f"{int(v/1_000_000)}",
    ylabel=Image.from_text("weighted article count in millions", FONT(BIGFONT), padding=s(5)))
    
# Put it all together

logo = Image.from_url_with_cache("https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1024px-Wikipedia-logo-v2.svg.png")
chart = chart.place(logo, align=(1,1), padding=200)

title = Image.from_column([Image.from_text("Largest language Wikipedias, weighted by activity".upper(), FONT(TITLEFONT, bold=True)),
                           Image.from_markup(
"""calculated using the geometric mean of the numbers of articles, non-articles and edits, normalised against English
//Source//: [[https:\//en.wikipedia.org/wiki/List_of_Wikipedias]] (30 July 2023)""", partial(FONT, SUBTITLEFONT), align="center", line_spacing=10)])
img = Image.from_column([title, chart], padding=s(5), bg="white")
img = img.place(Image.from_text("/u/Udzu", FONT(s(16)), fg="black", bg=0, padding=s(5)).pad((s(1),s(1),0,0), "black"), align=1, padding=s(10))
img.save("output/wikipedias.png")
