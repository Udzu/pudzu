from pudzu.charts import *

label, fg, bg = "#ffd152", "#efdab9", "#343233"
df = pd.read_csv("datasets/filmsfuture.csv")
columns = 3

def make_row(r):
    return [
        Image.from_text(r.year.replace('\\n','\n'), sans(36, bold=True), label),
        Image.from_text(f"{r.film.upper()}", sans(24, bold=False), fg, max_width=250),
        Image.from_url_with_cache(r.image).cropped_resize((320,160)) if nnn(r.image) else None,
    ]

array = [make_row(r) for _,r in df.iterrows()]
grids = list(generate_batches(array, ceil(len(array) / columns)))
charts = [Image.from_array(grid, bg=bg, xalign=(1,0,0), padding=(10,0)) for grid in grids]
chart = Image.from_row(charts, bg=bg, yalign=0)

TITLE = f"IN THE NOT SO DISTANT FUTURE..."
title = Image.from_text_justified(TITLE, chart.width-50, 80, partial(sans, bold=True), fg=label, bg=bg, padding=(0,20,0,0))
SUBTITLE = f"{len(df)} SCI-FI FILMS SET DURING THE 2000s"
subtitle = Image.from_text_justified(SUBTITLE, chart.width-200, 60, partial(sans, bold=True), fg=fg, bg=bg, padding=(0,0,0,20))

FOOTER = "¹ set during the last two days of 1999    ² setting of future scenes    ³ setting of start scenes"
footer = Image.from_text(FOOTER, sans(24), fg, bg, padding=10)

img = Image.from_column([title, subtitle, chart, footer], bg=bg, padding=(0,10))
img.place(Image.from_text("/u/Udzu", sans(24), fg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)

img.convert("RGB").save("output/filmsfuture.jpg")
