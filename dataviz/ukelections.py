import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

COLORS = {
    "Conservatives": "#393b79",
    "Labour": "#d62728",
    "Liberal Democrats": "#e7ba52", "Alliance": "#e7ba52", "Liberal": "#e7ba52",
    "Liberal Democrats/\nAlliance/Liberals": "#e7ba52",
    "SNP": "#FDF38E",
    "UKIP": "#7b4173",
}
PARTIES = { v:k for k,v in COLORS.items() }
    
df = pd.read_csv("datasets/ukelections2.csv")
totals = df[df.party=="TOTAL"].set_index("year")
df = df[df.party != "TOTAL"].reset_index(drop=True)
df['votes_pc'] = 100 * df.votes / totals.loc[df.year].reset_index().votes
df['seats_pc'] = 100 * df.seats / totals.loc[df.year].reset_index().seats
df['colors'] = df.party.map(COLORS)

fig = plt.figure(figsize=(10,10), dpi=100)
ax = fig.gca()
for color,party in PARTIES.items():
    ax.scatter(x=df.votes_pc[df.colors==color], y=df.seats_pc[df.colors==color], c=color, s=80)
ax.set(xlim=(0,70), ylim=(0,70))
ax.legend(list(PARTIES.values()))
ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".3")
ax.plot(ax.get_xlim(), (50,50), c=".3")
ax.plot((50,50), ax.get_ylim(), c=".3")
ax.grid()
ax.xaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{int(y)}%')) 
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{int(y)}%')) 
for x,y,l in zip(df.votes_pc, df.seats_pc, df.year):
    plt.annotate(l, (x,y), textcoords="offset points", xytext=(0,7), ha='center')

plt.title('UK General Elections: vote share versus seat share (1979–2017)'.upper())
plt.xlabel('Share of votes cast')
plt.ylabel('Share of seats won')
plt.savefig("output/ukelections2.png", dpi='figure')
