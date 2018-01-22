import sys
sys.path.append('..')
from charts import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index("country")
df = pd.read_csv("datasets/g7_policedeaths.csv").set_index("country")
df["police_pm"] = df["police_total"] * 1000000 / atlas.ix[df.index].population
