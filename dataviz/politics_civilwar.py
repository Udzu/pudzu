import sys
sys.path.append('..')
from charts import *

confederate = ["South Carolina", "Mississippi", "Florida", "Alabama", "Georgia", "Louisiana", "Texas"]
union = ["California", "Connecticut", "Illinois", "Indiana", "Iowa", "Kansas", "Maine", "Massachusetts", "Michigan", "Minnesota", "Nevada", "New Hampshire", "New Jersey", "New York", "Ohio", "Oregon", "Pennsylvania", "Rhode Island", "Vermont", "Dist. of Col.", "Wisconsin"]

vote_columns = { 
    1860: [2, [5,8]],
    1868: [2, 5],
    1872: [2, 5],
    1876: [2, 5],
    1880: [2, 5],
    1884: [5, 2],
    1888: [2, 5],
    1892: [5, 2],
    1896: [2, 5],
    1896: [2, 5],
    1900: [2, 5],
    1904: [2, 5],
    1908: [2, 5],
    1912: [8, 2],
    1916: [5, 2],
    1920: [2, 5],
    1924: [2, 5],
    1928: [2, 5],
    1932: [5, 2],
    1936: [5, 2],
    1940: [5, 2],
    1944: [5, 2],
    1948: [5, 2],
    1952: [2, 5],
    1956: [2, 5],
    1960: [5, 2],
    1964: [5, 2],
    1968: [2, 5],
    1972: [2, 5],
    1976: [5, 2],
    1980: [2, 5],
    1984: [2, 5],
    1988: [2, 5],
    1992: [5, 2],
    1996: [5, 2],
    2000: [2, 5], 
    2004: [2, 5], 
    2008: [5, 2],
    2012: [5, 2],
    2016: [5, 2]
}
  
def get_votes(df, state, year, republican):
    cols = list(make_sequence(vote_columns[year][0 if republican else 1]))
    if state not in df.index: state = state + "*"
    if state not in df.index: return 0
    return df.loc[state][cols].apply(ignoring_exceptions(int, 0)).sum()

with open("datasets/politics_civilwar.csv", "w", encoding="utf-8") as f:
    print("year,union_rep,union_dem,conf_rep,conf_dem", file=f)
    for y in range(1860,2017,4):
        if y == 1864: continue
        tclass = "elections_states" if y != 1976 else "ver11"
        dfs = pd.read_html("http://www.presidency.ucsb.edu/showelection.php?year={}".format(y), "Alabama", attrs={"class": tclass})
        df = dfs[0]
        df = df.set_index(0)
        union_rep = sum(get_votes(df, s, y, True) for s in union)
        union_dem = sum(get_votes(df, s, y, False) for s in union)
        conf_rep = sum(get_votes(df, s, y, True) for s in confederate)
        conf_dem = sum(get_votes(df, s, y, False) for s in confederate)
        print("{},{},{},{},{}".format(y, union_rep, union_dem,conf_rep, conf_dem), file=f)
        
    
