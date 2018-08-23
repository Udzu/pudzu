import sys
sys.path.append('..')
from charts import *

FONT = calibri
SCALE = 2
FONTSIZE = round(16*SCALE)
BIGFONT = round(18*SCALE)
SMALLFONT = round(14*SCALE)
SUBTITLEFONT = round(36*SCALE)
TITLEFONT = SIZE = round(40*SCALE)

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index("country")
df = pd.read_csv("datasets/g7_policedeaths.csv").set_index("country")
df["policedeaths_pm"] = df["policedeaths_total"] * 1000000 / atlas.loc[df.index].population

# Bar charts

def rlabel(r):
    return Image.from_row([
        Image.from_text(df.index[r].replace("\\n","\n"), FONT(FONTSIZE), "black", align="center"),
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((round(SIZE*1.5),SIZE)).trim(SCALE).pad(SCALE, "grey")
    ], padding=(2*SCALE,0))

def label_if(pred, labeler=lambda c,r,v: format_float(v, 3)): # TODO: automate this bit
    return lambda c,r,v: None if not pred(v) else labeler(c,r,v)

df = df.sort_values("guns_ph", ascending=False)
guns = bar_chart(df[["guns_ph"]], SIZE, SIZE*10, bg=None, horizontal=True, spacing=2*SCALE, label_font=FONT(FONTSIZE), rlabels=rlabel,
    clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,15)),
               BarChartLabelPosition.OUTSIDE : label_if(artial(op.lt,15))},
    grid_interval=10, ymax=120, ylabel=Image.from_text("privately owned guns per 100 population (2017)", FONT(BIGFONT), padding=5*SCALE))
    
df = df.sort_values("homicide_pm", ascending=False)
homicides = bar_chart(df[["homicide_pm"]], SIZE, SIZE*10, bg=None, horizontal=True, spacing=2*SCALE, label_font=FONT(FONTSIZE), rlabels=rlabel,
    clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,10), lambda c,r,v: "{:.1f} ({:,} total)".format(v, df.homicide_total[df.index[r]])),
               BarChartLabelPosition.OUTSIDE : label_if(artial(op.lt,10), lambda c,r,v: "{:.1f} ({:,} total)".format(v, df.homicide_total[df.index[r]]) + (df.index[r] == "Japan")*" (lower than the US police’s killing rate!)")},
    grid_interval=5, ymax=50, ylabel=Image.from_text("intentional homicides per million population (2015)", FONT(BIGFONT), padding=5*SCALE))

df = df.sort_values("policedeaths_pm", ascending=False)
policedeaths = bar_chart(df[["policedeaths_pm"]], SIZE, SIZE*15, bg=None, horizontal=True, spacing=2*SCALE, label_font=FONT(FONTSIZE), rlabels=rlabel,
    clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,0.5), lambda c,r,v: "{:.2f} ({:,} total)".format(v, df.policedeaths_total[df.index[r]])),
             BarChartLabelPosition.OUTSIDE: label_if(artial(op.lt,0.5), lambda c,r,v: "{:.1g} ({:,} total)".format(v, df.policedeaths_total[df.index[r]])) },
    grid_interval=0.25, label_interval=0.5, ymax=3.6, ylabel=Image.from_multitext(["killings by law enforcement officers per million population (2015) ", "(estimates)"], [FONT(BIGFONT), FONT(SMALLFONT)]).pad(5*SCALE,0))

# Put it all together

chart = Image.from_column([policedeaths, Image.from_row([guns, homicides])], padding=10*SCALE)
title = Image.from_column([Image.from_text("Police killing rates in G7 members".upper(), FONT(TITLEFONT, bold=True)), Image.from_text("compared to gun ownership and homicide rates", FONT(SUBTITLEFONT))])
# footer = Image.from_markup(
# "**Police killing estimates** from //The Counted// (US), //A Toutes Les Victimes// (France), //UK Home Office// (UK),\n  //Schusswaffeneinsatz.de// (Germany), //Wikipedia// (Canada), //ACAD// (Italy) and additional media reports.\n"
# "**Gun ownership data** from the //IHEID Small Arms Survey (2007)//.\n"
# "**Homicide data** from the //United Nations Office on Drugs and Crime// website.", partial(FONT, FONTSIZE), padding=5*SCALE)

img = Image.from_column([title, chart], padding=5*SCALE, bg="white")
# background = Image.from_url_with_cache("http://trueblueline.net/wp-content/uploads/2015/05/o-POLICE-LIGHTS-facebook.jpg").crop_to_aspect(img.width, img.height).resize(img.size).brighten(0.75)
# img = background.place(img)
#img.place(Image.from_text("/u/Udzu", font("arial", FONTSIZE), fg="black", bg=None, padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/g7_police.png")
