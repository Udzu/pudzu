from pudzu.charts import *

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')['flag']
flags['England'] = "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1280px-Flag_of_England.svg.png"
df = pd.read_csv("datasets/worldcup.csv").split_columns(["wcs", "wws"], "|") \
                                         .assign(wcc=lambda df: df.wcs.str.len()) \
                                         .assign_rows(wwc=lambda d: sum([1,0.2][w=='*'] for w in d.wws)) \
                                         .assign(total=lambda df: df.wcc+df.wwc) \
                                         .sort_values(["total", "wwc"], ascending=False)


ylabel = Image.from_text("combined number of World Wars and World Cups won", arial(18), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)

def rlabel(r):
    name = df.country[r]
    flag = Image.from_url_with_cache(flags[name]).to_rgba()
    return Image.from_column([
            flag.resize((90,60)).pad(1, "grey").pad((0,5), "white"),
            Image.from_text(name.upper(), arial(14, bold=True), "black", align="center", padding=(0,2))
            ], bg="white")
            
def clabel(c,r,v,w,h): 
    count = [df.wcc, df.wwc][c][r]
    values = treversed([df.wcs, df.wws][c][r])
    if len(values) == 0: return None
    def box(name):
        return Rectangle((w,int(round([1,0.2][name=='*']*h/count))), 0).place(Image.from_text(name, arial(24, bold=True)))
    
    return Image.from_column([box(str(v)) for v in values])
    
chart = bar_chart(df[['wcc','wwc']], 100, 800, type=BarChartType.STACKED, colors=[VegaPalette10.ORANGE, VegaPalette10.BLUE],
    spacing=5, ymax=7, rlabels=rlabel, ylabel=ylabel, clabels={ BarChartLabelPosition.INSIDE : clabel },
    grid_interval=1, label_interval=1, label_font=arial(14, bold=False),
    legend_fonts=partial(arial, 18), legend_position=(1,0), legend_args={'header': 'thing wot we won'.upper(), 'labels': ['FIFA World Cup', 'World War'], 'footer': "* France surrendered during WWII and spent most of the War under a collaborationist regime, but also took part in the victory under the Free French Forces. Italy fought on the Axis side until 1943, when it split into a collaborationist puppet state in the North and an Allied state in the south. Argentina and Uruguay both declared war on Germany at the very end of WWII, but didn't see any fighting.", 'max_width': 500})
    
title = Image.from_column([
Image.from_text('“Two World Wars and One World Cup”'.upper(), arial(40, bold=True), padding=(5,10,5,2)),
Image.from_text("countries with over 2 combined global-conflict and international-soccer-competition victories", arial(20, bold=False), padding=(5,2,5,10))
], bg="white")

img = Image.from_column([title, chart.pad(10, "white")], bg="white")
img.save("output/worldcup.png")