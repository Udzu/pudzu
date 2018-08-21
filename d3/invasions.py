import sys
sys.path.append('..')
from charts import *


# legend
HEADER = "Types of military action".upper()
COLORS = '#cb181d', '#fb6a4a', '#fcae91', '#238b45', '#BBBBBB'
LABELS = "Attack against the modern state", "Attack against a historic substate", "Attack against a historic parent state", "Supporting military action", "No military action(?)"
FOOTER = "• **Attacks** refer to any hostile military action in the territory of the state.\n• **Substate attacks** refer to actions against previously sovereign states contained within the borders of the modern state; this covers a significant proportion of colonisation.\n• **Parent attacks** refers to actions within the state when it was under the control of another country; this covers a large amount of intercolonial conflict.\n• **Supporting actions**, like attacks, only include military actions in the territory of the state."
def font_family(bold=False, italics=False): return arial(20 if italics else 24, bold=bold, italics=italics)
legend = generate_legend(COLORS, LABELS, 50, font_family, header=HEADER, footer=FOOTER, max_width=490)

img = Image.open("temp/invasions.png").remove_transparency("white")
chart = img.place(legend, (0,1))
title = Image.from_markup("**THE BRITISH INVASIONS:** countries attacked by Britain", partial(arial, 80))
chart = Image.from_column([title, chart.pad(10, "white")], bg="white")
chart.save("output/invasions.png")
