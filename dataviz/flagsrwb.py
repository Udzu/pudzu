from pudzu.charts import *
from pathlib import Path


DIR = Path(r"C:\Users\Uri\Documents\My Books\Hobbies\Flags\images")
IGNORE_TYPES = [ "icon", "dimen", "ufe", "vxt", "vex", "title", "fic", "film"]
FALSE_POSITIVES = [
"co-valca", "br-df-018", "us-il-ch215p",
"cu-rou59", "id-ktr5", "tw-olimp",
"ar-mne18", "ca-ab-bf", 
"fr-90-cg",  "pa-coc", "ro-54nvp", "sk-kn-vk",
"us-azstj", "us-orpo17",

# green, etc
"br-pr-238", "br-rs-237", "br-pr-238", "es-m-adf", "es-t-clr", 
"hu-so-bl", "jp-23-th-ak", "jp-46-mm", "pl-ma-ka", "sv-us-11",
"sv-sm-10", "sv-sm-20", "sv-mo-06", "ua-kg-ho", "by-mi-rd", 
"fm-pp-ko", "it-pgas7", "hn-sb-07", "sv-sa-13", "jp-08-ng",
"jp-32-go",
"be-wlgwz", "de-sf-li", "de-sf-lo", "pl-op-by", "mn-1310", 
"gt-to-04",

# both blues
 "us-tx-cc", "jp-11-fk",
 
# crests, etc
"tr-07-yu", "tr-15", "tr-34", "sv-li-15t", "tr-26",
"sv-ca1", "au-nsw", "au-ql", "zw-", "za-bsac", "za-ca", 
"xa-rosebu", "us-tx-lew", "us-tn-2m", "us-nv-lc2",
"us-bunkb", "ua-98676", "sv-ca-06", "sv-li-19",
"sv-us-16", "sv-us-sd", "sv-ss", "sv-sm", "us-frali",
"sr-54-gv", "so-b", "rel-kogf", "ps-bala", "pl-sw-na",
"ph-ifu", "no-kap", "no-pen", "nl-chpn", "nl-kon18", 
"ni-an-08", "nl-batr", "mn-su", "is-c1919", "int-sam",
"in-wankf", "in-travt", "in-cochr", "il-bshv", "ie-cdb",
"hu-be-fz", "ht-state", "hr-os-sv", "gb-rfase", "fr-33-sl",
"fm-pp-mh", "fi-nba", "br-sp-pb", "br-rs-257", "br-pb-006", "br-ce-077",
"be-whtb2", "su-lv", "su-kg", "su-uz", "co-cautr", "rel-kofg",
"ec-m2"

# thin
"nl-pltd1", "nl-pltd4",

]
FALSE_NEGATIVES = [
'us', 'np', 'np_1939', 'np_1958', 'ws', 'kh',
'us-ms', 'us-ar', 'us-oh-cl', 'us-oh-ci', 'us-in-in', 'us-ia', 'us-mo', 'us-oh', 'us-ga-tr',
'be-whtfr', 'cz-op-ht', 'cz-pv-be', 'de-di-02-bu', 'de-gw-he-ab2', 'de-nf-07-sd', 'de-od-03-wb',
'de-od-04-sf', 'de-pl-03-bl', 'de-rd-02-bu', 'de-rd-11-f09', 'de-rz-07-ri',
'us-wyeva', 'us-wy-su', 'us-va-wb', 'us-txnvs', 'us-ston', 'us-scpen', 'us-vaann', 'us-oharh',
'us-oh-uo', 'us-oh-md', 'us-nchdb', 'us-mtbil', 'us-mojef', 'us-lacsa', 'us-ga20',
'tw-tpe', 'tr-58-si', 'uno-itu1', "uy-pa", "xa-brbrr", "xa-hrtlk",
'br-pa-001', 'br-pb-003', 'br-pb-123', 'br-pr-060', 'fr-59-ba', 'fr-50-av', 'np-mustg', 'pl-wp-pb',
'py-as', 'pt-smf2', 'nl-fl-uk', 'se-17', 'ar-x-vd', 'be-wlglc', 'be-wlxpa', 'br-go-124',
"be-wlx", "us-iacdr"
]

df = pd.read_csv("datasets/flagsrwb.csv")
df = df.append(pd.DataFrame([{"path": DIR/n[0]/f"{n}.gif", "category": "extra"} for n in FALSE_NEGATIVES]), ignore_index=True)
df["stem"] = df.path.apply(lambda p: Path(p).stem)
df = df.sort_values("stem")
df = df[df.stem.apply(lambda p: not any(r in p for r in IGNORE_TYPES) and not any(p.startswith(r) for r in FALSE_POSITIVES))]
assert df.stem.is_unique

W, H = 80, 60
P, B = 4, 1
C, F = 30, 10
BG = "#EEEEEE"

def flag(p):
    img = Image.open(p).to_rgba()
    ratio = img.width / img.height
    img = img.resize_fixed_aspect(height=H) if ratio < W/H else img.resize_fixed_aspect(width=W) # if ratio > 1.8 else img.resize((W, H))
    def t(a): return B * (not any(alpha==0 for _,_,_,alpha in a))
    a = np.array(img)
    padding = (t(a[:,0]), t(a[0]), t(a[:,-1]), t(a[-1]))
    img = img.pad(padding, "grey")
    img = Image.from_column([img, Image.from_text(Path(p).stem, sans(F))])
    return img

flags = list(generate_batches(map(flag, df.path), C))
grid = Image.from_array(flags, padding=P, bg=BG)

TITLE = "Three cheers for the red, white, and blue!"
SUBTITLE = "a selection of 1200 red, white and blue flags taken from the Flags of the World website"
title = Image.from_text_justified(TITLE.upper(), grid.width-100, 150, partial(sans, bold=True))
subtitle = Image.from_text_justified(SUBTITLE, title.width, 100, partial(sans, italics=True))
titles = Image.from_column([title, subtitle], padding=5).pad(20, bg=BG)
img = Image.from_column([titles, grid], bg=BG)

img.save("output/flagsrwb.png")
img.convert("RGB").save("output/flagsrwb.jpg")