import seaborn as sns
from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT, fg, bg = sans, "white", "black"

atlas = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')
df = pd.read_csv("datasets/eu_foreignleaders.csv")

def entitle(img):
    title = Image.from_text("foreign-born European leaders".upper(), FONT(108, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("the most recent foreign-born head of state and government from each country", FONT(60), fg=fg, bg=bg).pad((0,0,0,10), bg)
    FOOTERS = ["""MORE RECENT (BUT LESS GOOD) ALTERNATIVES
1. President Adolf Schärf (1957-65) was born in Nikolsburg which later became part of Czechoslovakia.
    Chancellor Karl Renner (1918-20/1945) was born in Dolní Dunajovice which later became part of Czechoslovakia.
2. President Martti Ahtisaari (1994-00) was born in Viipuri which later became part of Russia.
    Prussian-born Frederick Charles was elected king in 1918 but never crowned.
3. President Konstantinos Karamanlis (1980-85/90-95) was born in Proti, Ottoman Empire before it became part of Greece.
4. Council Chairman János Kádár (1961-65) was born in Fiume which later became part of Croatia.""",
"""
5. President Mary McAleese (1997-11) was born in Belfast, Northern Ireland, but at the time Ireland claimed sovereignty over the entire island.
6. Some sources list Prime Minsiter Klaus Tschütscher (2009-13) as being born in Grabs, Switzerland, but others claim Vaduz.
7. Monaco-born Mindaugas II was elected King of Lithuania in 1918, but never assumed the crown.
8. President Emil Constantinescu (1996-00) was born Tighina which later became part of Moldova.
9. President Leonid Kravchuk (1991-94) was born in Velykyi Zhytyn, Poland before it became part of Ukraine.
10. During the Nazi Occupation, Netherlands and Norway had a foreign-born Reichskommissar, but also a government in exile.""",
"""FOOTNOTES
11. Hitler's birthplace was part of Germany between 1938 and 1945.
12. Buzek's birthplace was part of Poland between 1938 and 1939.

BARELY FOREIGN (BUT I COULDN'T FIND ANYONE BETTER)
13. De Gasperi's birthplace became part of Italy during his lifetime.
14. Aura's birthplace was part of Finland before it became Russian.
15. Văcăroiu's birthplace was part of Romania before it became Ukrainian.
16. Atatürk's birthplace was part of Turkey before it became Greek.
""",]


    footers = [Image.from_text(FOOTER, FONT(24), "white", padding=10, beard_line=True, line_spacing=1) for FOOTER in FOOTERS]
    footer = Image.from_row(footers, padding=(20,5), yalign=0)
    img = Image.from_column([title, subtitle, img, Rectangle((img.width, 2), "grey"), footer], bg=bg, padding=5).pad(15,bg=bg)
    img = img.place(Image.from_text("/u/Udzu", FONT(16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10)
    return img

grids = []
all_countries = sorted(set(df.country))
for countries in generate_batches(all_countries, ceil(len(all_countries)/3)):
    
    def match(country, type):
        match = df[(df.country == country) & (df.type == type)]
        return dict(match.iloc[0]) if len(match) else np.nan

    ss = [match(country, "s") for country in countries]
    gs = [match(country, "g") for country in countries]
    table = pd.DataFrame([ss,gs], index=["s","g"], columns=countries)
    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg" # "https://upload.wikimedia.org/wikipedia/commons/6/68/Solid_black.png" # 

    def cell(d):
        if non(d) or not get_non(d, 'name'): return None
        logger.info(f"{d['country']} / {d['type']}")
        img = Image.from_url_with_cache(get_non(d, 'image', DEFAULT_IMG))
        return Image.from_column([
          Image.from_text(get_non(d, 'name', ''), FONT(16, bold=True),fg=fg, bg=bg, beard_line=True),
          Image.from_text(get_non(d, 'role', ''), FONT(16, italics=True),fg=fg, bg=bg, beard_line=True),
          img.cropped_resize((200,200), (0.5,get_non(d, 'align', 0.2)) if img.height >= img.width else (get_non(d, 'align', 0.5), 0.5)),
          Image.from_text(f"{d['city']}, {d['place']}", FONT(16, bold=False), max_width=200, fg=fg, bg=bg, beard_line=True),
          ], bg=bg, padding=2).pad(5, bg)
        
    def flag(column):
        flag = Image.from_url_with_cache(atlas.flag[table.columns[column]]).to_rgba()
        flag = flag.resize_fixed_aspect(height=140) if flag.width / flag.height < 1.3 else flag.resize((200,140))
        flag = flag.trim(1).pad(1, "grey").pad((0,10,0,0), bg)
        label = Image.from_text(table.columns[column].upper().replace("BOSNIA","BiH"), FONT(20, bold=True),fg=fg,bg=bg,beard_line=True)
        return Image.from_column([flag.pad((0,0,0,10),bg=bg), label])

    def row_label(row):
        return Image.from_text("HEAD OF STATE" if row==0 else "HEAD OF GOV'T", FONT(20, bold=True), fg=fg, bg=bg, padding=(0,10)).pad_to(width=300).transpose(Image.ROTATE_90)

    grid = grid_chart(table, cell, col_label=flag, row_label=row_label, bg=bg, yalign=0)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0)
chart = entitle(chart)
chart.convert("RGB").save("output/euforeignleaders.jpg")

