from pudzu.charts import *
from pudzu.sandbox.bamboo import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country")
df = pd.read_csv("datasets/demographics_greek.csv")

def rlabel(r):
    return Image.from_text(str(df.year[r]), sans(16), padding=(0,2))

def clabel_outside(c,r,v):
    return Image.from_text("{:,}k\n({})".format(int(v) if v == int(v) else v, df.pc[r]), sans(16, bold=True), line_spacing=2, bg=RGBA(255, 255, 255, 200), padding=2, align="center")

chart = bar_chart(df[["greek"]], 80, 1100, spacing=2, label_font=sans(14),
    clabels={ BarChartLabelPosition.OUTSIDE: clabel_outside },
    rlabels=rlabel, grid_interval=100, ylabels=lambda v: "{:,},000".format(v) if v > 0 else "0",
    ylabel=Image.from_text("number of Greeks living in Turkey (Anatolia)", sans(18), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90))

legend = generate_legend([], [], header="KEY EVENTS", footer=
"""////**1912-13 Balkan Wars**
- saw ethnic cleansing of Turks in Europe
**1913-23 Greek Genocide**
- systematic killing of ~500,000 Greeks
**1919-22 Greco-Turkish War**
- unsuccessful post-War attack by Greece
**1923 population exchange with Greece**
- expulsion of ~1.2m Greeks and 400k Turks
**1932 Law 2007**
- law banning Greeks from 30 professions
**1942 Wealth Tax**
- ruinous tax targeted at non-Muslims
**1955 Istanbul Pogrom**
- state-sponsored mob attacks on Greeks
**1964-65 Expulsion of Istanbul Greeks**
- mass expulsion as a diplomatic tool
**1974 Turkish invasion of Cyprus**
- following a Greek-sponsored Cypriot coup""", font_family=partial(sans, 16))


chart.place(legend, align=(1,0), padding=(10,30), copy=False)

img1 = Image.from_url_with_cache("http://www.stavrodromion.org/images/Churches/Agia_Triada/1.jpg")
img2 = Image.from_url_with_cache("https://www.aegeandocumentary.org/wp-content/uploads/2013/06/the-film-mobile.jpg").resize_fixed_aspect(width=img1.width)
img3 = Image.from_column([img1, img2])

chart = Image.from_row([img3, chart])

footer = Image.from_markup("""**Sources**
- Pentzopoulos, Dimitri (2002). //The Balkan Exchange of Minorities and Its Impact on Greece//. C. Hurst & Co. pp. 29–30. ISBN 978-1-85065-702-6
- Icduygu, A., Toktas, S., & Soner, B. A. (2008). //The politics of population in a nation-building process: Emigration of non-muslims from turkey//. Ethnic and Racial Studies, 31(2), 358–389.           """
, partial(arial, 14))


title = Image.from_column([
    Image.from_text("The disappearance of Turkey's Greeks ".upper(), sans(48, bold=True)),
    ], bg="white", padding=2)

img = Image.from_column([title, chart, footer], bg="white", padding=5).pad((0,0,0,10), "white")
img.place(Image.from_text("/u/Udzu", sans(12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)
img.save("output/demographics_greek.png")
img.convert("RGB").save("output/demographics_greek.jpg", quality=90)