from pudzu.charts import *

df = pd.read_csv("datasets/flagsrwb.csv")
REMOVE = ["hn-ab-07", "co-valca", "hn-sb-07", "sv-us-11", "sv-sm-10", "by-mi-rd", "icon", "br-df-018", "-dimen",
"mn-1310", "it-pgas7", "no-dimen", "/ufe", "/vxt", "/vex"] # false positives
df = df[df.path.apply(lambda p: not any(r in p for r in REMOVE))]

def flag(p):
    img = Image.open(p).to_rgba()
    ratio = img.width / img.height 
    img = img.resize_fixed_aspect(height=60) if ratio < 1.3 else img.resize_fixed_aspect(width=80) if ratio > 2 else img.resize((80, 60))
    tran = any(v == (0,0,0,0) for _,v in img.getcolors(65536))
    return img.pad((1,1,0,1) if tran else 1, "grey") # TODO: better

flags = list(generate_batches(map(flag, df.path), 22))
grid = Image.from_array(flags, padding=5, bg="#EEEEEE")
grid.save("output/flagsrwb.png")

