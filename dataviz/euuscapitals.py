from pudzu.charts import *
from pudzu.experimental.bamboo import *

# visualisation
df = pd.read_csv("datasets/euuscapitals.csv").fillna(False)
map = Image.open("maps/USACanada.png")
COLOR = '#a91016'

def circle(r, bg):
    img = Image.new("RGBA", (2*r, 2*r))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, 2*r-1, 2*r-1), fill=bg)
    return img
    
def square(r, bg):
    return Image.new("RGBA", (2*r, 2*r), bg)
    
def cross(r, bg):
    img = Image.new("RGBA", (2*r, 2*r))
    img = img.place(Image.new("RGBA", (2*r, r//2), bg))
    img = img.place(Image.new("RGBA", (r//2, 2*r), bg))
    return img
    
def choose(population, list):
    if population >= 100000: return list[0]
    elif population >= 10000: return list[1]
    else: return list[2]
    
def box(population):
    return choose(population, [square, circle, cross])(20, COLOR).resize_fixed_aspect(scale=0.25)
    
def label(name, population):
    size = choose(population, [28, 24, 20])
    bold = choose(population, [True, True, False])
    return Image.from_text(name, arial(size, bold=bold), COLOR, align="center", padding=(0,0,0,4))
    
def city_label(name, population, above=False):
    dot = box(population)
    text = label(name, population)
    return Image.from_column([text, dot] if above else [dot, text], bg=0)
    
def add_cities(img, cities):
    img = img.copy()
    for _, d in cities.iterrows():
        if d.above:
            img = img.pin(city_label(d.city, d.population, True), (d.x, d.y+5), (0.5, 1))
        else:
            img = img.pin(city_label(d.city, d.population, False), (d.x, d.y-5), (0.5, 0))
    return img
  
map = add_cities(map, df)

lpops = [100000, 10000, 1000]
lfooter = "\n• ".join(["Map is limited to places with 1000+ residents and shows only the largest example for each name. Smaller locations that were omitted include:\n", "Copenhagen NY (pop 801)", "Oslo MN (pop 330)", "Kief ND (pop 13)", "Reykjavik MB (small community)", "Vatican LA (small community)", "Sofia NM (ghost town)", "Budapest GA (ghost town)"]) + "\n\nThere is also an Agram Township MN (pop 534), named using Zagreb's old German name, and an Angora Township MN (pop 249), named using Ankara's old English name."
lheader = "By population"
legend = generate_legend([box(p) for p in lpops], [label(" {:,}+ residents".format(p), p) for p in lpops], footer=lfooter, header=lheader, max_width=300)

nfooter = "\n• ".join(["Pronunciations are as expected, with the following exceptions:\n", 
"Berlin is BER-lin, not ber-LIN.",
"Madrid is MAD-rid, not mad-RID.",
"Prague is PRAYG, not PRAHG.",
"Riga is RYE-guh, not REE-guh.\n",
"(Athens is pronounced normally, unlike Athens IL or Athens KY, which are pronounced AY-thens)",
"(Vienna is pronounced normally, unlike Vienna IL or Vienna SD, which are pronounced vye-EH-nuh)"
])
note = generate_legend([], [], footer=nfooter, header="By pronunciation", max_width=280)

img = Image.from_row([map, Image.from_column([legend, note.pad((0,20,0,0), "white")], bg="white", xalign=0)], yalign=0, bg="white", padding=10)

title = Image.from_text("Capital cities of Europe: North American edition".upper(), arial(60, bold=True))
img = Image.from_column([title, img], bg="white", padding=(0,10))
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euuscapitals.png")
