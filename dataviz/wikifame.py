import sys
sys.path.append('..')
from charts import *
from wikipage import *

harmonic_mean = optional_import_from('statistics', 'harmonic_mean', lambda data: len(data) / sum(1/x for x in data))

# collect data

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
        ignoring_exceptions(score_births)(range(d*10,d*10+10))
            