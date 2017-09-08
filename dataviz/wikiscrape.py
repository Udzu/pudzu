import sys
import pathlib
from math import log
sys.path.append('..')

from wikipage import *
from bamboo import *

# wikifame scraping (requires manual cleanup and veririficaiton at the moment; could add simple wikidata corroboration)

def extract_births(year):
    DATE_PATTERN = re.compile(r"^[_ 0-9]*(January|February|March|April|May|June|July|August|September|October|November|December)[ 0-9]*$")
    wp = WikiPage.from_year(year)
    h2_start = find_tags(wp.bs4, all_(string='Births'), parents_("h2"))
    if len(h2_start) == 0: return pd.DataFrame(columns=("link", "year"))
    h2_end = find_tags(h2_start, next_siblings_('h2', limit=1))
    links = find_tags(wp.bs4, select_("#mw-content-text ul li"),
                              all_("a", href=re.compile(r"^/wiki"), title=re_exclude(DATE_PATTERN), limit=1),
                              exclude_(h2_end, is_after),
                              exclude_(h2_start, is_before))
    links = remove_duplicate_tags(links)
    return pd.DataFrame([{ "year": year, "link": WikiPage.title_from_url(a['href'])} for a in links])
    
harmonic_mean = optional_import_from('statistics', 'harmonic_mean', lambda data: len(data) / sum(1/x for x in data))
LIMITS = { 'length': 1500000, 'revisions': 25000, 'pageviews': 1000000 }

def score_people(df, lang="en", translate_from=None):
    df = df.assign_rows(progressbar = True,
                        wp = (lambda d: WikiPage(d['link'], lang=lang)) if translate_from is None else ignoring_exceptions(lambda d: WikiPage(d['link'], lang=translate_from).to_wikidata().to_wikipedia(lang=lang)))
    df = df.assign_rows(progressbar = True,
                        title=lambda d: '?' if d['wp'] is None else d['wp'].title,
                        length=lambda d: 1 if d['wp'] is None else len(d['wp'].response.content),
                        pageviews=lambda d: 1 if d['wp'] is None else int(median(([pv['views'] for pv in d['wp'].pageviews("20160101", "20170101")]+[0]*12)[:12])),
                        revisions=lambda d: 1 if d['wp'] is None else d['wp'].revision_count(),
                        disambiguation=lambda d: d['wp'] and bool(d['wp'].bs4.find(alt="Disambiguation icon")))
    df = df.assign_rows(score=lambda d: harmonic_mean([log(max(d[k], 2)) / log(max_value) for k,max_value in LIMITS.items()]))
    return df.filter_columns(lambda k: k != 'wp')

def score_births(years):
    dfs = [score_people(extract_births(year)) for year in tqdm.tqdm(years)]
    df = pd.concat(dfs, ignore_index=True).sort_values('score', ascending=False)
    df.to_csv("datasets/wikibirths/{}-{}.csv".format(min(years), max(years)), index=False, encoding="utf-8")
    return df
    
def score_births_by_decade(decades):
    for d in tqdm.tqdm(decades):
        score_births(make_iterable(range(d*10,d*10+10)))
        
def rescore_decades(decades, langs=["de", "es", "fr", "ja", "ru", "zh"]):
    for d in tqdm.tqdm(make_iterable(decades)):
        df = pd.read_csv("datasets/wikibirths/{d}0-{d}9.csv".format(d=d))
        for lang in tqdm.tqdm(make_iterable(langs)):
            lpath = pathlib.Path("datasets/wikibirths/{l}/{d}0-{d}9.csv".format(l=lang, d=d))
            if not lpath.parent.exists(): lpath.parent.mkdir()
            ldf = score_people(df, lang=lang, translate_from="en").sort_values('score', ascending=False)
            ldf.to_csv(str(lpath), index=False, encoding="utf-8")

def combine_decades(decades, langs=["de", "en", "es", "fr", "ja", "ru", "zh"], output_dir="combined"):
    output_dir = "datasets/wikibirths/{}".format(output_dir)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    for d in tqdm.tqdm(make_iterable(decades)):
        dfs = [pd.read_csv("datasets/wikibirths{}/{d}0-{d}9.csv".format("" if lang == "en" else "/"+lang, d=d)) for lang in langs]
        dfs = [df.groupby('link').first().filter_columns(['length', 'pageviews', 'revisions']) for df in dfs]
        df = sum(dfs).assign_rows(score=lambda d: harmonic_mean([log(max(d[k], 2)) / log(max_value) for k,max_value in LIMITS.items()]))
        df = df.sort_values('score', ascending=False)
        df.to_csv("{}/{d}0-{d}9.csv".format(output_dir, d=d), encoding="utf-8")
    
def top_per_century(centuries=range(10,19), langs=["de", "en", "es", "fr", "ja", "ru", "zh"]):
    return { c * 100 : { lang: read_csvs("datasets/wikibirths{}/{}*csv".format("" if lang == "en" else "/"+lang,c)).sort_values("score", ascending=False)['link'].iloc[0] for lang in langs} for c in make_iterable(centuries) }
            
