import sys
sys.path.append('..')

from charts import *

DEFAULT_IMG = "http://www.socialstudiesforkids.com/graphics/edwardtheconfessor-color.jpg"
TOP_BAR_BG = RGBA(230, 230, 240, 255)
BOT_BAR_BG = RGBA(230, 230, 240, 255)

states = pd.read_csv("datasets/usstates.csv")
statetable = pd.DataFrame([[first([dict(d) for _,d in states[(states.grid_x == x) & (states.grid_y == y)].iterrows()]) for x in range(states.grid_x.max()+1)] for y in range(states.grid_y.max()+1)])

for births in [True, False]:

    df = pd.read_csv("datasets/wiki{}_states.csv".format("births" if births else "deaths")).set_index("state")

    def cell(d):
        if d is None: return Image.EMPTY_IMAGE
        person = df.loc[d['name']]
        
        img = Image.from_url_with_cache(get_non(person, 'image_url', DEFAULT_IMG))
        img = img.crop_to_aspect(200, 180, (0.5, 0.2)).resize((200, 180))
        
        top = Image.new("RGBA", (200, 35), TOP_BAR_BG)
        code = Image.from_text(d['code'], arial(28, bold=True), fg="black", bg=TOP_BAR_BG)
        top.place(code, copy=False)
        
        bot = Image.new("RGBA", (200, 35), BOT_BAR_BG)
        name = Image.from_text(person['link'], arial(16, bold=True), fg="black", bg=BOT_BAR_BG)
        description = Image.from_text(person['description'], arial(16), fg="black", bg=BOT_BAR_BG, max_width=200)
        content = Image.from_column([name, description, ], bg=BOT_BAR_BG)
        bot.place(content, copy=False)
        
        return Image.from_column([top,img,bot])

    grid = grid_chart(statetable, cell, bg="white").pad(10, "white")

    title = Image.from_column([
    Image.from_text("Most famous {} in each US state/territory, according to Wikipedia".format("dead individuals born" if births else "individuals who died"), arial(54, bold=True), fg="black", bg="white").pad((10,0), bg="white"),
    Image.from_text("(restricted to deceased figures listed in Wikipedia's yearly Births sections; fame measure is a combination of article length, revisions and pageviews)", arial(32, italics=True), fg="black", bg="white", align="center", padding=(0,2)).pad((10,0,10,5), bg="white")
    ], bg="white").pad((0,10,0,20),bg="white")
    
    birth_footnotes = [
    "Stonewall Jackson was born in Clarksburg when it was still part of Virginia. Second is mathematician John Nash.",
    "Washington was born in Bridges Creek when it was still part of the Colony of Virginia. The top US-born Virginian is president Woodrow Wilson.",
    "Davy Crockett was born in Greene County when it was part of the unrecognized State of Franklin. Second is Confederate general Nathan Bedford Forrest.",
    "Both Brown and Johnson are beaten by president Andrew Jackson, who was born in the Waxhaws on the border of North and South Carolina.",
    "Liliuokalani was born in Honolulu when it was still part of the Kingdom of Hawaii. The top US-born Hawaiian is musician Israel Kamakawiwoʻole."
    ]
    death_footnotes = ["The most famous American citizen to die in Hawaii was aviator Charles Lindbergh."
    ]
    comment = Image.from_text("*" + "\n ".join(birth_footnotes if births else death_footnotes), arial(24, italics=True), fg="black", bg="white").pad((0,1,0,0), "black").pad((0,20,0,10),bg="white")

    chart = Image.from_column([title, grid, comment], bg="white")
    chart.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
    chart.save("output/wiki{}_states.jpg".format("births" if births else "deaths"))

# James Brown, Davy Crocket, Andrew Johnson, Stonewall Jackson
