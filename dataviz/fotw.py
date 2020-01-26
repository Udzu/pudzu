from pudzu.pillar import *
from pathlib import Path
from tqdm import tqdm

BG = "#EEEEEE"
FOTW_DIR = Path("images")

class HeraldicPalette(metaclass=NamedPaletteMeta):
    Y = "#fcdd09" # yellow
    W = "#ffffff" # white
    B = "#0f47af" # black
    R = "#da121a" # red
    P = "#9116a1" # purple
    K = "#000000" # black
    G = "#009200" # green
    T = "#804000" # brown
    O = "#ff8000" # orange
    C = "#75aadb" # sky blue

def runs(row): return (np.ediff1d(row) != 0).sum() + 1

def omit_types(filter, types="()^!~@}'$_"):
    @wraps(filter)
    def wrapped(p, *args, **kwargs):
        if any(c in p.stem for c in types): return None
        return filter(p, *args, **kwargs)
    return wrapped
    
def generate_cribs(filter, prefix=None, max_cols=10, max_rows=10, base_path=FOTW_DIR):
    i, counts, images = 0, {}, {}
    
    def save_and_increment(cat):
        if images.get(cat, []):
            icons = []
            for p in images[cat]:
                icon = Image.open(p).to_rgba().pad_to_aspect(80,50,bg=BG).resize_fixed_aspect(height=50)
                label = Image.from_text(p.stem, sans(10))
                both = Image.from_column([icon, label], padding=(0,3))
                icons.append(both)
            img = Image.from_array(list(generate_batches(icons, max_cols)), padding=5, bg=BG)
            counts[cat] = counts.get(cat, 0) + 1
            filename = f"{prefix or filter.__name__}_{cat}_{counts[cat]}.png"
            print(f"Saving flags to {filename}")
            img.save(filename)
            images[cat] = []
    
    for p in base_path.rglob("*gif"):
        try:
            cat = filter(p)
            if cat:
                i += 1
                print(str(cat)[0], end="")
                if i % max_cols == 0: print(f" {p.stem}")
                images.setdefault(cat, []).append(p)
                if len(images[cat]) >= max_cols * max_rows: save_and_increment(cat)
                    
        except:
            continue
    print()
    for cat in images: save_and_increment(cat)

@omit_types
def transparent(p):
    """Any flags with transparency"""
    img = Image.open(p)
    return any(c[-1] == 0 and v > max(img.width, img.height) for v,c in img.to_rgba().getcolors())

def bands(n):
    """Simple heuristic for n-banded flags"""
    @omit_types
    def bands(p):
        img = Image.open(p)
        if img.width < img.height: return None
        a = np.array(img)
        if all(a[0] == a[-1]) and runs(a[0]) == n and runs(a[:,0]) == 1:
            cat = "Vertical"
        elif all(a[:,0] == a[:,-1]) and runs(a[:,0]) == n and runs(a[0]) == 1:
            cat = "Horizontal"
        elif (all(a[0] == a[-1]) or all(a[:,0] == a[:,-1])) and runs(a[0]) == n and runs(a[:,0]) == n:
            cat = "Cross"
        else:
            return
        ap = np.array(img.to_palette(HeraldicPalette))
        if cat == "Vertical":
            cat += "_" + "".join(HeraldicPalette.names[i] for i,_ in itertools.groupby(ap[0]))
        elif cat == "Horizontal":
            cat += "_" + "".join(HeraldicPalette.names[i] for i,_ in itertools.groupby(ap[:,0]))
        return cat
    return bands

# TODO: color (e.g. pink), 
