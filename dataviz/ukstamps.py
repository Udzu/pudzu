from pudzu.charts import *

fg, bg = "black", "white"
font = arial

df = pd.read_csv("datasets/ukstamps.csv").set_index("name").fillna("").drop(columns=["2d"])

chart = grid_chart(df, 
    cell = lambda v: v and Image.from_url_with_cache(v).to_rgba().resize_fixed_aspect(height=100),
    row_label=lambda r: Image.from_text("{}".format(df.index[r]).upper(), font(24, bold=True), fg=fg, align="center", line_spacing=3, padding=(0,0,10,0)), 
    col_label=lambda c: Image.from_text("{}".format(df.columns[c]), font(24, bold=True), fg=fg, align="center", line_spacing=3),
    bg=None,
    xalign=(1,0.5,0.5),
    padding=10)

title = Image.from_text_justified("British stamp colour scheme, 1900–1950".upper(), chart.width - 100, 120, partial(font, bold=True), fg=fg)
img = Image.from_column([title, chart], padding=20, bg=bg)
img.save("output/ukstamps.png")

