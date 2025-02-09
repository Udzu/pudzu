import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

COLORS = {
    "Labour": "#d62728",
    "Conservatives": "#393b79",
    "Liberal Democrats": "#e7ba52", "Alliance": "#e7ba52", "Liberal": "#e7ba52",
    "Liberal Democrats/\nAlliance/Liberals": "#e7ba52",
    "SNP": "#FDF38E",
    "UKIP": "#7b4173",
    "Reform": "#12B6CF",
    "Greens": "#02A95B",
}
PARTIES = { v:k for k,v in COLORS.items() }
    
df = pd.read_csv("datasets/ukelections2.csv")
totals = df[df.party=="TOTAL"].set_index("year")
df = df[df.party != "TOTAL"].reset_index(drop=True)
df['votes_pc'] = 100 * df.votes / totals.loc[df.year].reset_index().votes
df['seats_pc'] = 100 * df.seats / totals.loc[df.year].reset_index().seats
df['colors'] = df.party.map(COLORS)
df['odds'] = df.votes_pc / (100 - df.votes_pc) / (df.seats_pc / (100 - df.seats_pc))
df['odds'] = np.where(df['odds']<1, 1/df['odds'],df['odds'])
df["winner"] = df.apply(lambda s: s.votes == df[df.year == s.year].votes.max(), axis=1)
df["opposition"] = df.apply(lambda s: s.votes == df[df.year == s.year].votes.nlargest(2).min(), axis=1)
df["marker"] = np.where(df["winner"], "^", np.where(df["opposition"], "v", "o"))

fig = plt.figure(figsize=(10,10), dpi=100)
ax = fig.gca()
ls = {}
for _, r in reversed(list(df.iterrows())):
    ls[COLORS[r.party]] = ax.scatter(x=r.votes_pc, y=r.seats_pc, c=r.colors, s=100, marker=r.marker)

ax.set(xlim=(0,70), ylim=(0,70))
legend = ax.legend([ls[p] for p in PARTIES], list(PARTIES.values()))
for handle in legend.legendHandles:
    handle._sizes = [100]
ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".3")
ax.plot(ax.get_xlim(), (50,50), c=".3")
ax.plot((50,50), ax.get_ylim(), c=".3")
ax.grid()
ax.xaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{int(y)}%')) 
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{int(y)}%')) 
for x,y,l in zip(df.votes_pc, df.seats_pc, df.year):
    plt.annotate(l, (x,y), textcoords="offset points", xytext=(0,7), ha='center')

plt.title('UK General Elections: vote share versus seat share (1979–2024)'.upper())
plt.xlabel('Share of votes cast')
plt.ylabel('Share of seats won')
plt.savefig("output/ukelections2.png", dpi='figure')
