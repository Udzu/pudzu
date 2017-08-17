import sys
sys.path.append('..')
from charts import *
from bamboo import *

# ------------------------
# Nobel prizes by US state
# ------------------------

SIZE = 50

states = pd.read_csv("datasets/usstates.csv")
table = pd.DataFrame([[first_or_default([dict(d) for _,d in states[(states.grid_x == x) & (states.grid_y == y)].iterrows()]) for x in range(states.grid_x.max()+1)] for y in range(states.grid_y.max()+1)])

def table_cell(d):
    if d is None: return Image.new("RGBA", (SIZE,SIZE), "white").pad(1, "white")
    img = Image.new("RGBA", (SIZE,SIZE), "#FFAAAA")
    img = img.place(Image.from_text(d['code'], arial(24,bold=True), fg="black"))
    img = img.pad(1, "white")
    return img

grid = grid_chart(table, table_cell, bg="white")
