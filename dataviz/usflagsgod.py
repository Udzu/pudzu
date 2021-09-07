from pudzu.charts import *
from pudzu.sandbox.bamboo import *

god = { "Mississippi", "Florida", "Georgia",
"Mississippi", "South Dakota",
}
name = { "Arkansas", "California", "Florida", 
"Idaho", "Illinois", "Iowa", "Kansas",
"Kentucky", "Maine", "Minnesota", "Nevada",
"Montana", "Nebraska", "New Hampshire", 
"North Dakota",  "Oklahoma", "Oregon", "Indiana",
"South Dakota", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin",  "Wyoming",
}
initials = { "North Carolina", "Ohio", "Colorado" }

flags = pd.read_csv("datasets/usstates.csv").set_index("name").flag

# EStonia-Finland, UK-Liechtenstein, Greece-Cyprus

# generate map
PALETTE = [VegaPalette10.BLUE, VegaPalette10.LIGHTBLUE, VegaPalette10.RED]
LABELS = [
"contains state name",
"contains state initials",
"mentions God",
]
PALETTE = PALETTE[:len(LABELS)]

FONT = sans

def colorfn(c):
    print(c)
    if c == "   ": print("XXXXXXXXXXXXXX")
    if c in ['Sea', 'Borders']: return "white"
    if c in god and c in name: return Stripe(20, PALETTE[0], PALETTE[2])
    if c in initials: return PALETTE[1]
    if c in god: return PALETTE[2]
    if c in name: return PALETTE[0]
    return "grey"
    
def labelfn(c, w,h):
   if c not in flags: return None
   return Image.from_url_with_cache(flags[c]).to_rgba().resize_fixed_aspect(width=min(w-2, 60), height=h-2).pad((1,0,0,0) if c == "Ohio" else 1, "grey")
   
map = map_chart("maps/USA.png", colorfn, labelfn)

legend = generate_legend(PALETTE, LABELS, header="STATE FLAG", box_sizes=40, font_family=partial(FONT, 24))

chart = map.place(legend, align=(1,0.8), padding=10)

title = Image.from_text("US state flags that mention their own name or God".upper(), arial(48, bold=True), padding=10)

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/usflagsgod.png")
