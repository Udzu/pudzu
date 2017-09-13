import sys
sys.path.append('..')

from charts import *

DEFAULT_IMG = "http://www.socialstudiesforkids.com/graphics/edwardtheconfessor-color.jpg"
TOP_BAR_BG = RGBA(230, 230, 240, 255)
BOT_BAR_BG = RGBA(230, 230, 240, 255)

df = pd.read_csv("datasets/wikibirths_states.csv").set_index("state")
states = pd.read_csv("datasets/usstates.csv")
statetable = pd.DataFrame([[first_or_default([dict(d) for _,d in states[(states.grid_x == x) & (states.grid_y == y)].iterrows()]) for x in range(states.grid_x.max()+1)] for y in range(states.grid_y.max()+1)])

def cell(d):
    if d is None: return Image.EMPTY_IMAGE
    person = df.loc[d['name']]
    
    img = Image.from_url_with_cache(get_non(person, 'image_url', DEFAULT_IMG))
    img = img.crop_to_aspect(200, 180, (0.5, 0.2)).resize_fixed_aspect(width=200)
    
    top = Image.new("RGBA", (200, 35), TOP_BAR_BG)
    code = Image.from_text(d['code'], arial(28, bold=True), fg="black", bg=TOP_BAR_BG)
    top.place(code, copy=False)
    
    bot = Image.new("RGBA", (200, 35), BOT_BAR_BG)
    name = Image.from_text(person['link'], arial(16, bold=True), fg="black", bg=BOT_BAR_BG)
    description = Image.from_text(person['description'], arial(16), fg="black", bg=BOT_BAR_BG, max_width=200)
    content = Image.from_column([name, description, ], bg=BOT_BAR_BG)
    bot.place(content, copy=False)
    
    return Image.from_column([top,img,bot])

grid = grid_chart(statetable, cell, bg="white")

title = Image.from_column([
Image.from_text("Famous Historical Figures by US State", arial(60, bold=True), fg="black", bg="white").pad((10,0), bg="white"),
Image.from_text("the most famous dead historical figure born in each state, according to English Wikipedia", arial(36, bold=True), fg="black", bg="white").pad((10,0,10,2), bg="white")
], bg="white").pad((0,10),bg="white")
comment = Image.from_text("blah di blah", arial(24), fg="black", bg="white").pad((0,20,0,5),bg="white")

chart = Image.from_column([title, grid, comment], bg="white")

# James Brown, Davy Crocket, Andrew Johnson, Stonewall Jackson
