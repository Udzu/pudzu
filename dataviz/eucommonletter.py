import sys
sys.path.append('..')
from charts import *
from bamboo import *

df = pd.read_csv("datasets/eucommonletter.csv").set_index("language")
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    if df.letter[c] in "e": return Set1Class9[0]
    elif df.letter[c] in "aαа": return Set1Class9[1]
    elif df.letter[c] in "oо": return Set1Class9[2]
    elif df.letter[c] in "i": return Set1Class9[3]
    
def colorfn2(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    if df.bigram[c] in ["de"]: return Set1Class9[0]
    if df.bigram[c] in ["en", "er", "es"]: return Set1Class9[1]
    if df.bigram[c] in ["на", "na"]: return Set1Class9[2]
    if df.bigram[c] in ["ie", "je", "је"]: return Set1Class9[3]
    return "grey"

def colorfn3(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    if df.trigram[c] in ["ent"]: return Set1Class9[0]
    else: return "grey"
    
def labelfn(c, w, h):
    if c not in df.index: return None
    return Image.from_text_bounded(df.letter[c].replace("\\n", "\n"), (w, h), 32, papply(arial, bold=True), align="center", padding=2)
    
def labelfn2(c, w, h):
    if c not in df.index: return None
    return Image.from_text_bounded(df.bigram[c].replace("\\n", "\n"), (w, h), 32, papply(arial, bold=True), align="center", padding=2)
    
def labelfn3(c, w, h):
    if c not in df.index: return None
    return Image.from_text_bounded(df.trigram[c].replace("\\n", "\n"), (w, h), 32, papply(arial, bold=True), align="center", padding=2)
    
map1 = map_chart("maps/Eurolang.png", colorfn, labelfn)
map2 = map_chart("maps/Eurolang.png", colorfn2, labelfn2)
map3 = map_chart("maps/Eurolang.png", colorfn3, labelfn3)

chart = Image.from_row([map1, map2, map3])

title = Image.from_column([
Image.from_text("The most common letters, letter pairs and letter triplets".upper(), arial(96, bold=True), padding=2),
Image.from_text("in different European languages, based on each language's Wikipedia (source: http://simia.net/letters)", arial(60), padding=2)],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.resize_fixed_aspect(scale=0.5)
img.save("output/eucommonletter.png")
