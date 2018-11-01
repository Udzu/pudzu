from pudzu.charts import *

FONT = calibri
BARBG = "#AAAAAA80"
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index("country")
atlas.flag["Northern Ireland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Northern_Ireland.svg/1024px-Flag_of_Northern_Ireland.svg.png"
atlas.flag["Wales"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Flag_of_Wales_2.svg/1024px-Flag_of_Wales_2.svg.png"
data = pd.read_csv("datasets/worldcup_smallest.csv")

stages = ["winner", "finalist", "semifinalist", "quarterfinalist", "competitor"]
maxes = [10, 10, 5, 5, 5]
intervals = [2, 2, 1, 1, 1]

# TODO: header, maximums

imgs = []
width, mx, it = 1000, 10, 1
for stage in stages:
    df = data[data.stage == stage].copy().reset_index()
    df = df.assign_rows(parity = lambda d, i: i % 2)
    df = df.assign_rows(popmax = lambda d: min(d['population'], mx))
    df = df.assign_rows(bar = lambda d: 0 if d['parity'] else mx - d['popmax'])

    def rlabel(r):
        img = Image.from_row([
            Image.from_text("{} ({})".format(df.country[r], df.year[r]), FONT(16), "black", align="center"),
            Image.from_url_with_cache(atlas.flag[df.country[r]]).convert("RGBA").resize((60,40)).trim(1).pad(1, "grey")
        ], padding=(2,0))
        return Rectangle((250,40), None if df.parity[r] else BARBG).place(img, align=(1,0.5))

    def label(c,r,v):
        if c > 0: return None
        else: return "{:.1f}m".format(df.population[r])

    def color(c,r,v):
        if c == 1: return BARBG
        elif v < df.population[r]: return VegaPalette10.ORANGE
        else: return VegaPalette10.BLUE
        
    chart = bar_chart(df[['popmax', 'bar']], 40, width, type=BarChartType.STACKED, bg=None, horizontal=True, spacing=2, label_font=FONT(16), rlabels=rlabel,
    clabels=label, colors=color, ylabel=None if stage != "winner" else Image.from_text("historic population (millions)", FONT(24, italics=True), padding=10),
    grid_interval=it, ymax=mx)
    label = Image.from_text("{}{}".format(stage.upper(), "*"*(False and stage in ["quarterfinalist", "competitor"])), FONT(28, bold=True), padding=10).transpose(Image.ROTATE_90)
    imgs.append([label, chart])
    
img = Image.from_array(imgs, padding=10)
title = Image.from_text("Smallest countries by population\nat each stage of the FIFA World Cup".upper(), FONT(52, bold=True), line_spacing=10, align="center")
footer = Image.from_text("* Competitors include the 1930 World Cup which had no qualification round. Quarterfinalists include the 1978 and 1982 World Cups which had a group stage of 8, but not the 1950 or 1982 World Cups, which didn't. Semifinalists and finalists include the 1950 World Cup, which had a final group stage of 4.", FONT(18), max_width=1100)
img = Image.from_column([title, img, footer], bg="white", padding=10)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg=None, padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/worldcup_smallest.png")
