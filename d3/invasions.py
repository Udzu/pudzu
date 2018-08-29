import sys
sys.path.append('..')
from charts import *

# legend
HEADER = "Types of military actions".upper()
COLORS = '#cb181d', '#fb6a4a', '#fcae91', '#238b45', '#BBBBBB'
LABELS = ["**Attack against the modern state**: //any hostile military action in the territory of the state.//",
"**Attack against a historic substate**: //actions against previously sovereign states contained within the borders of the modern state; this covers a significant proportion of colonisation.//",
"**Attack against a historic parent state**: //actions within the state when it was under the control of another country; this covers a large amount of intercolonial conflict.//",
"**Supporting military action**: //like attacks, these only include military actions within the territory of the state.//",
"**No military action**"]
FOOTER = """**DETAILS**
• **Attacks** refer to any hostile military action in the territory of the state.
• **Substate attacks** refer to actions against previously sovereign states contained within the borders of the modern state; this covers a significant proportion of colonisation.
• **Parent attacks** refers to actions within the state when it was under the control of another country; this covers a large amount of intercolonial conflict.
• **Supporting actions**, like attacks, only include military actions in the territory of the state."""
font_family = partial(arial, 24)
legend = generate_legend(COLORS, LABELS, (50,...), font_family, header=HEADER, border=True, max_width=2000)
# text = Image.from_markup(FOOTER, font_family, max_width=900)
# legend = Image.from_row([legend, text], padding=15, bg="white", yalign=0).pad(1, "black")

img = Image.open("temp/invasions.png").remove_transparency("white").trim((0,300,0,0))
chart = Image.from_column([img, legend], bg="white")
title = Image.from_markup("**THE BRITISH INVASIONS:** countries attacked by Britain", partial(arial, 80))
chart = Image.from_column([title, chart], bg="white")
chart.save("output/invasions.png")
