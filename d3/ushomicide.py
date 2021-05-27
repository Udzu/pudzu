from generate import *
from pudzu.charts import *

# generate d3 html

df = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_by_intentional_homicide_rate")[2]
COL = df.columns[0]
df[COL] = df[COL].apply(lambda x: x.replace("†","") if isinstance(x, str) else x) 
rates = df.set_index(COL).Rate

X = 2

COUNTRY = "United States"
THRESHOLD = rates[COUNTRY]
pc_much_greater = list(rates[(rates >= THRESHOLD*X)].index)
pc_greater = list(rates[(rates > THRESHOLD) & (rates < THRESHOLD*X)].index)
pc_less = list(rates[(rates < THRESHOLD) & (rates > THRESHOLD/X)].index)
pc_much_less = list(rates[(rates <= THRESHOLD/X)].index)
pc_same = list(rates[rates == THRESHOLD])

generate_datamap("ushomicide", dict_from_vals(much_greater=pc_much_greater, greater=pc_greater, less=pc_less, much_less=pc_much_less),  { "greater": VegaPalette10.ORANGE, "same": VegaPalette10.GREY, "less": VegaPalette10.LIGHTBLUE, "much_greater": VegaPalette10.RED, "much_less": VegaPalette10.BLUE })

# generate maps (currently done manually)

# add legends, title, etc

FONT = sans

HEADER_PC = "Homicide rate"
COLORS_PC = VegaPalette10.RED, VegaPalette10.ORANGE, "#cccccc", VegaPalette10.LIGHTBLUE, VegaPalette10.BLUE
LABELS_PC = "over 2x US rate", "1x to 2x US rate", "US rate (=4.96/100k)", "½x to 1x US rate", "less than ½x US rate"
legend_pc = generate_legend(COLORS_PC, LABELS_PC, 50, partial(FONT, 24), header=HEADER_PC.upper())
img_pc = Image.open("temp/ushomicide.png").remove_transparency("white").place(legend_pc, (0,0.7), padding=50)
title_pc = Image.from_text("US intentional homicide rate compared to the rest of the world".upper(), FONT(60, bold=True))
subtitle_pc = Image.from_markup("//using UNODC homicide data from [[https:\//en.wikipedia.org/wiki/List_of_countries_by_intentional_homicide_rate]]//", partial(FONT, 32))
chart = Image.from_column([title_pc, subtitle_pc, img_pc], bg="white", padding=10)
chart.place(Image.from_text("/u/Udzu", font("arial", 24), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
chart.convert("RGB").save("output/ushomicide.png")

