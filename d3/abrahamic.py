from generate import *
from pudzu.charts import *

# generate d3 html

second = ["Estonia", "Czech Republic", "Israel", "South Korea", "India", "Thailand", "Myanmar", "Hong Kong", "Singapore", "Mauritius", "Togo", "Madagascar", "Cambodia"]
neither = ["Nepal", "Bhutan", "Sri Lanka", "China", "Mongolia", "Laos", "Vietnam", "Taiwan", "Japan", "North Korea", "Macau"]

generate_datamap("abrahamic", dict_from_vals(second=second, neither=neither),  { "second": VegaPalette10.ORANGE, "neither": VegaPalette10.RED }, default_fill= "#AAAAAA")

# generate output

chart = Image.open("temp/abrahamic.png")
legend = generate_legend(["#AAAAAA", VegaPalette10.ORANGE, VegaPalette10.RED], ["the most common religion", "the second most common religion", "neither"], font_family = partial(arial, 16), header="Christianity or Islam is...")
chart.place(legend, align=(0,0.9), copy=False, padding=50)
title = Image.from_text_justified("Christianity and Islam: global religions\ncountries where the main religion is neither Christianity nor Islam".upper(), chart.width - 200, 200, partial(arial, bold=True), line_spacing=0)
img = Image.from_column([title, chart], bg="white", padding=(0,20))
img.save("output/abrahamic.png")
