import sys
sys.path.append('..')
from charts import *
from bamboo import *

# generate map
df = pd.read_csv("datasets/eunavajo.csv").set_index("country")
PALETTE = ['#3c7f6b', '#79aa73', 'grey']
PALETTE.insert(1, Rectangle(40, Stripe(10, PALETTE[0], PALETTE[1])))
FONT = calibri

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return PALETTE[-1]
    elif non(df.meaning[c]): return PALETTE[0]
    elif c in ["Netherlands", "Montenegro", "Iceland"]: return PALETTE[1]
    else: return PALETTE[2]
    
def labelfn(c, w,h):
   if c in ["Moldova", "Belarus", "Kosovo"]: return Image.from_text("?", FONT(16, bold=True))
   if c not in df.index: return None
   return first((img for sz in range(16,6,-1) for img in [Image.from_column([
        Image.from_text(df.name[c], FONT(sz, bold=True), max_width=w, align="center"),
        Image.EMPTY_IMAGE if non(df.meaning[c]) else Image.from_text("({})".format(df.meaning[c]), FONT(sz-2), max_width=w, align="center")
    ])] if img.width <= w and img.height <= h), None)
    
map = map_chart("maps/Europe.png", colorfn, labelfn)
legend = generate_legend(PALETTE, [
"**direct loans**, typically via English.",
"**loan-translations**, a.k.a. calques.",
"**neologisms**, mostly coined during WWII for use by Code Talkers and used since.",
"**unknown**"
], header="EXONYM ETYMOLOGY", box_sizes=40, max_width=350)
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("European country names in Navajo".upper(), arial(48, bold=True)),
Image.from_text("iron-hat-people land and other WWII Code Talker neologisms", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eunavajo.png")
