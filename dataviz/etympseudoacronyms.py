from pudzu.charts import *

FONT=sans
bg = "#67d7d0"
fg = "#a8e7e4"
tg = "#555555"


words = [
(
    "SOS",
    "Morse code distress signal",
    """Does //not// stand for **Save Our Souls**.

SOS is a distinct Morse code sequence consisting of three dots / three dashes / three dots (with no spaces between the letters) and doesn't stand for anything. The letters SOS are just a mnemonic: it could equally be described as IWB, VZE, 3B or V7."""
),
(
    "ISO",
    "standardization organisation",
    """Does //not// stand for **International Standardization Organization**.

To avoid having different acronyms in English (IOS), French (OIN) and Russian (MOC), the International Organization for Standardization adopted ISO as its abbreviated name, in reference to the Greek word ίσος, meaning 'equal'."""
),
(
    "UTC",
    "international time standard",
    """Does //not// stand for **Universal Time Clock**.

UTC was a compromise between the English proposal of CUT ('coordinated universal time') and the French proposal of TUC ('temps universel coordonné'). It also conforms to the pattern of the earlier Universal Time system (UT0, UT1, etc)."""
),
(
    "ICQ",
    "messenger client",
    """Derives from the English phrase 'I Seek You'."""
),
(
    "Windows XP",
    "operating system",
    """XP is short for 'eXPerience' and apparently symbolises "the rich and extended user experiences Windows and Office can offer by embracing Web services that span a broad range of devices"."""
),
(
    "xkcd",
    "webcomic",
    '''"It's just a word with no phonetic pronunciation — a treasured and carefully-guarded point in the space of four-character strings."'''
)
]

def bubble(word, meaning, etymology):
    text = Image.from_column(
        [Image.from_text(word, FONT(36, bold=True), tg, beard_line=True),
         Image.from_text(meaning, FONT(18, italics=True), tg, beard_line=True, padding=(0,5)),
         Image.from_markup(etymology, partial(FONT, 16), tg, max_width=250, padding=(0,10))])
    rectangle = Rectangle((text.width+50, text.height+50), fg, round=50).pad(20, bg=None)
    rectangle = rectangle.add_shadow(tg, offset=(5,5), blur=6)
    return rectangle.place(text)


grid = list(generate_batches([bubble(*word) for word in words], 3))
grid = Image.from_array(grid, padding=0, bg=bg)
title = Image.from_text_bounded("6 ‘acronyms’ that don't stand for anything".upper(), grid.size, 36, partial(FONT, bold=True), tg, bg, padding=(0,30,0,20))
img = Image.from_column([title, grid], bg=bg)
img.save("output/etympseudoacronyms.png")


