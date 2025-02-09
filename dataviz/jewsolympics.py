from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from pudzu.pillar import *

# accidentally lost original, so this is only the diffs since 2016!

data = [
    (2016, 1 + 1/7 + 1/12 + 1/5, 2 + 1/2 + 1/9, 3),
    (2020, 1 + 1/2 + 1 + 1/4 + 1, 0, 1 + 1 + 1),
]
df = pd.DataFrame(data, columns=["year", "gold", "silver", "bronze"])

W, H = 60, 40
PALETTE = ["#fcc900", "#d3d3d3", "#d26c00"]

def rlabel(r):
    return Image.from_text(f"{df.year[r]}", sans(16)).transpose(Image.ROTATE_90)

def f(v):
    return f"{int(v)}" if v == int(v) else f"{v:.1f}"

chart = bar_chart(df[["gold", "silver", "bronze"]], W, 600, BarChartType.STACKED, colors=PALETTE,
                   grid_interval=1, label_font=sans(14), label_interval=5,
                  ymax=20,
    rlabels=rlabel, spacing=1,
    clabels = lambda c,r,v: f(v),
    ylabel=Image.from_text("weighted number of medals won", sans(16), padding=5).transpose(Image.ROTATE_90)
)

#
# title = Image.from_text("European countries at the Summer Paralympics".upper(), sans(64, bold=True), padding=20)
# subtitle = Image.from_text("all-time medals won per country (and number of Games competed in in parentheses)", sans(32, italics=True), VegaPalette10.RED, padding=0)
# titles = Image.from_column([title, subtitle], bg="#FFFFFFAA")
# img = chart.place(titles, align=(0.5,0))
# img = img.pad((0,20,20,20), "white")
# img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)
#
chart.save("output/jewsolympics.png")
#

# TODO: remove S(0.1) from 1908 rugby GB (and totals)

# Multiple medallists

"""
{| class="wikitable" style="text-align:center; font-size:100%"
|+ Multiple medalists
|-
! |Athlete
! |Country
! |Sport
! style="width:3.5em; font-weight:bold;"|{{gold medal}}
! style="width:3.5em; font-weight:bold;"|{{silver medal}}
! style="width:3.5em; font-weight:bold;"|{{bronze medal}}
! style="width:3.5em;"|Total
|- 
|style="text-align:left"| '''[[Dara Torres]]''' ||style="text-align:left"| {{flagIOC|USA}} ||style="text-align:left"| {{OlympicEvent|Swimming|2024 Summer|image=Yes}} 
|| 4 || 4 || 4 || '''12'''
|- 
|style="text-align:left"| '''[[Mark Spitz]]''' ||style="text-align:left"| {{flagIOC|USA}} ||style="text-align:left"| {{OlympicEvent|Swimming|2024 Summer|image=Yes}} 
|| 9 || 1 || 1 || '''11'''
|- 
|style="text-align:left"| '''[[Ágnes Keleti]]''' ||style="text-align:left"| {{flagIOC|HUN}} ||style="text-align:left"| {{OlympicEvent|Gymnastics|2024 Summer|image=Yes}} 
|| 5 || 3 || 2 || '''10'''
|- 
|style="text-align:left"| '''[[Jason Lezak]]''' ||style="text-align:left"| {{flagIOC|USA}} ||style="text-align:left"| {{OlympicEvent|Swimming|2024 Summer|image=Yes}} 
|| 4 || 2 || 2 || '''8'''
|- 
|style="text-align:left"| '''[[Irena Szewińska]]''' ||style="text-align:left"| {{flagIOC|POL}} ||style="text-align:left"| {{OlympicEvent|Athletics|2024 Summer|image=Yes}} 
|| 3 || 2 || 2 || '''7'''
|- 
|style="text-align:left"| '''[[Maria Gorokhovskaya]]''' ||style="text-align:left"| {{flagIOC|URS}} ||style="text-align:left"| {{OlympicEvent|Gymnastics|2024 Summer|image=Yes}} 
|| 2 || 5 || - || '''7'''
|- 
|style="text-align:left"| '''[[Ildikó Rejtő]]''' ||style="text-align:left"| {{flagIOC|HUN}} ||style="text-align:left"| {{OlympicEvent|Fencing|2024 Summer|image=Yes}} 
|| 2 || 3 || 2 || '''7'''
|- 
|style="text-align:left"| '''[[Rudolf Kárpáti]]''' ||style="text-align:left"| {{flagIOC|HUN}} ||style="text-align:left"| {{OlympicEvent|Fencing|2024 Summer|image=Yes}} 
|| 6 || - || - || '''6'''
|- 
|style="text-align:left"| '''[[Aly Raisman]]''' ||style="text-align:left"| {{flagIOC|USA}} ||style="text-align:left"| {{OlympicEvent|Gymnastics|2024 Summer|image=Yes}} 
|| 3 || 2 || 1 || '''6'''
|- 
|style="text-align:left"| '''[[Jessica Fox (canoeist)|]]''' ||style="text-align:left"| {{flagIOC|AUS}} ||style="text-align:left"| {{OlympicEvent|Sailing|2024 Summer|image=Yes}} 
|| 3 || 1 || 2 || '''6'''
|}
"""
# Medals by games

# TODO: 2024, update total

"""
{| class="wikitable" style="text-align:center; font-size:90%"
|+ Medals by Games
|-
!Games
! style="width:3em; font-weight:bold;"|{{gold medal}}
! style="width:3em; font-weight:bold;"|{{silver medal}}
! style="width:3em; font-weight:bold;"|{{bronze medal}}
!style="width:3em; font-weight:bold;"|Total
!style="width:3em; font-weight:bold;"|Rank
|-
|style="text-align:left"| {{flagicon|Kingdom of Greece}} {{GamesName|SOG|1896}} || 5.4 || 2 || 2 || '''9.4''' || [[1896 Summer Olympics medal table|3]] 
|-
|style="text-align:left"| {{flagicon|France}} {{GamesName|SOG|1900}} || 1 || 3.4 || 1 || '''5.4''' || [[1900 Summer Olympics medal table|10]] 
|-
|style="text-align:left"| {{flagicon|US}} {{GamesName|SOG|1904}} || 3 || 1.1 || 1 || '''5.1''' || [[1904 Summer Olympics medal table|5]] 
|-
|style="text-align:left"| {{flagicon|UK}} {{GamesName|SOG|1908}} || 2.1 || 2.9 || 2.2 || '''7.1''' || [[1908 Summer Olympics medal table|7]] 
|-
|style="text-align:left"| {{flagicon|Sweden}} {{GamesName|SOG|1912}} || 1.0 || 4.1 || 0.8 || '''5.9''' || [[1912 Summer Olympics medal table|15]] 
|-
|style="text-align:left"| {{flagicon|Belgium}} {{GamesName|SOG|1920}} || 1 || 2.2 || 3.1 || '''6.4''' || [[1920 Summer Olympics medal table|14]] 
|-
|style="text-align:left"| {{flagicon|France}} {{GamesName|SOG|1924}} || 2.6 || 1.6 || 2.2 || '''6.3''' || [[1924 Summer Olympics medal table|12]] 
|-
|style="text-align:left"| {{flagicon|Netherlands}} {{GamesName|SOG|1928}} || 3.2 || 3.1 || 3.2 || '''9.6''' || [[1928 Summer Olympics medal table|11]] 
|-
|style="text-align:left"| {{flagicon|US}} {{GamesName|SOG|1932}} || 2.6 || 4.5 || 5.5 || '''12.6''' || [[1932 Summer Olympics medal table|12]] 
|-
|style="text-align:left"| {{flagicon|Nazi Germany}} {{GamesName|SOG|1936}} || 3.4 || 2.6 || 0.1 || '''6.1''' || [[1936 Summer Olympics medal table|11]] 
|-
|style="text-align:left"| {{flagicon|UK}} {{GamesName|SOG|1948}} || 2.2 || 1 || 1.3 || '''4.6''' || [[1948 Summer Olympics medal table|14]] 
|-
|style="text-align:left"| {{flagicon|Finland}} {{GamesName|SOG|1952}} || 6.1 || 6.4 || 5.1 || '''17.6''' || [[1952 Summer Olympics medal table|7]] 
|-
|style="text-align:left"| {{flagicon|Australia}} {{GamesName|SOG|1956}} || 9.0 || 2.5 || 1.4 || '''12.9''' || [[1956 Summer Olympics medal table|4]] 
|-
|style="text-align:left"| {{flagicon|Italy}} {{GamesName|SOG|1960}} || 4.2 || 4.0 || 4.4 || '''12.6''' || [[1960 Summer Olympics medal table|8]] 
|-
|style="text-align:left"| {{flagicon|Japan}} {{GamesName|SOG|1964}} || 7.3 || 4.1 || 2.2 || '''13.6''' || [[1964 Summer Olympics medal table|7]] 
|-
|style="text-align:left"| {{flagicon|Mexico}} {{GamesName|SOG|1968}} || 3.7 || 3.8 || 4.0 || '''11.5''' || [[1968 Summer Olympics medal table|13]] 
|-
|style="text-align:left"| {{flagicon|West Germany}} {{GamesName|SOG|1972}} || 6.9 || 1.9 || 3.8 || '''12.6''' || [[1972 Summer Olympics medal table|8]] 
|-
|style="text-align:left"| {{flagicon|Canada}} {{GamesName|SOG|1976}} || 2.3 || 0.8 || 2.6 || '''5.6''' || [[1976 Summer Olympics medal table|14]] 
|-
|style="text-align:left"| {{flagicon|Soviet Union}} {{GamesName|SOG|1980}} || 1.5 || 1 || - || '''2.5''' || [[1980 Summer Olympics medal table|20]] 
|-
|style="text-align:left"| {{flagicon|US}} {{GamesName|SOG|1984}} || 0.4 || 2.4 || 3 || '''5.8''' || [[1984 Summer Olympics medal table|28]]
|-
|style="text-align:left"| {{flagicon|South Korea}} {{GamesName|SOG|1988}} || 1.2 || 0.1 || 1.3 || '''2.6''' || [[1988 Summer Olympics medal table|24]] 
|-
|style="text-align:left"| {{flagicon|Spain}} {{GamesName|SOG|1992}} || 2.0 || 1.1 || 3.5 || '''6.5''' || [[1992 Summer Olympics medal table|25]] 
|-
|style="text-align:left"| {{flagicon|US}} {{GamesName|SOG|1996}} || 0.5 || 2 || 2.6 || '''5.1''' || [[1996 Summer Olympics medal table|54]]
|-
|style="text-align:left"| {{flagicon|Australia}} {{GamesName|SOG|2000}} || 4.2 || 2 || 4.2 || '''10.5''' || [[2000 Summer Olympics medal table|17]]
|-
|style="text-align:left"| {{flagicon|Greece}} {{GamesName|SOG|2004}} || 3.0 || 0.5 || 3.9 || '''7.4''' || [[2004 Summer Olympics medal table|26]] 
|-
|style="text-align:left"| {{flagicon|China}} {{GamesName|SOG|2008}} || 0.8 || 2.7 || 2.4 || '''5.9''' || [[2008 Summer Olympics medal table|56]] 
|-
|style="text-align:left"| {{flagicon|UK}} {{GamesName|SOG|2012}} || 2.3 || 1.1 || 2 || 5.4 || |[[2012 Summer Olympics medal table|27]] 
|-
|style="text-align:left"| {{flagicon|Brazil}} {{GamesName|SOG|2016}} || 1.4 || 2.6 || 3 || '''7.0''' || [[2016 Summer Olympics medal table|39]] 
|-
|style="text-align:left"| {{flagicon|Japan}} {{GamesName|SOG|2020}} || 3.8 || - || 3 || '''6.8''' || [[2020 Summer Olympics medal table|22]] 
|-
|style="text-align:left"| {{flagicon|France}} {{GamesName|SOG|2024}} ||  ||  ||  ||  || [[2024 Summer Olympics medal table| ]] 
|-
!colspan=1| Total !! 84.3 !! 67.6 !! 71.9 || 223.9 || [[All-time Olympic Games medal table|18]] 
|}
"""

# Medals by sport

# 2020
# gymnastics: G(1 + 1 + 1/4)
# beach volleyball: G(1/2)
# canoeing: G(1) + B(1)
# taekwondo: B(1)
# judo: B(1)

# 2024
# canoeing: G(2 + 1)
# fencing: G(1/4 + 1/4) + B(1)
# sailing: G(1) + S(1)
# wrestling: G(1)
# judo: S(1+1)+B(1)
# gymnastics: S(1)
# swimming: S(1/4)
# rugby: B(1/12)
# athletics: B(1)

# TODO: reproduce, update, update ranks

"""
{| class="wikitable" style="text-align:center; font-size:90%"
|+ Medals by Sport
|-
!Sport
! style="width:3em; font-weight:bold;"|{{gold medal}}
! style="width:3em; font-weight:bold;"|{{silver medal}}
! style="width:3em; font-weight:bold;"|{{bronze medal}}
!style="width:3em; font-weight:bold;"|Total
!style="width:3em; font-weight:bold;"|Rank
|-
|style="text-align:left"| {{OlympicEvent|Swimming|2024 Summer|image=Yes}} || 15.5 || 9.6 || 15.1 || '''40.3''' || [[1896 Summer Olympics medal table|8]] 
|-
!colspan=1| Total !! 84.3 !! 67.6 !! 71.9 || 223.9 || [[All-time Olympic Games medal table|18]] 
|}
"""

# Medals by country

# 2020
# Israel: G(1 + 1) + B(1 + 1)
# Australia: G(1) + B(1)
# ROC: G(1/4)
# USA: G(1/2)

# 2024
# Australia: G(2)+B(1)
# Israel: G(1) + S(4) + B(1)
# USA: G(2/4) + S(1/4) + B(1+1/12)

# TODO: reproduce, update, update %s

"""
{| class="wikitable" style="text-align:center; font-size:90%"
|+ Medals by Country
|-
!Country
! style="width:3em; font-weight:bold;"|{{gold medal}}
! style="width:3em; font-weight:bold;"|{{silver medal}}
! style="width:3em; font-weight:bold;"|{{bronze medal}}
!style="width:3em; font-weight:bold;"|Total
!style="width:3em; font-weight:bold;"|% of all
|-
|style="text-align:left"| {{flagIOC|USA}} || 25.7 || 22.9 || 25.7 || '''74.3''' || 2.9% 
|-
!colspan=1| Total !! 84.3 !! 67.6 !! 71.9 || 223.9 || 1.4%
|}
"""