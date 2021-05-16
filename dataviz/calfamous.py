from wikiscrape import *
from pudzu.sandbox.wikipage import *
from pudzu.dates import *
from pudzu.charts import *


def analyze_date(date, sections=1):
    wp = WikiPage(date)
    people = find_tags(
        wp.bs4,
        all_("span", id="Births"),
        parents_("h2"),
        next_siblings_("ul", limit=sections),
        all_("li"),
        all_("a", href=lambda s: s.startswith("/wiki/") and s[6] not in "0123456789", limit=1),
    )
    links = [a["href"].replace("/wiki/", "") for a in people if "https://" not in a["href"]]
    df = score_by_name(links)
    return df


fg, bg = "white", "black"
DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

df = pd.read_csv("datasets/calfamous.csv", dtype="object").set_index("date")
df.image = df.image.fillna(DEFAULT_IMG)
df.born = df.born.fillna("?")
df.died = df.died.fillna("?")
df.description = df.description.fillna("???")

array = pd.DataFrame(
    [[df.loc[date] if date in df.index else None for d in range(1, 32) for date in [f"{WesternCalendar.MONTHS[m]} {d}"]] for m in range(0, 12)],
    index=WesternCalendar.MONTHS,
    columns=list(range(1, 32)),
)


def cell(row):
    if row is None:
        return None
    img = Image.from_url_with_cache(row.image)
    box = Image.new("RGB", (180, 220), bg)
    box = box.place(
        Image.from_column(
            [
                img.crop_to_aspect(100, 100, tmap(float, (get_non(row, "align", 0.5), get_non(row, "align", 0.2)))).resize_fixed_aspect(width=160),
                Image.from_text(row.title, arial(12, bold=True), padding=(3, 5, 3, 2), fg=fg, bg=bg),
                Image.from_text(f"({row.born}–{row.died})", arial(12), padding=(3, 0, 3, 0), fg=fg, bg=bg),
                Image.from_text(row.description, arial(12), padding=(3, 0, 3, 0), fg=fg, bg=bg),
            ],
            bg=bg,
        )
    )
    return box


def col_label(column):
    return Image.from_text(str(array.columns[column]), arial(48, bold=True), padding=20, fg=fg)


def row_label(row):
    return Image.from_text(array.index[row].upper(), arial(48, bold=True), padding=20, fg=fg)


chart = grid_chart(array, cell, col_label=col_label, row_label=row_label)

FONT = sans
TITLE = "The most famous deceased person born on each day of the year"
SUBTITLE = "based on Wikipedia article lengths, revision counts and monthly views, averaged across different language Wikipedias"
FOOTER = "* Old Style date, prior to local adoption of the Gregorian Calendar  ** official birthday: actual date unknown"

img = Image.from_column([
    Image.from_text(TITLE.upper(), FONT(140, bold=True), "white"),
    Image.from_text(SUBTITLE, FONT(70, italics=True), "white"),
    chart,
    Image.from_text(FOOTER, FONT(60, italics=True), "white", line_spacing=5)
], padding=20, bg="black")

img.place(Image.from_text("/u/Udzu", FONT(32), fg="white", bg="black", padding=10).pad((2,2,0,0), "white"), align=1, padding=20, copy=False)
   
img.save("output/calfamous.png")
