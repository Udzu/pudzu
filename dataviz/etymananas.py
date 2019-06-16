from pudzu.charts import *

FONT = arial
UFONT = partial(font, "fonts/arialu")
DEFAULT = VegaPalette10.GREEN
PALETTE = { "p": VegaPalette10.ORANGE, "o": VegaPalette10.BROWN, "?": "#aaaaaa", "a": DEFAULT }

df = pd.read_csv("datasets/etymananas.csv").set_index("country").fillna("")

countries = set(df.index)

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return DEFAULT
    countries.remove(c)
    cols = [PALETTE[t] for t in df.category[c]]
    if len(cols) == 1: return cols[0]
    else: return Stripe(20, *cols)

world_map = map_chart("maps/World.png", colorfn)

legend = generate_legend([PALETTE[c] for c in ["a", "p", "o", "?"]], [
"from Tupi //nanas// ('excellent fruit'), mainly via French //ananas//",
"from Latin //pīnus// ('pine'), mainly via Spanish //piña// or English //pineapple//", 
"from various other sources", 
"unknown"
], header="MAIN WORD(S) FOR PINEAPPLE", box_sizes=(200,65), box_mask=Image.open("icons/pineapple.png").as_mask(), max_width=600, font_family=partial(arial, 22))
chart = world_map.place(legend, align=(0,1), padding=25)

title = Image.from_column([
Image.from_text("ANANAS VERSUS THE WORLD", arial(72, bold=True)),
Image.from_text("countries where most people call pineapple ‘ananas’, and ones where they don't", arial(36, italics=True))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)

df = pd.read_csv("datasets/etymananas2.csv")
def listfn(type):
    # Unicode workarounds generated with https://vincent7128.github.io/text-image/
    return Image.from_array([
    [ Image.from_text("{} ({})".format(d.language, d.population), UFONT(24, bold=True)),
      Image.open("text/{}.png".format(d.language)) if os.path.exists("text/{}.png".format(d.language)) else
      Image.from_markup(d.word, partial(UFONT, 24), max_width=400) ]
    for _,d in df.iterrows() if d.type == type], bg="white", padding=(4,1), xalign=(1,0))
    
examples = Image.from_column([Image.from_text("FROM LATIN PĪNUS:", UFONT(24, bold=True)), listfn("p"), Image.from_text("OTHER NON-ANANASIANS:", UFONT(24, bold=True), padding=(0,10,0,0)),listfn("a")], padding=2)
imgwords = Image.from_row([img, examples], bg="white", padding=(5,0))
imgwords.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
imgwords.save("output/etymananas.png")