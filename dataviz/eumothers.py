from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/eumothers.csv").set_index("country")
FONT = sans

PALETTE = {
    "IWD": VegaPalette10.RED,
    "SE": VegaPalette10.GREEN,
    "FSL": VegaPalette10.ORANGE,
    "FSM": VegaPalette10.LIGHTBLUE,
    "SSM": VegaPalette10.BLUE,
    "LSM": VegaPalette10.PURPLE,
    "other": VegaPalette10.GREY,
}

DESCRIPTIONS = [
    "**International Women's Day** (8 March)",
    "**Spring Equinox** (21 March)",
    "**Fourth Sunday in Lent** (Mothering Sunday)",
    "**First Sunday of May**",
    "**Second Sunday of May**",
    "**Last Sunday of May**\n(may be postponed in France for Pentecost)",
    """**On a different day**
  Norway: Second Sunday of February
  Israel: 30 Shevat (~February)
  Georgia: 3 March
  Slovenia: 25 March
  Armenia: 7 April
  Iran: 21 Ordibehesht (~11 May)
  Poland: 26 May
  Luxembourg: Second Sunday of June
  Belarus: 14 October
  Serbia: Second Sunday before Christmas""",
]
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index or non(df.group.get(c)): return "grey"
    elif "&" in df.group.get(c):
        colors = [PALETTE[i] for i in df.group[c].split("&")]
        return Stripe(20, *colors)
    elif "|" in df.group.get(c):
        return VegaPalette10.BROWN
    else: return PALETTE[df.group.get(c)]
    
map = map_chart("maps/Europe2.png", colorfn, None)
legend = generate_legend(list(PALETTE.values()), DESCRIPTIONS, box_sizes=(40,...), header="Mother's Day mainly celebrated on...".upper(), footer=FOOTER, font_family=partial(FONT, 16))
chart = map.place(legend, align=(1,0), padding=50)

title = Image.from_column([
Image.from_text("MOTHER'S DAYS", FONT(96, bold=True)),
Image.from_text("date of main Mother's Day celebrations (according to Wikipedia)", FONT(36))
],
bg="white", padding=2)

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.8)
img.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eumothers.png")

