from matplotlib.dates import YearLocator
from pudzu.charts import line_chart, LineChartType
from pudzu.sandbox.bamboo import *
from pudzu.pillar import *

for pc in [False, True]:
    data = pd.read_excel("cache/Monthly-AE-Time-Series-January-2024.xls")[13:]
    if pc:
        data["Unnamed: 12"] = data["Unnamed: 12"] / data["Unnamed: 11"]
        data["Unnamed: 13"] = data["Unnamed: 13"] / data["Unnamed: 11"]
    df = data[["Unnamed: 1", "Unnamed: 12", "Unnamed: 13"]]
    df.columns = ["date", "≥4 hour wait", "≥12 hour wait"]
    df = df.set_index("date")

    chart = line_chart(df, 1800, 1000, type=LineChartType.AREA_OVERLAYED, ymin=0, xmin=df.index[0],
               xmax=df.index[-1], xticks=YearLocator(), ylabels="{x:.0%}" if pc else "{x:0,.0f}", ymax=0.35 if pc else 180_000,
               ylabel="proportion of emergency admissions affected" if pc else "monthly number of emergency admissions affected",
               dpi=150, grid=dict(color='gray', linestyle='--', linewidth=0.5), legend=dict(loc='upper left'),
               colors=["#6baed6", "#2171b5"]).trim((50,0))

    chart = chart.trim((0,100,0,50))
    title = Image.from_text_bounded("NHS England A&E trolley waits".upper(), chart.size, 80, partial(arial, bold=True), padding=(20,0))
    subtitle = Image.from_text_bounded("emergency admission patients waiting ≥4 hours from decision to admit to admission", (round(chart.width * 0.85), chart.height), 60, partial(arial, italics=False), padding=(20,10,20,20))
    footer = Image.from_markup("Source: [[https:\//www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/]]", partial(sans, 24), padding=20)
    img = Image.from_column([title, subtitle, chart, footer], bg="white")
    img.place(Image.from_text("/u/Udzu", arial(24), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=5, copy=False)
    img.save(f"output/uknhs-{pc}.png")

