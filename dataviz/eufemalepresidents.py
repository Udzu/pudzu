from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

df = pd.read_csv("datasets/eufemaleleaders.csv")
df = df[~df.hosdate.isna()].set_index("country").hosdate
df["Hungary"] = 2022
del df["Switzerland"]
del df["San Marino"]

df["Serbia"] = 2002
df["Israel"] = 2007

monarchies = [
    "UK", "Netherlands", "Sweden", "Norway", "Belgium", "Luxembourg", "Denmark", "Andorra", "Vatican City", "Spain", "Liechtenstein", "Monaco",
"Jordan", "Saudi Arabia", "Morocco",
]

P = "#e31a1c"
AP = "#fb9a99"
N = "#1f78b4"
M = "#a6cee3"
B = M #"#b2df8a"

def colorfn(c):
    if c in monarchies: return M
    elif c in ["Serbia", "Israel"]: return AP
    elif c in df.index: return P
    elif c in ["Switzerland", "Bosnia", "San Marino"] : return B
    elif c in ['Sea', 'Borders']: return "white"
    else: return N

@ignoring_exceptions
def labelfn(c):
    year = str(int(df[c]))
    if c in ["Israel", "Serbia"]: year = f"({year})"
    return year

chart = map_chart("maps/Europe2.png", colorfn, labelfn, label_font=sans(16, bold=True))
legend = generate_legend([P, AP, N, M],
                         ["has had a female president", "has had a female caretaker president", "no female president yet",
                          "no presidents (monarchy or collective head-of-state)"],
                         font_family = partial(sans, 16), max_width=350)
chart = chart.place(legend, align=(1,0), padding=50)

# put it all together
title = Image.from_text("European countries that have had a female President".upper(), sans(48, bold=True), "black", "white", padding=10)
img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eufemalepresidents.png")

