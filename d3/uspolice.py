from generate import *
from pudzu.charts import *

# generate d3 html

total_greater = ["Brazil", "India", "Mexico", "South Africa", "Nigeria", "Venezuela", "USA", "Russia", "Colombia", "Philippines", "DR Congo", "China", "Pakistan", "Ethiopia", "El Salvador", "Honduras", "Guatemala", "Uganda", "Bangladesh", "Tanzania", "Iraq", "Turkey", "Ukraine", "Ivory Coast", "Argentina", "Peru", "Kenya", "Thailand", "Egypt", "Afghanistan", "Iran", "Mali", "Madagascar", "Yemen", "Sudan", "Dominican Republic", "South Sudan", "Vietnam", "Jamaica", "Indonesia", "Chad", "Angola", "Myanmar", "North Korea", "Senegal"]
generate_datamap("uspolice_total", dict_from_vals(greater=total_greater),  { "greater": '#BBBBBB' }, default_fill= VegaPalette10.RED)

pc_greater = ["Singapore", "Iceland", "Japan", "Macau", "Saint Helena", "Guernsey", "Jersey", "Isle of Man", "Andorra", "Holy See", "San Marino", "Liechtenstein", "Monaco", "Nauru", "Niue"]
pc_half = ["Italy", "Poland", "Oman", "Austria", "Portugal", "Spain", "China", "Czechia", "Netherlands", "Switzerland", "Bahrain", "Norway", "Indonesia", "Brunei", "Slovenia", "Hong Kong", "Qatar", "French Polynesia", "Burkina Faso"]
pc_fifth = ["Canada", "Ghana", "Tajikistan", "Kosovo", "Macedonia", "Jordan", "Vietnam", "Saudi Arabia", "Finland", "Serbia", "Israel", "Algeria", "France", "Bosnia and Herzegovina", "Romania", "Morocco", "UK", "Germany", "Bulgaria", "Bhutan", "Cyprus", "Sweden", "Slovakia", "Croatia", "Georgia", "New Zealand", "Denmark", "Tonga", "Australia", "Malta", "United Arab Emirates", "Taiwan", "Ireland", "Maldives", "Greece", "Luxembourg", "South Korea", "Palestine"]
generate_datamap("uspolice_pc", dict_from_vals(greater=pc_greater, half=pc_half, fifth=pc_fifth),  { "greater": VegaPalette10.PURPLE, "half": VegaPalette10.RED, "fifth": VegaPalette10.ORANGE })

# generate maps (currently done manually)

# add legends, title, etc

FONT = calibri

HEADER_TOTAL = "Homicides in 2016"
COLORS_TOTAL = VegaPalette10.RED,
LABELS_TOTAL = "fewer than 1093 homicides",
legend_total = generate_legend(COLORS_TOTAL, LABELS_TOTAL, 50, partial(FONT, 24), header=HEADER_TOTAL.upper())
img_total = Image.open("temp/uspolice_total.png").remove_transparency("white").place(legend_total, (0,0.7), padding=50)
title_total = Image.from_text("In 2016, US police killed 1093 people (down 5% on the year before)".upper(), FONT(60, bold=True))
subtitle_total = Image.from_text("this was more than the number of intentional homicides in 183 countries and territories", FONT(48, bold=True))

HEADER_PC = "Homicide rate in 2016"
COLORS_PC = VegaPalette10.PURPLE, VegaPalette10.RED, VegaPalette10.ORANGE
LABELS_PC = "less than 3.4 per million", "less than 6.8 per million", "less than 17 per million"
legend_pc = generate_legend(COLORS_PC, LABELS_PC, 50, partial(FONT, 24), header=HEADER_PC.upper())
img_pc = Image.open("temp/uspolice_pc.png").remove_transparency("white").place(legend_pc, (0,0.7), padding=50)
title_pc = Image.from_text("Measured per capita, this was 3.4 deaths per million population".upper(), FONT(60, bold=True))
subtitle_pc = Image.from_text("or more than the homicide rate in 14 countries and territories, over 50% of it in 33, and over 20% of it in 71", FONT(48, bold=True))

chart = Image.from_column([title_total, subtitle_total, img_total, title_pc, subtitle_pc, img_pc], bg="white", padding=10)
chart.place(Image.from_text("/u/Udzu", font("arial", 24), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
chart.convert("RGB").resize_fixed_aspect(scale=0.5).save("output/uspolice.png")
