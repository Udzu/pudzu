from pudzu.charts import *
from string import ascii_lowercase as lc

df = pd.read_csv("datasets/twoletters.csv")
groups = { w : t[0] for t in df.itertuples() for w in t[2].split(' ') }
palette = [ "#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4", "#fed9a6", "#ffffcc", "#e5d8bd", "#fddaec" ]
labels = [ "Functional words: //be//, //of//, //to//,...", "Interjections: //hm//, //ow//, //yo//,...", "Letter names: //ar//, //ef//, //pi//,...", "Solfège notes: //re//, //mi//, //fa//,...", "Contractions: //ad//, //bi//, //za//,...", "Foreignisms: //aa//, //qi//, //zo//,...", "Dialectal words: //ae//, //ch//, //un//,...", "Other words: //ax//, //ma//, //pa//,..." ]

def box(word):
    return Rectangle(45, "white" if word not in groups else palette[groups[word]]).place(Image.from_text(word.upper(), arial(16, bold=True), "#F0F0F0" if word not in groups else "black"))
    
grid = Image.from_array([[box(r+c)  for c in lc] for r in lc]).pad(1, "black")
grid.save("output/twolettersgrid.png")

def legbox(i):
    return Rectangle(40, palette[i]).place(Image.from_text(str(sum(1 for _,j in groups.items() if i==j)), arial(16, bold=True)))
    
legend = generate_legend([legbox(i) for i in range(len(palette))], labels, font_family=partial(arial, 24), header="WORD CATEGORIES", footer="Words in multiple categories are included under their most common meaning.", max_width=400)

chart = Image.from_row([grid, legend], bg="white", yalign=0, padding=10)
title = Image.from_text("A categorisation of two-letter English words".upper(), arial(48))
subtitle = Image.from_text("based on the Collins Scrabble Words tournament wordlist", arial(36))
img = Image.from_column([title, subtitle, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/twoletters.png")