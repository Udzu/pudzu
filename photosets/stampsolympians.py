from pudzu.pillar import *

olympians = [
"https://i.colnect.net/b/5221/705/Alfred-and-Gustav-Flatow-gymnastics-1896.jpg",
"https://i.colnect.net/b/3268/207/Alfred-Hajos-Guttman-Athens-1896.jpg",
"https://i.colnect.net/b/1055/474/Triple-jump-1904.jpg",
"https://i.colnect.net/b/3462/492/Jeno-Fuchs.jpg",
"https://i.colnect.net/b/7678/996/Fanny-Rosenfeld-100-m-and-400-m-Relay-1928.jpg",
"https://i.colnect.net/b/19551/345/Helene-Mayer-1910-1953.jpg",
"https://i.colnect.net/b/5203/466/Ellen-M%C3%BCller-Preis-Austria-fencer.jpg",
"https://cdn2.picryl.com/photo/1957/12/31/1957-iii-druzheskie-igry-molodyozhi-gimnastika-c35a25-1024.jpg",
"https://i.colnect.net/b/3462/461/Agnes-Keleti.jpg",
"https://i.colnect.net/b/1762/937/Oscar-Moglia-basketball.jpg",
"https://i.colnect.net/b/4267/690/Tamara-Press-shot-put-1960.jpg",
"https://i.colnect.net/b/2760/013/Mark-Spitz-USA-7-Gold-Medals-in-Swimming.jpg",
"https://i.colnect.net/b/7780/943/Faina-Melnik-1945-2016-Munich-1972.jpg",
"https://i.colnect.net/b/4385/289/Mitch-Gaylord-US.jpg",
"https://i.colnect.net/b/8347/976/Figure-skating.jpg",
"https://i.colnect.net/b/8194/303/Jessica-Fox---Canoe-Slalom-Women-s-Canoe.jpg",
"https://i.colnect.net/b/21859/659/Noemie-Fox-Canoeing.jpg",
]

medals = [
"https://i.colnect.net/b/20046/026/Canoe-single---double.jpg",
"https://i.colnect.net/b/8561/223/Relay-Race-Women.jpg",
"https://i.colnect.net/b/879/294/Fencing.jpg",
"https://i.colnect.net/b/21228/112/Silver-medalist-Andrea-Gyarmati.jpg",
"https://i.colnect.net/b/8754/546/Gold-medalist-Gy%C3%B6rgy-Gedo.jpg",
"https://i.colnect.net/b/5078/527/Boxing-and-silver-and-bronze-medals.jpg",
"https://i.colnect.net/b/2662/846/Judo.jpg",
"https://i.colnect.net/b/2662/847/Windsurfing.jpg",
"https://i.colnect.net/b/2662/848/Kayaking.jpg",
]

def line(*urls, n=100):
    imgs = [Image.from_url_with_cache(url).convert("RGBA").resize_fixed_aspect(height=200) for url in urls]
    imgs = list(generate_batches(imgs, n))
    return Image.from_column([Image.from_row(row, padding=5) for row in imgs], xalign=0, bg="black")


a = line(*olympians[:6]); a.convert("RGB").save("output/stampsolympians1.jpg")
b = line(*olympians[6:11]); b.convert("RGB").save("output/stampsolympians2.jpg")
c = line(*olympians[11:]); c.convert("RGB").save("output/stampsolympians3.jpg")

img = Image.from_column([a, b, c])
