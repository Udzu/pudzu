import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/eumonarchies.csv").set_index('country')

republics = ImageColor.from_floats(sns.color_palette("Blues", 4))
monarchies = "#CC5555"
never = RGBA(207,215,225,255)

def colorfn(c):
    abolished = ValueCache()
    if c not in df.index:
        return None if c == 'Sea' else "grey"
    elif df['monarchy'][c]:
        return monarchies
    elif none_or_nan(df['abolished'][c]):
        return never
    elif abolished.set(int(re.search('[0-9]+', df['abolished'][c]).group())) < 1914:
        return republics[1]
    elif abolished.value < 1939:
        return republics[2]
    else:
        return republics[3]
    
map = map_chart("maps/Europe.png", colorfn, ignoring_exceptions(lambda c: str(get_non(df.loc[c], "abolished", ""))), label_font=arial(16, bold=True))

title = Image.from_column([
Image.from_text("THE KING IS DEAD", arial(48, bold=True)),
Image.from_text("abolition of monarchies in Europe", arial(36))],
bg="white")

chart = Image.from_column([title.pad((0,5),"white"), map], bg="white")

