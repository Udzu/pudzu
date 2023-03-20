from pudzu.charts import *
from pudzu.sandbox.bamboo import *

bg = "#31475e"
fg = "#f0f0f0"
hg = "#ff5555"

for ONE_COL in [True, False]:

    df = pd.read_csv("datasets/etymcomputinglangs.csv", index_col=False).fillna("?")
    if ONE_COL or True: # (if you really need an extra entry to balance)
        df = df[df.word != "Simula"]

    array = []
    for _,r in df.iterrows():
        row = [
            Image.from_text(r['word'], arial(32, bold=True), fg, beard_line=True),
            Image.from_text(f"{r['year']}", arial(24), hg, beard_line=True),
            Image.from_markup(r['description'], partial(arial, 18), fg, beard_line=True, max_width=700)
        ]
        array.append(row)

    def split_list(a_list):
        half = ceil(len(a_list)/2)+1
        if ONE_COL: return a_list,
        return a_list[:half], a_list[half:]

    grid = Image.from_row([Image.from_array(a, padding=(10,5), xalign=(1,0.5,0)*2, yalign=0.5) for a in split_list(array)], yalign=0, padding=(10,0))
    title = Image.from_text_bounded("How computer languages{}got their names".format('\n' if ONE_COL else ' ').upper(), grid.size, 64, partial(arial, bold=True), fg, align="center", line_spacing=10)

    img = Image.from_column([title, grid], bg=bg, padding=15).pad((0,5,0,15), bg)
    img.place(Image.from_text("/u/Udzu", sans(16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10, copy=False)
    img.save("output/etymcomputinglangs{}.png".format("" if ONE_COL else 2))




