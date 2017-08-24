import sys
import seaborn as sns
sys.path.append('..')

from charts import *
from wikipage import *

# data visualisation 

DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
df = pd.read_csv("datasets/wikibirths.csv")
table = pd.DataFrame([[df.iloc[century*10+decade]['name'] if century*10+decade < len(df) else None for decade in range(0,10)] for century in range(0,10)],
                     index=["{}00s".format(c) for c in range(10,20)], columns=["'{}0s".format(d) for d in range(0,10)])
df = df.set_index('name')

def process(img, name):
    bg = "black"
    box = Image.new("RGB", (180,200), bg)
    box = box.place(Image.from_column([
      img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
      Image.from_text(name, arial(12, bold=True), padding=(3, 5, 3, 2), fg="white", bg=bg),
      Image.from_text(get_non(df['description'], name, ""), arial(12), padding=(3,0,3,0), fg="white", bg=bg)
      ], bg=bg))
    return box
    
title = Image.from_column([
Image.from_text("100 famous people of the second millennium", arial(60, bold=True), fg="white", bg="black").pad((10,0)),
Image.from_text("the most famous person born each decade, according to English Wikipedia", arial(36, bold=True), fg="white", bg="black").pad((10,0,10,2))
], bg="black").pad((0,10))

grid = grid_chart(table, lambda n: n and get_non(df['image_url'], n, DEFAULT_IMG), image_process=process, row_label=arial(20, bold=True), col_label=arial(20, bold=True), bg="black", title=title)
grid.show()

# data collection (would need more cleanup/corroboration to be used in larger quantities)

def extract_births(year):
    DATE_PATTERN = re.compile(r"^[_ 0-9]*(January|February|March|April|May|June|July|August|September|October|November|December)[ 0-9]*$")
    wp = WikiPage.from_year(year)
    h2_start = find_tags(wp.bs4, all_(string='Births'), parents_("h2"))
    h2_end = find_tags(h2_start, next_siblings_('h2', limit=1))
    links = find_tags(wp.bs4, select_("#mw-content-text ul li"),
                              all_("a", href=re.compile(r"^/wiki"), title=re_exclude(DATE_PATTERN), limit=1),
                              exclude_(h2_end, is_after),
                              exclude_(h2_start, is_before))
    links = remove_duplicate_tags(links)
    return pd.DataFrame([{ "year": year, "link": WikiPage.title_from_url(a['href'])} for a in links])
    
def score_people(df):
    LIMITS = { 'length': 1500000, 'revisions': 25000, 'pageviews': 1000000 }
    harmonic_mean = optional_import_from('statistics', 'harmonic_mean', lambda data: len(data) / sum(1/x for x in data))
    df = df.assign_rows(progressbar = True,
                        wp=lambda d: WikiPage(d['link']))
    df = df.assign_rows(progressbar = True,
                        title=lambda d: d['wp'].title,
                        length=lambda d: len(d['wp'].response.content),
                        pageviews=lambda d: int(median(([pv['views'] for pv in d['wp'].pageviews("20160101", "20170101")]+[0]*12)[:12])),
                        revisions=lambda d: d['wp'].revision_count(),
                        disambiguation=lambda d: bool(d['wp'].bs4.find(alt="Disambiguation icon")))
    df = df.assign_rows(score=lambda d: harmonic_mean([log(max(d[k], 2)) / log(max_value) for k,max_value in LIMITS.items()]))
    return df.filter_columns(lambda k: k != 'wp')

def score_births(years):
    dfs = [score_people(extract_births(year)) for year in tqdm.tqdm(years)]
    df = pd.concat(dfs, ignore_index=True).sort_values('score', ascending=False)
    df.to_csv("datasets/wikibirths/{}-{}.csv".format(min(years), max(years)), index=False, encoding="utf-8")
    return df
    
def score_births_by_decade(decades):
    for d in tqdm.tqdm(decades):
        score_births(range(d*10,d*10+10))