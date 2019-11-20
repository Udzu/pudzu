from pudzu.charts import *
import seaborn as sns

BG = "white"
FONT = calibri
LIMITS = [10, 5, 2, 1, 0]
REDS = treversed(tmap(RGBA, sns.color_palette("Reds", len(LIMITS))))

countries = pd.read_csv("datasets/countries.csv").split_columns(['country', 'organisations', 'tld'], "|").explode('country').set_index("country")
states = pd.read_csv("datasets/usstates.csv").set_index('name')

eus = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_by_intentional_homicide_rate")
eu = eus[3].set_index(0)[[1]].dropna()[1:].rename(columns={1: 'homicides'}).update_columns(homicides=float).sort_values("homicides", ascending=False).filter_rows(lambda d, i: i in countries.index and 'eu' in countries.organisations[i])

uss = pd.read_html("https://en.wikipedia.org/wiki/Murder_in_the_United_States_by_state")
us = uss[0].set_index(0)[[3]][1:].rename(columns={3: 'homicides'}).update_columns(homicides=float).sort_values("homicides", ascending=False)

def colorfn(c, df):
    if c in ['Sea', 'Borders']: return BG
    c = {"UK": "United Kingdom", "Bosnia": "Bosnia and Herzegovina"}.get(c, c)
    if c not in df.index: return "grey"
    return REDS[next(i for i,lim in enumerate(LIMITS) if df.homicides[c] > lim)]

eu_map = map_chart("maps/Europe.png", partial(colorfn, df=eu))
us_map = map_chart("maps/USA.png", partial(colorfn, df=us))
us_map = us_map.trim((0,0,50,0))
legend_labels = ["{}+ per 100,000".format(LIMITS[0])] + ["{}–{} per 100,000".format(i,j) for i,j in zip(LIMITS[1:-1], LIMITS[:-2])] + ["<{} per 100,000".format(LIMITS[-2])]
legend = generate_legend(REDS, legend_labels, header="Intentional homicide rate", box_sizes=60, fonts=partial(FONT, 28))
maps = Image.from_row([us_map, eu_map.place(legend, align=(1,0), padding=10)], bg=BG)

eu = eu.assign_rows(source='eu')
us = us.assign_rows(source='us').filter_rows('homicides<20')
df = pd.concat([eu,us]).sort_values('homicides', ascending=False)

def bar_color(c, r): return VegaPalette10.RED if df.source[df.index[r]] == 'us' else "#003399"

def bar_label(r): 
    eu = df.source[df.index[r]] == 'eu'
    atlas = countries if eu else states
    flag = Image.from_url_with_cache(atlas.flag[df.index[r]]).to_rgba().resize((30,20)).pad(1, "grey")
    code = countries.tld[df.index[r]][0][1:].upper() if eu else states.code[df.index[r]]
    return Image.from_column([flag, Image.from_text(code, FONT(16), padding=(0,4,0,0))])
    
ylabel = Image.from_text("Intentional homicide rate per 100,000", FONT(16)).transpose(Image.ROTATE_90)
bar = bar_chart(df[['homicides']], 32, 400, spacing=1, bg=BG, colors=bar_color, ymax=max(df.homicides), grid_interval=1, rlabels=bar_label, clabels=None, label_font=FONT(16), ylabel=ylabel)
bar_legend = generate_legend([VegaPalette10.RED, "#003399"], ["US state", "EU member"], fonts=partial(FONT, 32))
bar = bar.place(bar_legend, align=(1,0), padding=(10,25))

title = Image.from_column([
Image.from_text("A COMPARISON OF HOMICIDE RATES IN THE US AND EU", FONT(96, bold=True)), 
Image.from_text("2015 data from the United Nations Office on Drugs, and Crime and the FBI Uniform Crime Reports", FONT(54, italics=True))
], padding=5)

img = Image.from_column([title, maps, bar], bg=BG, padding=10)
img = img.pad((0,0,0,40), "white").place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10)
img.save("output/politics_homicide.png")