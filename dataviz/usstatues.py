
from pudzu.charts import *


DEFAULT_IMG = "http://www.socialstudiesforkids.com/graphics/edwardtheconfessor-color.jpg"
TOP_BAR_BG = RGBA(230, 230, 240, 255)
BOT_BAR_BG = RGBA(230, 230, 240, 255)

states = pd.read_csv("datasets/usstates.csv")
statetable = pd.DataFrame([[first([dict(d) for _,d in states[(states.grid_x == x) & (states.grid_y == y)].iterrows()]) for x in range(states.grid_x.max()+1)] for y in range(states.grid_y.max()+1)])


df = pd.read_csv("datasets/usstatues.csv").set_index("state")

PALETTE = { "c": VegaPalette10.RED,
            "f": VegaPalette10.RED,
            "n": VegaPalette10.GREEN,
            "w": VegaPalette10.BLUE,
            "a": VegaPalette10.BROWN,
            "x": "#AAAAAA" }

def cell(d):
    if d is None or d['code'] == "PR": return Image.EMPTY_IMAGE
    
    if d['name'] not in df.index:
        img = Image.new("RGBA", (200, 180), "#777777" if d['code'] == "DC" else "#AAAAAA")
    else:
        person = df.loc[d['name']]
        names = person["names"].split(",")
        groups = person["groups"].split(",")
        people = []
        for n,g in zip_equal(names, groups):
            colors = [PALETTE[x] for x in g]
            size = (200, 180 // len(names))
            if len(colors) == 1:
                i = Rectangle(size, colors[0])
            else:
                i = Image.from_pattern(Stripe(40, *colors), size)
            if n is not None:
                i.place(Image.from_text(n, arial(16, bold=True), fg="black"), copy=False)
            people.append(i)
        img = Image.from_column(people)
        
    top = Image.new("RGBA", (200, 35), TOP_BAR_BG)
    code = Image.from_text(d['code'], arial(28, bold=True), fg="black")
    top.place(code, copy=False)
    
    return Image.from_column([top,img])

grid = grid_chart(statetable, cell, bg="white").pad(10, "white")

title = Image.from_column([
Image.from_text("Statues of the National Statuary Hall Collection".upper(), arial(74, bold=True), fg="black", bg="white").pad((10,0), bg="white"),
Image.from_text("2 statues selected by each state to represent it at the United States Capitol in Washington D.C. (plus former statues in parentheses)", arial(36, italics=True), fg="black", bg="white", align="center", padding=(0,2)).pad((10,10,10,5), bg="white")
], bg="white").pad((0,20,0,30),bg="white")

birth_footnotes = [
"In 2019, Arkansas voted to replace Clarke and Rose with Johnny Cash and Daisy Lee Gatson Bates, but this hasn't happened yet.",
"In 2020, Virginia voted to replace Lee with Barbara Rose Johns, but while Lee's statue was removed immediately Johns' statue is still pending.",
"Clarke (AR) and Aycock (NC) were prominent postbellum white supremacists, Calhoun (SC) a prominent antebellum one.",
"Kenna (WV) served as a Confederate soldier as a child but was not otherwise associated with the Confederate cause."
]
comment = Image.from_text("*" + "\n ".join(birth_footnotes), arial(24, italics=True), fg="black", bg="white").pad((0,1,0,0), "black").pad((0,20,0,10),bg="white")


boxes = [Rectangle((40,40), PALETTE[n]).place(Image.from_text(s, arial(16), "white")) for n,s in zip("cwna", ["13*","11*","7","1*"])]

leg = generate_legend(boxes, ["Confederates/white supremacists","Women","Indigenous Americans", "African Americans"], font_family=partial(arial, 24),
    header = "Statues depicting...".upper(),
    footer = "*The 13 confederate statues includes 3 that have since been removed and 2 that are scheduled to be. Planned replacements include 2 women and 1 African American.",
    max_width=500)


grid.place(leg, align=(0.15,0), copy=False, padding=25)

chart = Image.from_column([title, grid, comment], bg="white")
chart.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
chart.save("output/usstatues.png")

