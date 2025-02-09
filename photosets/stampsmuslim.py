from pudzu.pillar import *

synagogues = [
    "https://i.colnect.net/b/4476/718/Ben-Ezra-Synagogue.jpg",
    "https://i.colnect.net/b/5826/141/Al-Ghariba-Synagogue-Jirba.jpg",
    "https://i.colnect.net/b/4493/538/Chabad-Lubavich-Synagogue-Almaty.jpg",
    "https://i.colnect.net/b/8565/212/Ruins-of-synagogue-5th-cent-Sarand%C3%AB.jpg",
    "https://i.colnect.net/b/5344/203/Church-Mosque-and-Synagogue.jpg",
    "https://i.colnect.net/b/756/569/500th-Years-of-the-Admission-of-the-Spanish-Jews-in-Turkey.jpg",
    "https://i.colnect.net/b/8579/295/Holocaust-Arm-and-Feet-through-a-gate.jpg",
    "https://i.colnect.net/b/8579/318/Holocaust-Arm-and-Feet-through-a-gate.jpg",
    "https://i.colnect.net/b/950/849/Selahaddin-Ulkumen-1914-2003-Consul-General-in-Rhodes-at.jpg",
]

people = [
    "https://i.colnect.net/b/4474/346/Laila-Mourad-1918-95-singer-and-movie-star.jpg",
    "https://i.colnect.net/b/20025/462/Habiba-Msika-Singer.jpg",
    "https://i.colnect.net/b/8492/470/Gilbert-Naccache.jpg",
    "https://i.colnect.net/b/1603/625/Birth-Centenary-of-Lev-Landau-1908-1968.jpg",
    "https://i.colnect.net/b/7874/524/Birth-Centenary-of-Lotfi-Zadeh-Computer-Scientist.jpg",
    "https://i.colnect.net/b/8567/877/Norbert-Jokl.jpg",
    "https://i.colnect.net/b/475/761/Painters-of-Pakistan---Anna-Molka-Ahmed.jpg",
    "https://i.colnect.net/b/2632/195/Warriors-by-P-Zaltsman-1973.jpg",
]
banks = [
    "https://i.colnect.net/b/1308/713/41st-Anniversary-of-Misr-Bank.jpg",
    "https://i.colnect.net/b/4465/033/Misr-Bank-75th-anniv.jpg",
    "https://i.ebayimg.com/images/g/76sAAOSw0pFkGNHr/s-l1200.webp",
    "https://i.colnect.net/b/1367/936/50th-Anniversary-of-Bank-Al-Maghrib.jpg",
    "https://i.colnect.net/b/2160/155/Arabic-Inscription---University-Emblem.jpg",
    "https://i.colnect.net/b/2122/792/National-Assembly.jpg",
    "https://i.colnect.net/b/7825/408/Parliament-Building-Dhaka.jpg",
]
def line(*urls, n=100):
    imgs = [Image.from_url_with_cache(url).convert("RGBA").resize_fixed_aspect(height=200) for url in urls]
    imgs = list(generate_batches(imgs, n))
    return Image.from_column([Image.from_row(row, padding=5) for row in imgs], xalign=0, bg="black")


a = line(*synagogues, n=5); a.convert("RGB").save("output/stampsmuslim1.jpg")
b = line(*people, n=5); b.convert("RGB").save("output/stampsmuslim2.jpg")
d = line(*banks, n=4); d.convert("RGB").save("output/stampsmuslim4.jpg")

img = Image.from_column([a, b, d])
