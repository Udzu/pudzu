# FALSE COGNATES

from pudzu.charts import *

#FONT=sans
font_path = "liberation2/LiberationSans"

def ff(path, names): return [path+name for name in names]

FONT = font_family(["/usr/share/fonts/truetype/liberation2/LiberationSans-Regular",
"/usr/share/fonts/truetype/liberation2/LiberationSans-Italic",
"/usr/share/fonts/truetype/liberation2/LiberationSans-Bold",
"/usr/share/fonts/truetype/liberation2/LiberationSans-BoldItalic"]
)

bg = "#67d7d0"
fg = "#a8e7e4"
tg = "#555555"

male = """**MALE**
< Old French //malle//
< Latin //masculus//
= dim. of //mās// ("man")
? //origin unknown//"""

female = """**FEMALE**
< Old French //femele//
< Latin //femella// ("girl")
= dim. of //femina// ("woman")
< PIE //*dʰeh-m̥hn-éh// ("breastfeeder")
~ //cognate with doe//"""

man = """**MAN**
< Old Eng //mann// ("person")
< Proto-Germanic //*mann//
< PIE //*mon-//"""

human = """**HUMAN**
< Middle French //humain//
< Latin //hūmānus// < //humus//
< PIE //*dʰǵʰomós// ("earthling")
~ //cognate with groom//"""

homosapiens = """**HOMO** SAPIENS
< Latin //homo// ("man")
< PIE //*ǵʰm̥mṓ// ("earthling")
~ //cognate with groom//"""

homosexual = """**HOMOSEXUAL**
< German //Homosexual//
< Greek //homos// ("same")
< PIE //*somHós//
~ //cognate with "same"//"""

island = """**ISLAND**
< Old Eng //īġland//
< Proto-Germanic //*awjōlandą//
< PIE //*hekʷeh// ("water")
   + //*landą// ("land")"""

isle = """**ISLE**
< Old French //ille//
< Latin //insula//
? //origin unknown//"""


emoticon = """**EMOTICON**
< Blend of //emotion// + //icon//
< Latin //ēmōtus// (lit. "moved out")
   + Greek //eikṓn// ("image")"""

emoji = """**EMOJI**
< Japanese //emoji//
= //e// ("picture")
   + //moji// ("character")"""

pencil = """**PENCIL**
< Old French //pincil//
< Latin //pēnicillum// ("brush")
= dim. of //pēnis// ("tail")
< PIE //*pes-// ("penis")
~ //cognate with penis//"""

pen = """**PEN**
< Old French //penne//
< Latin //penna// (“feather”)
< PIE //péthr̥//
~ //cognate with feather//"""

mouse = """**MOUSE**
< Old Eng //mūs//
< Proto-Germanic //*mūs//
< PIE //*muhs//"""

dormouse = """**DORMOUSE**(?)
< Middle Eng //dormous//
? maybe Fr //dormouse// ("dormant")
< PIE //*drem-// ("sleep")"""

titmouse = """**TITMOUSE**
< Middle Eng //tit// ("small bird")
   + //mose// ("titmouse")
< Proto-Germanic //*maisǭ//
? //origin unknown//"""

swimmingpool = """SWIMMING **POOL**
< Old Eng //pōl//
< Proto-Germanic //*pōlaz//
< PIE //*bale-// ("bog, marsh")"""

carpool = """CAR **POOL**
< French //poule// ("collective stakes")
? maybe from //poule// ("hen")
< Latin //pulla// ("hen")
< PIE //*polH-// ("animal young")"""

cesspool = """**CESSPOOL**(?)
? maybe Middle Fr //souspirail//  ("air hole")
< Latin //suspirare// ("to sigh")
= //sub-// ("below") + //spirare// ("breathe")
< PIE //*(s)peys-//"""

wood = """**WOOD**
< Proto-Germanic //*widuz//
< PIE //*widʰus// ("tree, beam")"""

woodchuck = """**WOODCHUCK**
< Cree //otchek// ("fisher")
< Objibwe //ojiig//"""

wormwood = """**WORMWOOD**
< Middle Eng //wermode//
< Proto-Germanic //*wermōdaz//
? //origin unknown//
~ //cognate with "vermouth"//"""

cut = """**CUT**
< Old Norse //*kytja//
< Proto-Germanic //*kutjaną//
? //origin unknown//"""

cutlet = """**CUTLET**
< French //côtelette//
< dim of Old French //coste// ("rib")
< Latin //costa//
< PIE //*kost-//"""

cutlass = """**CUTLASS**
< Middle Fr //coutelas// ("large knife")
< aug of Old Fr //coutel// ("knife")
< Latin //cultellus//
? //origin unknown//"""

def bubble(etymologies):
    text = Image.from_row(
        [Image.from_column([
Image.from_markup(etymology[:etymology.index("\n")], partial(FONT, 32, bold=True), tg, beard_line=True, padding=(0,10,0,0)),
Image.from_markup(etymology[etymology.index("\n")+1:], partial(FONT, 16), tg, padding=(0,5,0,10)),
], xalign=0
)
 for etymology in etymologies], padding=(10,0), yalign=0)
    rectangle = Rectangle((text.width+50, text.height+50), fg, round=50).pad(20, bg=None)
    rectangle = rectangle.add_shadow(tg, offset=(5,5), blur=6)
    return rectangle.place(text)


layout = [
 [[male, female], [man, human], [homosapiens, homosexual]],
 [[cut, cutlet, cutlass], [wood, woodchuck, wormwood]],
 [[mouse, titmouse, dormouse], [swimmingpool, carpool, cesspool]], 
 [[island, isle], [pen, pencil], [emoticon, emoji]]]
grid = [[bubble(words) for words in row] for row in layout]
grid = Image.from_column([Image.from_row(row) for row in grid], bg=bg)
title = Image.from_text_bounded("10 sets of English false cognates".upper(), grid.size, 60, partial(FONT, bold=True), tg, bg, padding=(0,30,0,10))
subtitle = Image.from_text_bounded("words that look like they're related but aren't!", grid.size, 36, partial(FONT, italics=True), tg, bg, padding=(0,10,0,20))
img = Image.from_column([title, subtitle, grid], bg=bg)
img.save("output/etymcognates.png")




