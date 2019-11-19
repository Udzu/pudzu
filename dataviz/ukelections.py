import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLORS = {
    "Labour": "#d62728",
    "Conservatives": "#393b79",
    "Liberal Democrats": "#e7ba52", "Alliance": "#e7ba52", "Liberal": "#e7ba52",
    "UKIP": "#7b4173",
    "SNP": "#FDF38E"
}
    
df = pd.read_csv("datasets/ukelections2.csv")
totals = df[df.party=="TOTAL"].set_index("year")
df = df[df.party != "TOTAL"].reset_index(drop=True)
df['votes_pc'] = 100 * df.votes / totals.loc[df.year].reset_index().votes
df['seats_pc'] = 100 * df.seats / totals.loc[df.year].reset_index().seats
df['colors'] = df.party.map(COLORS)

ax = plt.figure().gca()

ax.scatter(x=df.votes_pc, y=df.seats_pc, c=df.colors, s=80)
ax.set(xlim=(0,70), ylim=(0,70))
ax.grid()
ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".3")
for x,y,l in zip(df.votes_pc, df.seats_pc, df.year):
    plt.annotate(l, (x,y), textcoords="offset points", xytext=(0,7), ha='center')

plt.title('UK election vote share versus seat share (1979-2017)')
plt.xlabel('Vote share (%)')
plt.ylabel('Seat share (%)')
plt.show()