from pudzu.pillar import *

rothschild = "https://i.colnect.net/b/5949/682/Rothschild-s-Myna-Leucopsar-rothschildi.jpg"
axelrod = "https://i.colnect.net/b/18922/589/Cardinal-Tetra-Cheirodon-axelrodi.jpg"
kandt = "https://i.colnect.net/b/7488/345/Golden-monkey-Cercopithecus-kandti.jpg"
neumann = "https://i.imgur.com/ID9qCgT.jpg"
frankel = "https://www.collectgbstamps.co.uk/images/gb/2017/2017_8814_l.jpg"

marx = "https://i.colnect.net/b/4473/883/Karl-Marx-Stadt.jpg"
sverdlov = "https://i.colnect.net/b/6321/977/Statue-of-Yakov-Sverdlov.jpg"
rakosi = "https://i.colnect.net/b/21113/383/R%C3%A1kosi-House-of-Culture-Type-I.jpg"
luxembourg = "https://i.colnect.net/b/8008/114/Engineering-School--Rosa-Luxembourg-.jpg"
ephraim = "https://i.colnect.net/b/19590/774/Ephraim-Palais.jpg"

citroen = "https://i.imgur.com/CRRWtTx.jpg"
olivetti = "https://i.colnect.net/b/668/580/Olivetti-Typewriters-Production.jpg"
philips = "https://www.optischefenomenen.nl/cache/images/8/4/8/gerard-leonard-frederik-philips-1858-1942-800x600-8316.jpg"
marx2 = "https://i.colnect.net/b/5091/162/Steam-Locomotive---Gowan-and-Marx-1839.jpg"
mercedes = "https://thumbs.dreamstime.com/b/monaco-circa-stamp-printed-monaco-veteran-cars-issue-shows-mercedes-circa-monaco-circa-stamp-printed-monaco-171669101.jpg"

lasker = "https://www.kenmorestamp.com/media/catalog/product/cache/9d5edec8622712b9afac34ccb2611c8e/u/s/us_3432b.jpg"
woolf = "https://i.colnect.net/b/449/749/Virginia-Woolf-photo-by-George-Charles-Beresford.jpg"
einstein = "https://i.colnect.net/b/4580/753/Mileva-Mari%C4%87-Einstein-Scientist.jpg"

def line(*urls):
    imgs = [Image.from_url_with_cache(url).convert("RGBA").resize_fixed_aspect(height=200) for url in urls]
    return Image.from_row(imgs, padding=5, bg="black")


a = line(rothschild, axelrod, neumann, kandt, frankel)
b = line(marx, sverdlov, rakosi, luxembourg, ephraim)
c = line(citroen, olivetti, philips, marx2, mercedes)
d = line(woolf, lasker, einstein)

a.convert("RGB").save("output/stampsnamesakes1.jpg")
b.convert("RGB").save("output/stampsnamesakes2.jpg")
c.convert("RGB").save("output/stampsnamesakes3.jpg")
d.convert("RGB").save("output/stampsnamesakes4.jpg")

img = Image.from_column([a,b,c,d])
