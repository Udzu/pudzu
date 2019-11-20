from pudzu.charts import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')
df = pd.read_csv("datasets/eutourism.csv").set_index("Destination").select(lambda c: atlas.continent[c] == "Europe" or c in ["Georgia", "Azerbaijan", "Armenia"])
df = df.fillna({'2015': df['2014']})[['2015','2015.1']]
df.columns = ['arrivals', 'receipts']
df = pd.concat([df, atlas[['population']]], join='inner', axis=1)[lambda df: df.population > 100000]
df['arrivals_pc'] = df['arrivals'] / df['population'] * 1000000
df['receipts_pc'] = df['receipts'] / df['population'] * 1000000

arrivals = df[['arrivals']].sort_values('arrivals', ascending=False)
receipts = df[['receipts']].sort_values('receipts', ascending=False)
arrivals_pc = df[['arrivals_pc']].sort_values('arrivals_pc', ascending=False)
receipts_pc = df[['receipts_pc']].sort_values('receipts_pc', ascending=False)

def rlabel(df, r): 
    return Image.from_row([
        Image.new("RGBA", (180,0), 0).pin(Image.from_text("{}. {}".format(r+1, df.index[r].replace("United Kingdom", "UK")).replace("Czech Republic", "Czechia").upper(), arial(18, bold=True), padding=2), (0,0), align=(0,0.5)),
        Image.from_url_with_cache(atlas.flag[df.index[r]]).resize((80,60)).pad(1, "grey").pad((2,0), "white")
        ], padding=1, bg="white")

def clabel(formatter, filterfn, col, c, r, v):
    return Image.from_text(formatter(v), arial(16, bold=False), col, padding=3) if filterfn(v) else None

imgs = []    
for title, df, ft, mx in [("total tourist arrivals (in millions)", arrivals,lambda v: "{:.1f}m".format(v/1000), 6000),
                           ("tourist arrivals per thousand population", arrivals_pc,lambda v: "{:,}".format(int(v)).replace(',', ' '), 500),
                           ("total tourist receipts (in US$ billions)", receipts,lambda v: "${:.1f}b".format(v/1000), 5000),
                           ("tourist receipts per capita", receipts_pc,lambda v: "${:,}".format(int(v)).replace(',', ' '), 600)
                           ]:
    img = bar_chart(df, 62, 600, horizontal=True, spacing=1, colors=["#003399"], ymax=df.iloc[0][0], rlabels=partial(rlabel, df),
                    clabels={ BarChartLabelPosition.INSIDE : partial(clabel, ft, lambda v: v > mx, "white"), 
                              BarChartLabelPosition.OUTSIDE :  partial(clabel, ft, lambda v: v <= mx, "black") })
    img = Image.from_column([Image.from_text(title.upper(), arial(24, bold=True)), img], padding=5, bg="white")
    imgs.append(img)

chart = Image.from_row(imgs, bg="white", padding=5)

title = Image.from_column([
Image.from_text("International tourism in Europe, 2015".upper(), arial(90, bold=True), padding=(5,10,5,2)),
Image.from_text("figures from the United Nations World Tourism Organization*", arial(60, italics=True), padding=(5,2,5,10))], bg="white")

footer = Image.from_text("* chart excludes countries and territories with fewer than 100 thousand residents; arrival figures for Sweden and Slovakia are from 2014.", arial(32, italics=True), "black", padding=10)

img = Image.from_column([title, chart, footer], bg="white", padding=20)
img = img.resize_fixed_aspect(scale=0.5)
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eutourists.png")
