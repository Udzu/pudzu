import sys
sys.path.append('..')
from charts import *

PALETTE = { "s": VegaPalette10.BLUE, "e": VegaPalette10.GREEN, "i": VegaPalette10.ORANGE, "w": VegaPalette10.RED, "n": VegaPalette10.PURPLE }
FONT = calibri

data = pd.DataFrame([[None,"s"],["n","w"],["i","e"]])

labels = { "e": "England", "s": "Scotland", "i": "Republic of Ireland", "n": "Northern Ireland", "w": "Wales" }
flags = { "e": "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1024px-Flag_of_England.svg.png",
          "n": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Saint_Patrick%27s_Saltire.svg/1024px-Saint_Patrick%27s_Saltire.svg.png", # "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Northern_Ireland.svg/1024px-Flag_of_Northern_Ireland.svg.png",
          "s": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1024px-Flag_of_Scotland.svg.png",
          "w": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Flag_of_Wales_2.svg/1024px-Flag_of_Wales_2.svg.png",
          "i": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Flag_of_Ireland.svg/1024px-Flag_of_Ireland.svg.png" }
footballi = { "n": "https://upload.wikimedia.org/wikipedia/en/0/0b/Northern_ireland_national_football_team_logo.png",
              "s": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Scottish_Football_Association_Logo.svg/877px-Scottish_Football_Association_Logo.svg.png",
              "w": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f5/Football_Association_of_Wales_logo.svg/890px-Football_Association_of_Wales_logo.svg.png",
              "i": "https://upload.wikimedia.org/wikipedia/en/8/87/FAI.png",
              "e": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d5/FA_crest_2009.svg/715px-FA_crest_2009.svg.png" }
rugbyi = { "i": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ca/Irish_Rugby_Football_Union_logo.svg/752px-Irish_Rugby_Football_Union_logo.svg.png",
           "w": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d6/Welsh_Rugby_Union_logo.svg/774px-Welsh_Rugby_Union_logo.svg.png",
           "e": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a1/England_national_rugby_union_team_%28emblem%29.svg/677px-England_national_rugby_union_team_%28emblem%29.svg.png",
           "s": "https://upload.wikimedia.org/wikipedia/en/c/c6/Scotlandlogo.png" }
cricketi = { "s": "https://www.ticketline.co.uk/images/artist/cricket-scotland/cricket-scotland.png",
             "e": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/England_cricket_team_logo.svg/546px-England_cricket_team_logo.svg.png",
             "i": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Cricket_Ireland_logo.svg/768px-Cricket_Ireland_logo.svg.png" }
basketballi = { "e": "https://upload.wikimedia.org/wikipedia/en/9/90/British_Basketball_logo.png", 
                "i": "http://www.basketballireland.ie/wp-content/themes/HT-theme/custom-design/images/logo.png" }
olympicsi = { "e": "https://upload.wikimedia.org/wikipedia/en/thumb/1/10/British_Olympic_Association_logo.svg/1219px-British_Olympic_Association_logo.svg.png",
              "i": "https://upload.wikimedia.org/wikipedia/en/d/d4/Olympic_Council_of_Ireland.png" }

footballg = "eiswn"
rugbyg = [ "e", "in", "s", "w" ]
cricketg = [ "ew", "in", "s" ]
basketballg = [ "esw", "in" ]
olympicsg = [ "eswn", "i" ]

def imagefn(imgs, c):
    img = Rectangle(300, 0)
    if c in imgs:
        i = Image.from_url_with_cache(imgs[c]).to_rgba().resize_fixed_aspect(width=300, height=300)
        if imgs == flags:
            i = i.trim(1).pad(1, "black")
            i = Image.from_column([Image.from_text(labels[c].upper(), FONT(32, bold=True), padding=(0,10)), i])
        img = img.place(i)
    return img 
 
def groupfn(groups, c):
    if c is None: return None
    else: return first_or_default((g[0] for g in groups if c in g))

countries = grid_chart(data, partial(imagefn, flags), padding=15, group_fg_colors=PALETTE, group_rounded=True, group_padding=4, bg=0)
football = grid_chart(data, partial(imagefn, footballi), partial(groupfn, footballg), padding=15, group_fg_colors=PALETTE, group_rounded=True, group_padding=5, bg=0)
rugby = grid_chart(data, partial(imagefn, rugbyi), partial(groupfn, rugbyg), padding=15, group_fg_colors=PALETTE, group_rounded=True, group_padding=5, bg=0)
cricket = grid_chart(data, partial(imagefn, cricketi), partial(groupfn, cricketg), padding=15, group_fg_colors=PALETTE, group_rounded=True, group_padding=5, bg=0)
basketball = grid_chart(data, partial(imagefn, basketballi), partial(groupfn, basketballg), padding=15, group_fg_colors=PALETTE, group_rounded=True, group_padding=5, bg=0)
olympics = grid_chart(data, partial(imagefn, olympicsi), partial(groupfn, olympicsg), padding=15, group_fg_colors=PALETTE, group_rounded=True, group_padding=5, bg=0)

array = [[countries, football, rugby], [cricket, basketball, olympics]]
labels = [["UK & Ireland", "@ Football (Soccer)", "@ Rugby Union"], ["@ Cricket", "@ Basketball", "@ The Olympics"]]
array = tmap_leafs(lambda l,i: Image.from_column([Image.from_text(l.upper(), FONT(52, bold=True), beard_line=True, padding=(0,15)), i]), labels, array)
array = tmap_leafs(lambda i: i.pad(10, 0).pad(1, "black"), array, base_factory=list)
array[0][0] = array[0][0].remove_transparency('#E0E0FF')
#array = tmap_leafs(lambda i, c: i.remove_transparency(c), array, [['#E0E0FF','#F0F0F0','#F0F0F0'],['#F0F0F0','#F0F0F0','#F0F0F0']])
grid = Image.from_array(array)

title = Image.from_text("The wonderfully inconsistent groupings\nof British and Irish sport associations".upper(), FONT(80, bold=True), align="center")
img = Image.from_column([title, grid, Rectangle(0, "white")], bg="white", xalign=0.5, padding=20)
img.place(Image.from_text("/u/Udzu", font("arial", 32), fg="grey", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.convert("RGB").resize_fixed_aspect(scale=0.5).save("output/uksport.png")
