from pudzu.charts import *
from pudzu.bamboo import *

df = pd.read_csv("datasets/etymsmurfs.csv").set_index("language")

CATEGORIES = ["sh", "sm", "s", "o", None]
DESCRIPTIONS = ["from French Schtroumpfs", "from Dutch Smurfen", "other names beginning with S", "names not beginning with S", "unknown"]
PALETTE = ['#045a8d', '#2b8cbe', '#bdc9e1', '#cc2735', 'grey']
FOOTER = "\n".join([
"• Schtroumpf is a neologism that happens to sound like the German for sock.",
"• Smurf is also a neologism.",
"• Šmoulové is based on their blue colour.",
"• Şirinler means cute.",
"• Barrufet is a Catalan sprite and sounds similar to Barretina, the smurf hat.",
"• Pitufos comes from Patufet, a Catalan folktale character.",
"• Pottokiak comes from Pottoka, the Basque pony breed.",
"• Puffi comes from buffi (funny/strange).",
"• Törpök means dwarves.",
"• Dardasim is a portmanteau of dardakim (young children) and nanasim (dwarfs)"
])
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    else: return PALETTE[CATEGORIES.index(df.group.get(c))]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(font, "fonts/arialu", bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE, DESCRIPTIONS, header="Etymologies", footer=FOOTER, box_sizes=(80,40), max_width=300, box_mask=Image.open("icons/smurf.jpg").convert("L").invert_mask(), fonts=partial(arial, 16))
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("‘THE SMURFS’ IN DIFFERENT LANGUAGES", arial(48, bold=True)),
Image.from_text("translations and etymologies of Peyo's little blue creatures", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymsmurfs.png")
