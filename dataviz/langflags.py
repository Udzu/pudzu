from pudzu.charts import *
from string import ascii_lowercase as lc

df = pd.read_csv("datasets/langflags.csv").set_index("639-1")
W,H = 100, 70
BG = "#E0E0E0"

def box(code):
    flag = get_non(df.flag, code)
    if flag is not None:
        img = Image.from_url_with_cache(flag).convert("RGBA").remove_transparency(BG)
        dims = (W-1, H-1) if img.width / img.height > 1.1 else (H-1, H-1)
        box = img.resize(dims).pad_to(W-1, H-1, bg=BG)
    else:
        box = Rectangle((W-1, H-1), BG if code not in df.index else "#A0A0A0")
    return box.pad((code.endswith("a"),code.startswith("a"),1,1), "#808080")

def label(letter):
    return Image.from_text(letter.upper(), sans(24, bold=True), "black", padding=10)

grid = Image.from_array([[None] + [label(r) for r in lc]] + [[label(r)] + [box(r+c)  for c in lc] for r in lc], bg="white")

title = Image.from_text("A flag for every ISO 639-1 language code".upper(), arial(80, bold=True))
subtitle = Image.from_text("aka an unnecessary exercise in politicisation and ambiguity repurposed as a quiz", arial(48, italics=True))
img = Image.from_column([title, subtitle, grid], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/langflags.png")

print(df[df.flag.isna()])
