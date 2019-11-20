from pudzu.charts import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')
df = pd.read_csv("datasets/siunits.csv").fillna("d")

# TODO: count by type, add two types and sort
counts = df.groupby("country").count()
counts["sort"] = counts.description - 10 * counts.index.isin(["latin", "greek"])
counts = counts.sort_values("sort", ascending=False)[['symbol']]

gb = df.groupby(["country", "type"]).count()[["symbol"]]
counts = gb.symbol.unstack(level=1).fillna(0)
counts["sort"] = counts.b + counts.d + counts.n - 10 * counts.index.isin(["latin", "greek"])
counts = counts.sort_values(["sort", "b"], ascending=False).drop("sort", axis=1)

# ylabel = Image.from_text("% of area in Europe", arial(14), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: h-(h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray(mask_array * 255).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def rlabel(r):
    countries = atlas[atlas.tld.str.contains(counts.index[r])].index
    if len(countries) >= 1:
        name = countries[0]
        if "Kingdom" in name: name = "UK"
        if "States" in name: name = "US"
        flag = Image.from_url_with_cache(atlas.flag[countries[0]])
    elif counts.index[r] == "hrsb":
        name = "Croerbia*"
        flag = half_and_half(Image.from_url_with_cache(atlas.flag["Croatia"]).resize((900,600)), Image.from_url_with_cache(atlas.flag["Serbia"]).resize((900,600)))
    else:
        name = counts.index[r].title()
        flag = Rectangle((90,60), "#EEEEEE").place(Image.from_text(["abc","αβγ"]["Greek" in name], arial(24, bold=True), beard_line=True))
    return Image.from_column([
            flag.resize((90,60)).pad(1, "grey").pad((0,5), "white"),
            Image.from_text(name.upper(), arial(14, bold=True), "black", align="center", padding=(0,2))
            ], bg="white")
            
def clabel(c,r,v,w,h): 
    rows = df[(df.type == counts.columns[c]) & (df.country == counts.index[r])]
    color = ["black", "white"][counts.columns[c] == "b"]
    if len(rows) == 0: return None
    def box(w,h,symbol,name):
        return Rectangle((w,h), 0).place(Image.from_text(symbol, arial(24, bold=True), color, beard_line=True), align=(0.5,0.4)).place(Image.from_text(name, arial(12, italics=True), color, max_width=w, align="center", beard_line=True), align=(0.5,1), padding=(0,3))
    return Image.from_column([box(w,h//len(rows),r.symbol,"({})".format(r.description) if r.country in ["latin", "greek"] else r.description) for _, r in rows.iterrows()])
    
chart = bar_chart(counts, 100, 800, type=BarChartType.STACKED, colors=[VegaPalette10.BLUE.darken(0.7), VegaPalette10.BLUE, VegaPalette10.BLUE.brighten(0.5)],
    spacing=5, ymax=8, rlabels=rlabel, clabels={ BarChartLabelPosition.INSIDE : clabel },
    grid_interval=1, label_interval=1, label_font=arial(14, bold=False),
    legend_fonts=partial(arial, 14), legend_position=(0.5,0.1), legend_args={'header': 'type of unit'.upper(), 'labels': ['SI base unit', 'SI derived unit', 'sanctioned non-SI unit'], 'footer': 'Other accepted non-SI units include min, h, d, °, ′, ″, t, au.', 'max_width': 200})

title = Image.from_column([
Image.from_text("etymologies of the SI unit names".upper(), arial(40, bold=True), padding=(5,10,5,2)),
Image.from_text("arranged by the nationality of the scientists (or language of the words) they're named for", arial(24, bold=False), padding=(5,2,5,10))
], bg="white")

footer = Image.from_text("* Tesla was an ethnic Serb born in present day Croatia, then part the Austrian Empire, who emigrated to the US.", arial(14), "black", padding=10)

img = Image.from_column([title, chart.pad(10, "white"), footer], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/siunits.png")