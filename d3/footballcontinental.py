from pudzu.charts import *
from generate import *

df = pd.read_csv("datasets/footballcontinental.csv").set_index("continent")

colormap = {}
for i,cs in df.iterrows():
    cs = cs.teams.split("|")
    assert set(cs) < set(atlas.index), f"Unrecognised countries: {set(df.index) - set(atlas.index)}"
    for c in cs:
        colormap[c] = i if c != "Australia" else "Australia"

PALETTE = {
    "Europe": VegaPalette10.RED,
    "South America": VegaPalette10.GREEN    ,
    "North America": VegaPalette10.LIGHTGREEN,
    "Oceania": VegaPalette10.PURPLE,
    "Asia": VegaPalette10.BLUE,
    "Africa": VegaPalette10.BROWN,
}

LABELS = {
    "Europe": "European Championship",
    "South America": "Copa América",
    "North America": "CONCACAF Gold Cup",
    "Oceania": "OFC Nations Cup",
    "Asia": "Asian Cup",
    "Africa": "Africa Cup of Nations",
}

ps = ["Oceania", "Asia"]
WIDTH = 10
rects = [f'<rect x="{i*WIDTH}" y="0" width="{WIDTH}" height="{WIDTH*len(ps)}" style="fill:{PALETTE[p].to_hex()}"/>' for i,p in enumerate(ps)]
PATTERNS = f'''<defs>
<pattern id="{''.join(ps)}" width="{WIDTH*len(ps)}" height="{WIDTH*len(ps)}" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
{'  '.join(rects)}
</pattern>
</dev>
'''
PALETTE["Australia"] = f'url(#{"".join(ps)})'


generate_datamap("footballcontinental", colormap, palette=PALETTE, patterns=PATTERNS, codifier=partial(codify_countries, dependencies=False))


FONT = sans

HEADER_PC = "Championship"
PALETTE_PC = sorted((c,l) for (l,c) in LABELS.items())

legend_pc = generate_legend([PALETTE[l] for _,l in PALETTE_PC], [c for c,_ in PALETTE_PC], 50, partial(FONT, 24), header=HEADER_PC.upper())
img_pc = Image.open("temp/footballcontinental.png").remove_transparency("white").place(legend_pc, (0,0.7), padding=50)
title_pc = Image.from_text("continental football championship winners".upper(), FONT(60, bold=True))
chart = Image.from_column([title_pc, img_pc], bg="white", padding=10)
chart.place(Image.from_text("/u/Udzu", font("arial", 24), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
chart.convert("RGB").save("output/footballcontinental.png")

