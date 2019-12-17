from math import ceil
from pathlib import Path
from typing import Sequence

from pudzu.pillar import *
from pudzu.dates import *
from pudzu.experimental.bamboo import *

FONT = sans
W1, W2 = 100, 420
PALETTE = {"b": VegaPalette10.RED, "n": VegaPalette10.ORANGE, "c": VegaPalette10.GREEN, "w": VegaPalette10.BLUE, "j": VegaPalette10.BROWN }
bg, fg = RGBA("white"), RGBA("black")

def to_date(d: str) -> Date:
    match = re.match(r"^(\d{4})(?: ([A-Z][a-z]{2})(?: (\d{2}))?)?$", d.replace(" "," "))
    if not match: raise ValueError(f"Invalid date: '{d}'")
    year, month, day = match.groups()
    if month is None: return ApproximateDate(int(year), DatePrecision.YEAR)
    month = next(i for i,m in enumerate(WesternCalendar.MONTHS, 1) if m[:3] == month)
    if day is None: return ApproximateDate((int(year), month), DatePrecision.MONTH)
    return ApproximateDate((int(year), month, int(day)), DatePrecision.DAY)

df = pd.read_csv("datasets/eumaps.csv")
df = df.assign_rows(d=lambda r: to_date(r.date)).sort_values("d")

def make_row(r: pd.Series):
    bg = "#FFFF80" if "M" in r.type else "#CCCCCC" if "O" in r.type else "white"
    fg = PALETTE[r.type[0]]
    if "L" in r.type: fg = fg.blend("#CCCCCC", 0.3)
    bold, italics = "M" in r.type, "L" in r.type
    font = FONT(16, bold=bold, italics=italics)
    date = Image.from_text(r.date, font, fg=fg, bg=bg, max_width=W1-4, beard_line=True, padding=2)
    description = Image.from_text(r.description, font, fg=fg, bg=bg, max_width=W2-4, beard_line=True, padding=2)
    row = Image.from_row([date.pad_to_aspect(W1, date.height, 0, bg),
                          description.pad_to_aspect(W2, description.height, 0, bg)], bg=bg)
    return row

rows = [make_row(r) for _, r in tqdm.tqdm(df.iterrows())]
headers = [Image.open(n).crop_to_aspect(1.23, align=1).resize_fixed_aspect(width=W1+W2) for n in sorted(Path(".").glob("maps/eumaps/*"))]
column_height = sum(i.height for i in rows) / len(headers)
bare_columns = list(generate_subsequences(rows, lambda r: True, lambda r, rs: sum(i.height for i in rs) >= column_height-10))
columns = [Image.from_column([h]+column) for h,column in zip(headers, bare_columns)]
grid = Image.from_row(columns, yalign=0, bg="white")

title = Image.from_text_justified("A guide for dating European maps published after 1900".upper(), grid.width, 80, partial(FONT, bold=True), bg="white", padding=20)

legend = Image.from_multitext(["Changes to: ", "country border", " / ", "country name", " / ", "city name", " / ", "body of water", " / ", "bridge",
                               "             Change is: ", "major change", " / ", "limited recognition", " / ", "outside Europe"],
                              [FONT(24), FONT(24), FONT(24), FONT(24), FONT(24), FONT(24), FONT(24), FONT(24), FONT(24), FONT(24),
                               FONT(24), FONT(24, bold=True), FONT(24), FONT(24, italics=True), FONT(24), FONT(24)],
                              [fg, PALETTE["b"], fg, PALETTE["n"], fg, PALETTE["c"], fg, PALETTE["w"], fg, PALETTE["j"],
                               fg, fg, fg.blend("#CCCCCC", 0.3), fg, fg, fg],
                              [bg, bg, bg, bg, bg, bg, bg, bg, bg, bg,
                               bg, "#FFFF80", bg, bg, bg, "#CCCCCC"], beard_line=True).pad(20, "white")

subtitle = Image.from_markup("based on a list produced by Sasha Trubetskoy ([[@sasha_trub]]); maps are from [[History of Europe: Every Year]] YouTube video by Cottereau", partial(FONT, 24), bg="white", padding=(0,0,0,20))

img = Image.from_column([title, grid, legend, subtitle], bg="white").pad((20,0), bg="white")
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/eumaps.png")

