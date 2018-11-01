from pudzu.charts import *

INTERVAL = 20
CONTINENTS = ["Europe", "North America", "Asia", "Oceania", "Africa", "South America"]
PALETTE = [VegaPalette10[c] for c in ("Blue", "Red", "Orange", "Purple", "Brown", "Green")]

FILTER = {"Chemistry", "Physics", "Physiology and Medicine" }
TITLE = "Science Nobel Prize winners by continent"
SUBTITLE = "Physics, Chemistry and Medicine prizes by the nationality of the winners*"
FILENAME = "nobels_science"

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')
nobels = pd.read_csv("datasets/nobels.csv").split_columns('countries', '|')
nobels = nobels[nobels.countries != ()]
nobels = nobels[nobels.category.isin(FILTER)]
nobels = nobels.assign_rows(continents = lambda d: frozenset(atlas.continent[c] for c in d.countries))

by_continent = nobels.split_rows('continents')
df_continent = pd.DataFrame(columns=["date"]+CONTINENTS)
for i in range(nobels.date.min(), nobels.date.max() + 1, INTERVAL):
    df = by_continent[(by_continent.date >= i) & (by_continent.date < i + INTERVAL)]
    d = df.groupby("continents").count().name
    df_continent.loc[len(df_continent)] = [f"{i}–{min(nobels.date.max(),i+INTERVAL-1)}" if c == "date" else d.get(c, 0) for c in df_continent.columns]
d = by_continent.groupby("continents").count().name
df_continent.loc[len(df_continent)] = ["TOTAL" if c == "date" else d.get(c, 0) for c in df_continent.columns]
data = df_continent.set_index("date")

by_country = nobels.split_rows('countries')
country_dict = {}
for n,i in enumerate(range(nobels.date.min(), nobels.date.max() + 1, INTERVAL)):
    df = by_country[(by_country.date >= i) & (by_country.date < i + INTERVAL)]
    count = df.groupby("countries").count().name.sort_values(ascending=False)
    if (count[4] == count[5]): logger.log(logging.WARNING, "{} tie for 5/6 between {} and {}".format(i, count.index[4], count.index[5]))
    country_dict[n] = tuple(count[:5].items())
count = by_country.groupby("countries").count().name.sort_values(ascending=False)
if (count[4] == count[5]): logger.log(logging.WARNING, "Total tie for 5/6 between {} and {}".format(count.index[4], count.index[5]))
country_dict[len(country_dict)] = tuple(count[:5].items())

# plot

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: h-(h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray(mask_array * 255).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def flag(r,i):
    c, n = country_dict[r][i]
    if c == "Russia":
        flag = Image.from_url_with_cache("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/1000px-Flag_of_the_Soviet_Union.svg.png").to_rgba()
    elif c == "Germany" and r == 0:
        flag = Image.from_url_with_cache("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Flag_of_the_German_Empire.svg/1024px-Flag_of_the_German_Empire.svg.png").to_rgba()
    elif c == "Switzerland" and i == 4:
        flag = half_and_half(Image.from_url_with_cache(atlas.flag["Sweden"]).to_rgba().resize((900,600)), Image.from_url_with_cache(atlas.flag["Switzerland"]).to_rgba().resize((900,600)))
        n = f"{n} (tie)"
    else:
        flag = Image.from_url_with_cache(atlas.flag[c]).to_rgba()
    flag = flag.resize((70,50)).pad(1, "grey")
    label = Image.from_text(str(n), arial(16))
    return Image.from_column([flag, label])

def country_flags(r):
    return Image.from_row([flag(r, i) for i in range(5)], padding=(5,0), bg="white")

chart = bar_chart(data, 80, 1400, horizontal=True, spacing=2, type=BarChartType.STACKED_PERCENTAGE,
     colors = PALETTE,
     rlabels = { BarChartLabelPosition.BELOW: lambda r: Image.from_text(data.index[r], arial(28), padding=5),
                 BarChartLabelPosition.ABOVE: country_flags },
     clabels = {  BarChartLabelPosition.INSIDE: lambda c,r,v: Image.from_text(str(data.iloc[r][c]), arial(18)) },
     label_font=arial(16), grid_interval = 0.1,
    ylabel=Image.from_text("science prizes by continent (and 5 winningest countries)", arial(28), padding=5)
     )

title = Image.from_column([
Image.from_text(TITLE.upper(), arial(64, bold=True), padding=(5,10,5,2)),
Image.from_text(SUBTITLE, arial(40, bold=False), padding=(5,2,5,10))
], bg="white")

# TODO: legend, title, 

legend = Image.from_row([
    Image.from_row([Rectangle(40, c), Image.from_text(s, arial(24))], padding=2)
    for c,s in zip(PALETTE, CONTINENTS)], padding=5, bg="white")

footer = Image.from_row([legend, Image.from_text("(*nationalites at or prior to award; winners from multiple continents are counted under each)", arial(24))], padding=10)

img = Image.from_column([title, chart.pad(10, "white"), footer], bg="white")
img.save(f"output/{FILENAME}.png")

