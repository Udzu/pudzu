from pudzu.charts import *
from pudzu.bamboo import *
from fractions import Fraction

# data
df = pd.read_csv("datasets/nobels.csv").split_columns('countries', '|').explode('countries').update_columns(jewish=Fraction)
countries = sorted(c for c in set(df.countries) if len(df[df.countries == c]) >= 5)
dj = pd.DataFrame([{ 'total': len(dc), 'jewish': len(dc[dc.jewish == 1]), 'half': len(dc[(dc.jewish < 1) & (dc.jewish >= 0.5)]) } for c in countries for dc in [df[df.countries == c]]], index=countries)
do = df.filter_rows(lambda d: d['countries'] not in countries).groupby("name").head()
dj = dj.sort_values("total", ascending=False)
dj.loc["Other*"] = { "total":  len(do), "jewish": len(do[do.jewish == 1]), "half": len(do[(do.jewish < 1) & (do.jewish >= 0.5)]) }
dj["gentile"] = dj["total"] - dj["jewish"] - dj["half"]
dj["rest"] = 400 - dj["total"]
dj["pc"] = dj["jewish"] / dj["total"]

# graphs
flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country").flag
flags["Other*"] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_the_United_Nations.svg/1024px-Flag_of_the_United_Nations.svg.png'
dem = pd.read_csv("datasets/demographics_jewish2.csv").set_index("country")

FONT = calibri
BARBG = "#AAAAAA80"
table = dj[["jewish", "half", "gentile", "rest"]]

def colorfn(c,r,v):
    if c < 3: return [VegaPalette10.BLUE, VegaPalette10.LIGHTBLUE, VegaPalette10.RED][c]
    else: return [BARBG, None][r % 2 != 0]

def rlabelfn(r, df):
    label = {"US": "United States", "UK": "United Kingdom", "Czech Republic": "Czechia"}.get(df.index[r], df.index[r])
    img = Image.from_row([
        Image.from_text(label, FONT(16), "black"),
        Image.from_url_with_cache(flags[df.index[r]]).convert("RGBA").resize((30,20)).trim(1).pad(1, "grey")
    ], padding=(2,0))
    return img.pad_to_aspect(150,20, bg=[BARBG, None][r % 2 != 0], align=1)

def pclabelfn(r, df):
    imgs = [Image.from_text("N/A" if "Other" in df.index[r] else "<0.01%" if dem[c][df.index[r]] == 0 else format_float(dem[c][df.index[r]], 2)+"%", FONT(16), "black", beard_line=True) for c in ["2016", "1933"]]
    imgs = [Rectangle((80,20), [BARBG, None][r % 2 != 0]).place(img) for img in imgs]
    return Image.from_row(imgs)
    
def pclabelhead():
    imgs = [Image.from_text(c, FONT(16, bold=True), "black", beard_line=True) for c in ["2016", "1933"]]
    imgs = [Rectangle((80,20), None).place(img) for img in imgs]
    return Image.from_row(imgs)
    
chart1 = bar_chart(table, 20, 700, type=BarChartType.STACKED, spacing=2, colors=colorfn,
                  horizontal=True, label_font=FONT(16), clabels=None, rlabels=partial(rlabelfn, df=dj),
                  ymax=400, grid_interval=50,
                  xlabel=Image.from_markup("by country (//*Other includes all countries with fewer than 5 winners//)", partial(FONT, 16), "black", padding=10).transpose(Image.ROTATE_90),
                  ylabel=Image.from_text("by total number of Nobel laureates", FONT(16), "black", padding=10))

legend = generate_legend([colorfn(i,0,0) for i in range(3)], ["Jewish", "Half-Jewish", "Not Jewish"], fonts=partial(FONT, 16), header="Background", box_sizes=30)
chart1 = chart1.place(legend, align=1, padding=(20,10))
                  
do = dj.loc["Other*"]
dp = dj.drop("Other*").sort_values(["pc", "total"], ascending=False)
dp.loc["Other*"] = do
table = dp[["jewish", "half", "gentile"]]
chart2 = bar_chart(table, 20, 400, type=BarChartType.STACKED_PERCENTAGE, spacing=2, colors=colorfn,
                   horizontal=True, label_font=FONT(16), ylabel=Image.from_text("by proportion of winners who are Jewish", FONT(16), "black", padding=10),
                   rlabels={BarChartLabelPosition.BELOW: partial(rlabelfn, df=dp), BarChartLabelPosition.ABOVE: partial(pclabelfn, df=dp)},
                   clabels=lambda c,r,v: [None,"{:.0%}".format(v)][c<=1 and v >= 0.05], grid_interval=0.25)
chart2 = chart2.place(pclabelhead(), align=(1,0), padding=(0,30))
chart2 = chart2.place(Image.from_text("Jewish population", FONT(16, bold=True), "black"), align=(1,0), padding=(20,10))
                   
combined = Image.from_row([chart1, chart2], bg="white", yalign=1)

title = Image.from_text("Jewish Nobel laureates by country".upper(), FONT(60, bold=True))
img = Image.from_column([title, combined], padding=5, bg="white")
img = img.pin(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg=None, padding=5).pad((1,1,0,0), "black"), img.size, align=(1,0), bg="white")
img.save("output/nobelsjewish.png")

# wikipedia, cleaned up (link)
# jinfo
# 2016: American Jewish Yearbook 2016
# 1933: United States Holocaust Memorial Museum / American Jewish Committee / 1931 Palestine Census (removing subdistricts primarily in Palestine).


