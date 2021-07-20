from pudzu.charts import *

FONT=sans
bg = "#67d7d0"
fg = "#a8e7e4"
tg = "#555555"


words = [
(
    "é",
    "café",
    "acute accent",
    """From Latin //acūta// (“sharp”), a calque of the Greek //oxeîa//. Originally used to indicate syllables with high pitch."""
),
(
    "à",
    "à la mode",
    "grave accent",
    """From Latin //gravis// (“heavy”), a calque of the Greek //barús//. Originally used to indicate syllables with low pitch."""
),
(
    "û",
    "crème brûlée",
    "circumflex",
    """From Latin //circumflexus// (“bent around”), a calque of the Greek //perispōménē//. Originally used to indicate syllables with a high-low pitch contour."""
),
(
    "ï",
    "naïve",
    "diaeresis, umlaut",
    """From Greek //diaíresis// (“division”) indicating syllable separation; or from German //Umlaut// (lit. around sound) indicating sound change."""
),
(
    "ç",
    "façade",
    "cedilla",
    """From Spanish //cedilla// (little Z) due its resemblance to a subscript cursive z. Originates from Visigothic script."""
),
(
    "ñ",
    "jalapeño",
    "tilde",
    """From Latin //titulus// (“title, superscription”), originally used to indicate omitted letters.""",
),
(
    "ā",
    "Māori",
    "macron",
    """From Greek makrón (“long”). Originally used to indicate long or heavy syllables.""",
),
(
    "i",
    "İstanbul",
    "tittle",
    """From Medieval Latin //titulus// (“small stroke) from Latin //titulus//. Doublet of tilde. Turkish distinguishes between dotless ı and dotted i.""",
),
(
    "å",
    "ångström",
    "overring",
    """From Proto-Germanic //*ubar-// (“over”) and //*hringaz// (“ring”)"""
),
(
    "ą",
    "pączek",
    "ogonek",
    """From Polish //ogonek// (“little tail”)."""
),
(
    "ă",
    "pastramă",
    "breve",
    """From Latin //brevis// (“short, brief”), a calque of the Greek //brachy//. Originally used to indicate short syllables."""
),
(
    "ř",
    "Dvořák",
    "caron, háček",
    """Possibly a blend of //caret// (from Latin “it lacks” due to its use in proofreading) and //macron//; from Czech //háček// (lit. small hook).""",
),
]

def bubble(word, example, meaning, etymology):
    text = Image.from_column(
        [Image.from_multitext([word, " as in ", example], [FONT(48, bold=True), FONT(24), FONT(24, italics=True)], tg, beard_line=True),
         Image.from_text(meaning, FONT(24, bold=True), tg, beard_line=True, padding=(0,5)),
         Image.from_markup(etymology, partial(FONT, 16), tg, max_width=250, padding=(0,10))])
    rectangle = Rectangle((text.width+50, text.height+50), fg, round=50).pad(20, bg=None)
    rectangle = rectangle.add_shadow(tg, offset=(5,5), blur=6)
    return rectangle.place(text)


grid = list(generate_batches([bubble(*word) for word in words], 4))
grid = Image.from_array(grid, padding=0, bg=bg)
title = Image.from_text_bounded("Diacritical mark names and etymologies".upper(), grid.size, 40, partial(FONT, bold=True), tg, bg, padding=(0,35,0,25))
img = Image.from_column([title, grid], bg=bg)
img.save("output/etymdiacritics.png")


