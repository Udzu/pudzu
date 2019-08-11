import seaborn as sns
from pudzu.charts import *
from pudzu.bamboo import *

df = pd.read_csv("datasets/euvoting.csv").set_index('country')
colors = sns.cubehelix_palette(6, start=1.5, rot=-1, dark=.25)
palette = [RGBA(c) for c in colors]

def colorfn(c):
    if c not in df.index:
        return "white" if c in ['Sea', 'Borders'] else "grey"
    abolished = df['full'][c]
    return palette[(abolished-1890)//20]

def labelfn(c):
    if c not in df.index:
        return None
    abolished = str(df['full'][c])
    partial = "" if non(df['partial'][c]) else "({}-)\n".format(int(df['partial'][c]))
    return Image.from_text(partial+abolished, arial(16, bold=True), align='center')
    
map = map_chart("maps/Europe.png", colorfn, labelfn)
map.save("output/euvoting.png")