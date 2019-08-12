from pudzu.charts import *

table = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_by_intentional_homicide_rate")[1]
df = table.drop_duplicates().set_index(0)[[3]].dropna().rename(columns={3: 'homicides'})[1:]
df = df[df.homicides != "Rate"].update_columns(homicides=float).sort_values("homicides", ascending=False)

def colorfn(c):
    c = { "Republic of the Congo": "Congo", 
          "Swaziland": "South Africa",
          "The Gambia": "Gambia",
          "Macedonia": "North Macedonia",
          "Democratic Republic of the Congo": "D. R. Congo",
          "Aland Islands": "Finland",
          "Western Sahara": "Morocco"}.get(c, c)
    if c in ['Sea', 'Borders']: return "white"
    if c not in df.index: return print(c) or VegaPalette10.RED
    #if df.homicides[c] * 2 < 2.93: return VegaPalette10.RED
    if df.homicides[c] < 2.93: return VegaPalette10.RED
    #if df.homicides[c] / 2 < 2.93: return VegaPalette10.LIGHTBLUE
    else: return "grey"

chart = map_chart("maps/World.png", colorfn)
title = Image.from_markup("**Countries whose overall intentional homicide rate is lower than the Brazilian police's 2018 homicide rate**".upper(), partial(arial, 40))
img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_brazil.png")
