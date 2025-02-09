from pudzu.pillar import *

torah = "https://i.ebayimg.com/images/g/gSkAAOSwftRllDtS/s-l1600.jpg"
torahs = [
 "https://i.colnect.net/b/2589/272/Torah-Scroll.jpg",
 "https://i.colnect.net/b/2593/742/Scroll-of-the-Torah-Mosaic-Law---012.jpg",
 "https://i.colnect.net/b/2593/748/Scroll-of-the-Torah-Mosaic-Law---035.jpg",
 "https://i.colnect.net/b/2593/746/Scroll-of-the-Torah-Mosaic-Law---040.jpg",
 "https://i.colnect.net/b/2593/752/Scroll-of-the-Torah-Mosaic-Law---080.jpg",
 "https://i.colnect.net/b/2593/744/Scroll-of-the-Torah-Mosaic-Law---015.jpg"
]
aruch = "https://i.colnect.net/b/2593/722/Shulhan-Arukh-Lawcode-Compendium-400-Years.jpg"

weimar = "https://i.colnect.net/b/19308/755/Centenary-of-the-Weimar-Constitution.jpg"
austria = "https://i.colnect.net/b/7188/317/Centenary-of-the-Austrian-Federal-Constitution.jpg"
japan = "https://i.colnect.net/b/7527/341/Enforcement-of-the-New-Constitution-1947.jpg"
hungary = "https://i.colnect.net/b/21142/224/National-coat-of-arms.jpg"
udhr = "https://i.colnect.net/b/6029/158/Flame-and-Hands.jpg"
netherlands = "https://i.colnect.net/b/2193/790/New-Netherlands-Civil-Code--Burgerlijk-Wetboek-.jpg"
france = "https://files.ekmcdn.com/sdcollectable/images/france-sg3531-1998-constitution-3f-good-fine-used-1181-p.jpg?v=30e8d882-8eb8-4cdc-93dd-ddabf37dd205"

def line(*urls):
    imgs = [Image.from_url_with_cache(url).convert("RGBA").resize_fixed_aspect(height=200) for url in urls]
    return Image.from_row(imgs, padding=5, bg="black")
    
a = line(*torahs, aruch, weimar, austria)
b = line(japan, udhr, hungary, netherlands, france)
c = Image.from_column([a,b])

a.convert("RGB").save("output/stampsjewishlegal1.jpg")
b.convert("RGB").save("output/stampsjewishlegal2.jpg")
