import sys
sys.path.append('..')
from charts import *
from bamboo import *

df = pd.read_csv("datasets/eucapitals.csv")
data = pd.DataFrame(list(generate_batches([dict(row) for _,row in df.iterrows()], 4))[:2])
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

flags = { "Kosovo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Kosovo.svg/1024px-Flag_of_Kosovo.svg.png",
          "Abkhazia": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Abkhazia.svg/1024px-Flag_of_Abkhazia.svg.png",
          "South Ossetia": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Flag_of_South_Ossetia.svg/1024px-Flag_of_South_Ossetia.svg.png",
          "Northern Cyprus": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Flag_of_the_Turkish_Republic_of_Northern_Cyprus.svg/1024px-Flag_of_the_Turkish_Republic_of_Northern_Cyprus.svg.png",
          "Artsakh": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Flag_of_Artsakh.svg/1024px-Flag_of_Artsakh.svg.png",
          "Transnistria": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Transnistria_%28state%29.svg/1024px-Flag_of_Transnistria_%28state%29.svg.png",
          "Donetsk People's Republic": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Donetsk_People%27s_Republic_flag.png",
          "Luhansk People's Republic": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Flag_of_the_Lugansk_People%27s_Republic_%28Official%29.svg/1024px-Flag_of_the_Lugansk_People%27s_Republic_%28Official%29.svg.png",
          "Catalonia": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Estelada_blava.svg/1024px-Estelada_blava.svg.png",
          "Republika Srpska": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Flag_of_Republika_Srpska.svg/1280px-Flag_of_Republika_Srpska.svg.png",
          "Scotland": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1000px-Flag_of_Scotland.svg.png",
          "Basque Country": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Flag_of_the_Basque_Country.svg/1024px-Flag_of_the_Basque_Country.svg.png"
}

cityflags = { "Kosovo": "http://www.crwflags.com/fotw/images/r/rs-prist.gif",
          "Abkhazia": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Flag_of_None.svg/1024px-Flag_of_None.svg.png",
          "South Ossetia": "https://flagspot.net/images/g/ge-tskn.gif",
          "Northern Cyprus": "https://flagspot.net/images/c/cy-t-nic.gif",
          "Artsakh": "https://flagspot.net/images/a/az-step.gif",
          "Transnistria": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Flag_of_Tiraspol.svg/552px-Flag_of_Tiraspol.svg.png",
          "Donetsk People's Republic": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Flag_of_Donetsk.svg/1280px-Flag_of_Donetsk.svg.png",
          "Luhansk People's Republic": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Flag_of_Luhansk.svg/1024px-Flag_of_Luhansk.svg.png"
}     

def process(d):
    return Image.from_column([
      Image.from_text(d['country'], arial(24, bold=True), fg=fg, bg=bg),
      Image.from_text(d['state'], arial(24, italics=True), max_width=320, align="center", fg=fg, bg=bg),
      Image.from_text("({})".format(d['recognition']), arial(24, italics=False), max_width=320, align="center", padding=(0,0,0,4), fg=fg, bg=bg),
      Image.from_url_with_cache(flags.get(d['country'], default_img)).resize((318,198)).pad(1, "grey"),
      Image.from_text(d['capital'], arial(24, bold=True), fg=fg, bg=bg),
      Image.from_text("(pop. {})".format(d['population']), arial(24, bold=False), fg=fg, bg=bg),
      Image.from_url_with_cache(cityflags.get(d['country'], default_img)).resize((318,198)).pad(1, "grey"),
      Image.from_url_with_cache(get_non(d, "image", default_img)).crop_to_aspect(200, 200, (0.5, 0.2)).resize_fixed_aspect(width=320)
      ], padding=4, bg=bg)

title = Image.from_column([
    Image.from_text("Unrecognised capital cities of Europe", arial(72, bold=True), fg=fg, bg=bg),
    Image.from_text("de facto capital cities of unrecognised or partly recognised states", arial(48, italics=True), fg=fg, bg=bg)
    ], bg=bg)
      
grid = grid_chart(data, process, padding=(10,20), bg=bg, yalign=0, title=title).pad(20, bg)
grid.save("output/flagseurope.png")
