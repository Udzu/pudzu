from pudzu.charts import *
from glob import glob

df = pd.read_csv("datasets/flagsbiband.csv").set_index("colours")

FONT, SIZE = sans, 24
fg, bg = "black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
COLORS = { "W": "white", "Y": "yellow", "R": "red", "G": "green", "B": "blue", "K": "black", }
W, H = 320, 200
MISSING = Rectangle((W,H),"#BBBBBB")

def label(c, size):
    w, h = size
    label = Image.from_text_bounded(" ", (W,H), SIZE, partial(FONT, bold=True), beard_line=True)
    description = Image.from_text_bounded(" ", (W,H), SIZE, partial(FONT, italics=True), beard_line=True)
    if c == "Y":
        flag = Triangle(max(w,h), "orange", "yellow", p=1.0).crop_to_aspect(w,h).trim(1).pad(1, "grey")
    elif c == "B":
        flag = Triangle(max(w,h), RGBA.blend("lightblue", bg, 0.1), RGBA.blend("blue", bg, 0.1), p=1.0).crop_to_aspect(w,h).trim(1).pad(1, "grey")
    else:
        flag = Rectangle((w-2, h-2), RGBA(COLORS.get(c)).blend(bg, 0.05 if c == "K" else 0.1)).pad(1, "grey")
    return Image.from_column([label, description, flag], padding=2, bg=bg)
    
def process(d):
    if non(d.get('name')): return None if "code" in d and d["code"][0] == d["code"][-1] else MISSING
    label = Image.from_text_bounded(d['name'].replace("*","").upper(), (W,H), SIZE, partial(FONT, bold=True), beard_line=True)
    description = Image.from_text_bounded(get_non(d, 'description', " "), (W,H), SIZE, partial(FONT, italics=True), beard_line=True)
    flag = Image.from_url_with_cache(get_non(d, 'flag', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=H-2) if flag.width / flag.height < 1.3 else flag.resize((W-2,H-2))
    flag = flag.pad(1, "grey")
    flaglabel = Image.from_column([label, description, flag], padding=2, bg=bg)
    if "*" in d['name']: flaglabel = flaglabel.blend(Rectangle(flaglabel.size, bg), 0.3)
    return flaglabel

def bi_grid(orientation):
    ms = df[df.orientation == orientation]
    colors = "".join(COLORS)
    array = [[dict(ms.loc[code][["name", "description", "flag"]]) if (code) in ms.index else {"code":code} for b in colors for code in [(b+t) if orientation in "HS" else (t+b)]] for t in colors]
    data = pd.DataFrame(array, index=list(colors), columns=list(colors))
    grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=1,
                      row_label=lambda row: label(data.index[row], (100, H)),
                      col_label=lambda col: label(data.columns[col], (W,100)), 
#                      corner_label=label(middle, (100,100))
                      )
    return grid

def mono_grid():
    ms = df[df.orientation == "S"]
    colors = "".join(COLORS)
    array = [[dict(ms.loc[b][["name", "description", "flag"]]) for b in colors]]
    data = pd.DataFrame(array, columns=list(colors))
    grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=1,
                      col_label=lambda col: label(data.columns[col], (W,100)), 
#                      corner_label=label(middle, (100,100))
                      )
    return grid

mono = mono_grid()
bi1 = Image.from_row([bi_grid(c) for c in "HV"], padding=100, bg=bg)
bi2 = Image.from_row([bi_grid(c) for c in "DS"], padding=100, bg=bg)
grid = Image.from_column([mono, bi1, bi2], padding=50, bg=bg)

title = Image.from_column([
    Image.from_text_bounded("From Aargau to Zürich".upper(), grid.size, 360, partial(FONT, bold=True), fg=fg, bg=bg, padding=(100,20)),
    Image.from_text_bounded("a selection of solid and bicolor flags".upper(), grid.size, 240, partial(FONT, bold=True), fg=fg, bg=bg, padding=(100,20)),
    ], padding=0)
img = Image.from_column([title, grid], bg=bg, padding=(20,0)).pad(10, bg)
img.place(Image.from_text("/u/Udzu", FONT(48), fg=fg, bg=bg, padding=10).pad((2,2,0,0), fg), align=1, padding=10, copy=False)
img.save("output/flagsbiband.png")
img.resize_fixed_aspect(scale=0.5).save("output/flagsbiband2.png")

# some ultra naive helper functions for finding biband flags from fotw
# TODO: convert to RGB and posterize

@artial(ignoring_exceptions, False)
def is_biband(img, horizontal=True):
    a = np.ascontiguousarray(img if not horizontal else np.array(img).transpose())
    void_dt = np.dtype((np.void, a.dtype.itemsize * np.prod(a.shape[1:])))
    _,ids, count = np.unique(a.view(void_dt).ravel(), return_index=1,return_counts=1)
    if count.max() >= a.shape[0] * 0.38:
        mode = a[ids[count.argmax()]]
        groups = [len(list(v)) for k,v in itertools.groupby(mode)]
        filtered = [n for n in groups if n >= 10]
        if len(groups) <= 5 and len(filtered) == 2:
            return True
    return False

@artial(ignoring_exceptions, False)
def is_diagonal(img, flip=False):
    a = np.array(img)
    if flip: a = a.transpose()
    def runs(i):
        b = a[i]
        b = np.concatenate([b[:b.size//3],b[-b.size//3:]])
        return len([n for k,v in itertools.groupby(b) for n in [len(list(v))] if n >1])
    if runs(0) == 1 and runs(a.shape[0]//2) == 2 and runs(a.shape[0]-1) == 1: return True
    elif not flip: return is_diagonal(img, True)
    else: return False

def find_bibands(files="a/*gif", horizontal=True, filter_fn=is_biband):
    images = []
    for p in glob(files):
        try:
            i = Image.open(p)
        except:
            continue
        if i.width < i.height: continue
        if filter_fn(i, horizontal): 
            print(f"{len(images)}. {p}")
            icon = i.to_rgba().pad_to_aspect(80,50,bg=bg).resize_fixed_aspect(height=50)
            label = Image.from_text(p, sans(10))
            images.append(Image.from_column([icon, label], padding=(0,3)))
    return Image.from_array(list(generate_batches(images, 18)), padding=5, bg=bg) if images else Rectangle(10, bg)
