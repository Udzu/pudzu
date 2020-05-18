import seaborn as sns
from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT, fg, bg = sans, "white", "black"

atlas = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')
flags = atlas.flag
flags["Serbia and Montenegro"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Flag_of_Yugoslavia_%281992%E2%80%932003%29%3B_Flag_of_Serbia_and_Montenegro_%282003%E2%80%932006%29.svg/1024px-Flag_of_Yugoslavia_%281992%E2%80%932003%29%3B_Flag_of_Serbia_and_Montenegro_%282003%E2%80%932006%29.svg.png"
flags["USSR"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/1024px-Flag_of_the_Soviet_Union.svg.png"
flags["Czechoslovakia"] = flags["Czech Republic"]
flags["Yugoslavia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Flag_of_Yugoslavia_%281946-1992%29.svg/1024px-Flag_of_Yugoslavia_%281946-1992%29.svg.png"
flags["Romania"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Flag_of_Romania_%281952-1965%29.svg/1024px-Flag_of_Romania_%281952-1965%29.svg.png"
flags["Bulgaria"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Flag_of_Bulgaria_%281946-1948%29.svg/1024px-Flag_of_Bulgaria_%281946-1948%29.svg.png"
flags["Germany"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Germany_%281935%E2%80%931945%29.svg/1024px-Flag_of_Germany_%281935%E2%80%931945%29.svg.png"
flags["Italy"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Flag_of_Italy_%281861-1946%29_crowned.svg/1024px-Flag_of_Italy_%281861-1946%29_crowned.svg.png"
flags["Montenegro"] = "https://i.redd.it/w4jj4tbscae41.jpg"
flags["Spain"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Flag_of_Spain_%281945%E2%80%931977%29.svg/1024px-Flag_of_Spain_%281945%E2%80%931977%29.svg.png"
flags["Albania"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Flag_of_Albania_%281946%E2%80%931992%29.svg/1024px-Flag_of_Albania_%281946%E2%80%931992%29.svg.png"
df = pd.read_csv("datasets/eu_diedinoffice.csv")

def entitle(img):
    title = Image.from_text("european leaders who died in office".upper(), FONT(108, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("most recent example per country; excludes ceremonial heads of state", FONT(60), fg=fg, bg=bg).pad((0,0,0,10), bg)
    FOOTERS = ["""1. Nicolae Ceaușescu was executed just 3 days after being overthrown in 1989.
2. Päts was imprisoned by the Soviets in 1940 but considered head of state by the government-in-exile until his death.
3. Žemaitis led the anti-Soviet resistance and is considered the head of state by modern Lithuania.
4. Kolarov died just a few months after general secretary Georgi Dimitrov.
5. Goebbels committed suicide just one day after Hitler.
6. Mussolini was executed in 1945 while still leading the Italian Social Republic puppet state in Northern Italy."""]
    footers = [Image.from_text(FOOTER, FONT(24), "white", padding=10, beard_line=True, line_spacing=1) for FOOTER in FOOTERS]
    footer = Image.from_row(footers, padding=(20,5), yalign=0)
    img = Image.from_column([title, subtitle, img, footer], bg=bg, padding=5).pad(15,bg=bg)
    img = img.place(Image.from_text("/u/Udzu", FONT(16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10)
    return img

grids = []
for rows in generate_batches(df.iterrows(), ceil(len(df)/3)):
    
    def match(country, type):
        match = df[(df.country == country) & (df.type == type)]
        return dict(match.iloc[0]) if len(match) else np.nan

    table = pd.DataFrame([[dict(r) for _, r in rows]], columns=[r.country for _,r in rows])
    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg" # "https://upload.wikimedia.org/wikipedia/commons/6/68/Solid_black.png" # 

    def cell(d):
        if non(d) or not get_non(d, 'name'): return None
        img = Image.from_url_with_cache(get_non(d, 'image', DEFAULT_IMG))
        return Image.from_column([
          Image.from_text_bounded(get_non(d, 'name', ''), (200, 200), 16, partial(FONT, bold=True),fg=fg, bg=bg, beard_line=True),
          img.cropped_resize((200,200), (0.5,get_non(d, 'align', 0.2)) if img.height >= img.width else (get_non(d, 'align', 0.5), 0.5)),
          Image.from_text(get_non(d, 'role', ''), FONT(16, italics=True),fg=fg, bg=bg, beard_line=True),
          Image.from_text("{}, {}".format(get_non(d, 'cause', '?'), d['year']), FONT(16, bold=False), max_width=200, fg=fg, bg=bg, beard_line=True),
          ], bg=bg, padding=2).pad(5, bg)
        
    def flag(column):
        flag = Image.from_url_with_cache(atlas.flag[table.columns[column]]).to_rgba()
        flag = flag.resize_fixed_aspect(height=130) if flag.width / flag.height < 1.3 else flag.resize((200,130))
        flag = flag.trim(1).pad(1, "grey").pad((0,10,0,0), bg)
        label = Image.from_text_bounded(table.columns[column].upper().replace("BOSNIA","BiH"), (200, 200), 20, partial(FONT, bold=True),fg=fg,bg=bg,beard_line=True)
        return Image.from_column([flag.pad((0,0,0,10),bg=bg), label])

    def row_label(row):
        return Image.from_text("HEAD OF STATE" if row==0 else "HEAD OF GOV'T", FONT(20, bold=True), fg=fg, bg=bg, padding=(0,10)).pad_to(width=300).transpose(Image.ROTATE_90)

    grid = grid_chart(table, cell, col_label=flag, bg=bg, yalign=0)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0)
chart = entitle(chart)
chart.convert("RGB").save("output/eudiedinoffice.jpg")

