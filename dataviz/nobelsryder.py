from pudzu.bamboo import *
from pudzu.charts import *

# analysis

countries = pd.read_csv("datasets/countries.csv").split_columns("country", "|").split_rows("country").set_index("country")
nobels = pd.read_csv("datasets/nobels.csv").split_columns("countries", "|")
nobels = nobels.assign_rows(eu=lambda r: any(countries.continent.get(c) == 'Europe' for c in r.countries))
nobels = nobels.assign_rows(us=lambda r: any(c == "US" for c in r.countries))
countries.loc["Turkey", "continent"] = "Europe"
years = list(range(nobels.date.min(), nobels.date.max()+1))

def calc_scores(filter):
    scores = nobels[filter].groupby("date").sum()
    scores = scores.assign_rows(winner=lambda r: "us" if r.us>r.eu else "eu" if r.eu>r.us else "tie")
    return scores.reindex(years).fillna({"eu": 0, "us": 0, "winner": "tie"})
    
FILTERS = [
    nobels.category == nobels.category, 
    ~nobels.category.isin(["Economics"]),
    nobels.category.isin(["Chemistry", "Physics", "Physiology and Medicine"])]

winners = pd.concat([calc_scores(filter).winner for filter in FILTERS], axis=1)
winners.columns = ["all", "official", "science"]
    
science_winners = calc_scores(FILTERS[2])[["eu","us"]]
humanity_winners = calc_scores(FILTERS[1])[["eu","us"]] - calc_scores(FILTERS[2])[["eu","us"]]
economics_winners = calc_scores(FILTERS[0])[["eu","us"]] - calc_scores(FILTERS[1])[["eu","us"]]

# visualisation

FONT = arial
COLORS = { "eu": VegaPalette10.BLUE, "us": VegaPalette10.RED, "tie": "#BBBBBB" }

def summary_cell(winner):
    label = {"eu": "E", "us": "US", "tie": "=" }
    return Rectangle(20, COLORS[winner]).place(Image.from_text(label[winner], FONT(10, bold=True)))

summary_labels = Image.from_text("Winner**".upper(), FONT(10, bold=True), padding=(0,5), beard_line=True)
summary = Image.from_column([summary_labels, Image.from_array([tmap(summary_cell, r) for r in winners.values.tolist()])])

def winner_row(type, year):
    row = ([Rectangle(20, COLORS[type])] * int(science_winners[type].get(year,0)) +
          [Rectangle(20, COLORS[type].brighten(0.25))] * int(humanity_winners[type].get(year,0)) +
          [Rectangle(20, COLORS[type].brighten(0.5))] * int(economics_winners[type].get(year,0)))
    if type == "us": row = row[::-1]
    return Image.from_row(row) if row else Rectangle((0,20))
    
def year_label(year):
    return Rectangle((40,20), "white").place(Image.from_text(str(year), FONT(10, bold=True)))
    
results_labels = [Image.from_text(s.upper(), FONT(10, bold=True), padding=(0,5), beard_line=True) for s in ["American winners", "year", "European winners"]]
results = Image.from_array([results_labels] + [[winner_row("us",y), year_label(y), winner_row("eu",y)] for y in range(nobels.date.min(), nobels.date.max()+1)], xalign=(1,0.5, 0))

grid = Image.from_row([results, summary], padding=20, bg="white", yalign=1).pad((100,0,0,0), "white")

boxes = [Image.from_row([Rectangle(30, COLORS["eu"].brighten(n)), Rectangle(30, COLORS["us"].brighten(n))]) for n in (0, 0.25, 0.5)]
legend1 = generate_legend(boxes, ["Sciences", "Peace/Literature", "Economics"], font_family=partial(FONT, 16), header="Prize categories".upper(), border=False)
results = [winners.groupby(c).size().to_dict() for c in winners.columns]
results_text = ["{} v {} ({} ties)".format(d["eu"], d["us"], d["tie"]) for d in results]
legend2 = generate_legend([], [], font_family=partial(FONT, 16), header="Overall winners".upper(), footer=Image.from_array(
[[Image.from_text(type, FONT(16)), Image.from_text(result, FONT(16, bold=True))] for type,result in zip(["All Prizes:", "w/o Economics:", "Science Prizes:"], results_text)], xalign=0, padding=4
), border=False)
legend3 = Image.from_text("* based on winners' nationalities at or before the time of award; Russian and Turkish winners are counted as European; dual nationals may be counted as both European and American.\n** the three winner columns correspond to: all the prizes; all the prizes apart from Economics; and only the science prizes.", FONT(12, italics=True), max_width=legend2.width, padding=4)
legend = Image.from_column([legend1, legend2, legend3], xalign=0, bg="white").pad(1, "black")

gridlegend = grid.place(legend, align=0, padding=(40,80))

title = Image.from_text_justified("Nobel Prize Ryder Cup".upper(), grid.width-60, 80, partial(FONT, bold=True), bg="white", padding=(0,20,0,5))
subtitle = Image.from_text_justified("US versus European* Nobel laureates per year", grid.width-60, 80, partial(FONT, bold=True), bg="white", padding=(0,5,0,5))

img = Image.from_column([title, subtitle, gridlegend], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((0,1,1,0), "black"), align=(0,1), padding=10, copy=False)
img.save("output/nobelsryder.png")

