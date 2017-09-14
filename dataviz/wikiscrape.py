import sys
import pathlib
from math import log
sys.path.append('..')

from wikipage import *
from bamboo import *

# wikifame scraping (messy; also requires manual cleanup and verificaiton at the moment)

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

def score_by_name(names, *args, **kwargs):
    df = pd.DataFrame([{'link': name} for name in make_iterable(names)])
    return score_people(df, *args, **kwargs)
    
def score_births(years):
    dfs = [score_people(extract_births(year)) for year in tqdm.tqdm(years)]
    df = pd.concat(dfs, ignore_index=True).sort_values('score', ascending=False)
    df.to_csv("datasets/wikibirths/en/{}-{}.csv".format(min(years), max(years)), index=False, encoding="utf-8")
    return df
    
def score_births_by_decade(decades):
    for d in tqdm.tqdm(decades):
        score_births(make_iterable(range(d*10,d*10+10)))
        
def rescore_decades(decades, langs=["de", "es", "fr", "ja", "ru", "zh"]):
    for d in tqdm.tqdm(make_iterable(decades)):
        df = pd.read_csv("datasets/wikibirths/en/{d}0-{d}9.csv".format(d=d))
        for lang in tqdm.tqdm(make_iterable(langs)):
            lpath = pathlib.Path("datasets/wikibirths/{l}/{d}0-{d}9.csv".format(l=lang, d=d))
            if not lpath.parent.exists(): lpath.parent.mkdir()
            ldf = score_people(df, lang=lang, translate_from="en").sort_values('score', ascending=False)
            ldf.to_csv(str(lpath), index=False, encoding="utf-8")

def load_decades(decades=range(100,190), lang="en"):
    return pd.concat([pd.read_csv("datasets/wikibirths/{l}/{d}0-{d}9.csv".format(l=lang, d=d)) for d in make_iterable(decades)], ignore_index=True)
    
def normalise_scores(df):
    limits = { k : df[k].max() for k in LIMITS.keys() }
    return df.assign_rows(score=lambda d: harmonic_mean([log(max(d[k], 2)) / log(max_value) for k,max_value in limits.items()]))
    
def combine_scores(decades=range(100,190), langs=["en", "de", "es", "fr", "ja", "ru", "zh"]):
    dfs = [load_decades(decades, lang) for lang in tqdm.tqdm(langs)]
    dfs = [df.groupby('link').first() for df in dfs]
    df = normalise_scores(sum(df.filter_columns(['length', 'pageviews', 'revisions']) for df in dfs))
    return pd.concat([df, dfs[0].filter_columns(['year', 'title'])], axis=1).sort_values("score", ascending=False)

def normalise_and_combine_scores(decades=range(100,190), langs=["en", "de", "es", "fr", "ja", "ru", "zh"]):
    dfs = [normalise_scores(load_decades(decades, lang)) for lang in tqdm.tqdm(langs)]
    dfs = [df.groupby('link').first() for df in dfs]
    df = sum(df.filter_columns(['score']) for df in dfs) / len(langs)
    df = df.sort_values('score', ascending=False)
    return pd.concat([df, dfs[0].filter_columns(['year', 'title'])], axis=1).sort_values("score", ascending=False)
       
def top_per_x(df, x=10):
    return df.reset_index(drop=True).groupby_rows(lambda r: r['year'] // x).first()

# extract us state of birth (for dead people only; could use cleanup)

def is_us_state(wd):
    return any(x.get('id') in ["Q35657", 'Q1352230', 'Q783733'] for x in wd.property_values("P31", convert=False))
    
def state_of_place(wd):
    carry_on = True
    if is_us_state(wd): return wd.name()
    for region in wd.property_values("P131"):
        state = state_of_place(region)
        if state: return state
        elif region.id == "Q30": carry_on = False
    return None if carry_on else wd.name()

def state_of_birth_or_death(name, living=False, birth=True):
    american = False
    wd = WikiPage(name).to_wikidata()
    if living or wd.property_values(wd.DATE_OF_DEATH, convert=False):
        for pob in (wd.places_of_birth if birth else wd.places_of_death):
            for cob in pob.property_values(wd.COUNTRY, lambda qs: wd.END_TIME not in qs, convert=False):
                if cob.get('id') == 'Q30':
                    american = True
                    state = state_of_place(pob)
                    if state: return state
    return "US" if american else None

def write_states(df, file, append=False, **kwargs):
    with open(file, "w" if not append else "a", encoding="utf-8") as f:
        if not append: print("link,score,state", file=f)
        for i in tqdm.tqdm(range(len(df))):
            state = state_of_birth_or_death(df.iloc[i]['link'], **kwargs)
            if state:
                print("{},{},{}".format(df.iloc[i]['title'].replace(',',''),df.iloc[i]['score'],state), file=f)
                f.flush()

