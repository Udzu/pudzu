import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/euvotes.csv").set_index('country')

palette = list(reversed(ImageColor.from_floats(sns.cubehelix_palette(9, start=0.2, rot=-0.75))))

def colorfn(c):
    if c not in df.index:
        return None if c == 'Sea' else "grey"
    votes = df.loc[c].votes
    if votes > 20000000: return palette[0]
    elif votes > 10000000: return palette[1]
    elif votes > 5000000: return palette[2]
    elif votes > 2000000: return palette[3]
    elif votes > 1000000: return palette[4]
    elif votes > 500000: return palette[5]
    elif votes > 200000: return palette[6]
    elif votes > 100000: return palette[7]
    else: return palette[8]
    
def labelfn(c):
    if c not in df.index: return None
    dfc = df.loc[c]
    label = "{name} '{year}\n({votes:.1f}M)".format(name=dfc.leader.split(" ")[-1], year=dfc.year[2:], votes=int(dfc.votes) / 1000000)
    return Image.from_text(label, arial(14, bold=True), align="center", padding=2)

map = map_chart("maps/Europe.png", colorfn, labelfn)
map.save("output/euvotes.png")

