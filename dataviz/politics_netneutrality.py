import sys
sys.path.append('..')
from charts import *
import seaborn as sns

PALETTE = tmap(RGBA, sns.color_palette())
DCOL = PALETTE[0]
RCOL = PALETTE[2]
ICOL = RGBA(126, 164, 226, 255)
FONT_SIZE = 16

LABELS = ["Republicans", "Democrats", "Independents\ncaucusing with\nDemocrats"]

CONGRESS = { "Aye": (234, 6, 0), "No": (2, 177, 0), "Not voting*": (4, 9, 0) }
congress = pd.DataFrame(CONGRESS, index=LABELS).transpose()

SENATE = { "Aye": (46, 0, 0), "No": (0, 50, 2), "Not voting": (1, 1, 0) }
senate = pd.DataFrame(SENATE, index=LABELS).transpose()

combined = pd.concat([congress, pd.DataFrame([{}], index=[""]), senate]).fillna(0)[LABELS]

img = bar_chart(combined, 80, 800, spacing=5, type=BarChartType.STACKED, colors=(RCOL, DCOL, ICOL), ymax=250,
    grid_interval=50, tick_interval=25, ylabels=arial(FONT_SIZE), rlabels=arial(FONT_SIZE), clabels=lambda c,r,v,w,h: None if v < 3 else Image.from_text_bounded(str(int(v)), (w,h), FONT_SIZE, papply(arial, bold=True), fg="white", padding=(0,0,0,1)),
    legend_box_sizes=(50,50), legend_fonts=papply(arial, FONT_SIZE), legend_position=(1, 0), legend_args={'header': "Party"})
h = img.height
img = img.pin(Image.from_text("HOUSE VOTE", arial(FONT_SIZE)), (200, h), align=(0.5,0))
img = img.pin(Image.from_text("SENATE VOTE", arial(FONT_SIZE)), (550, h), align=(0.5,0))
    
title = Image.from_text("vote breakdown of failed\n2011 resolution to nullify\nFCC net neutrality rules".upper(), arial(30, bold=True), "black", "white", padding=(0,10), align="center", max_width=700)
footer = Image.from_text("*includes 1 Republican who would have voted yes but for a medical matter", arial(16), "black", "white", padding=(0,5))
img = Image.from_column([title, img, footer], bg="white", padding=5)

# # Save
img = img.pad((10,10), "white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_netneutrality.png")
