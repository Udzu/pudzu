from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns


not_colder = {"Cyprus", "Portugal", "Malta", "Algeria", "Tunisia", "Vatican City", "San Marino", "Monaco",

              "Israel", "Lebanon", "Palestine", "Jordan", "Saudi Arabia", "Iraq",
              }
not_hotter = {"Iceland", "Faroe Islands"}

def colorfn(c):
    if c == "Ireland":
        return VegaPalette10.GREEN
    # elif c in ["Algeria", "Tunisia", "Morocco"]:
    #     return "white"
    elif c in not_colder:
        return "#AAAAAA" # VegaPalette10.RED
    elif c in not_hotter:
        return "#AAAAAA" # VegaPalette10.BLUE
    elif c in ["Sea", "Borders"]:
        return "white"
    else:
        return VegaPalette10.ORANGE



map = map_chart("maps/Europe2.png", colorfn)
legend = generate_legend(
  [VegaPalette10.GREEN, "#AAAAAA", VegaPalette10.ORANGE],
  ["Ireland (−19.1°C to 33.3°C)",
   "Lower highest temperature //or// higher lowest temperature",
   "Higher highest temperature //and// lower lowest temperature",
   ], 60, partial(arial, 24), header="Temperature extremes".upper(), max_width=400)

chart = map.place(legend, align=(1,0), padding=10)

# title
title = Image.from_column([
Image.from_text("The Temperate Isle".upper(), arial(128, bold=True)),
Image.from_text("nearly every European country has recorded both a higher highest temperature (33.3°C/91.9°F) and a lower lowest temperature (−19.1°C/−2.4°F) than Ireland",
                arial(36, italics=True),
                max_width=1400, align="center", padding=8),
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", arial(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save(f"output/eutempireland.png")

