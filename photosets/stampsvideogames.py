from pudzu.pillar import *
import pandas as pd

df = pd.read_csv("stampsvideogames.csv")

france = Image.from_url_with_cache("https://i.colnect.net/b/770/703/Video-Games.jpg").convert("RGBA").resize_fixed_aspect(width=800)

# fimgs = [Image.from_url_with_cache(img).convert("RGBA").resize_fixed_aspect(width=320) for img in df[df.group == "F"].image]
# france = Image.from_array(list(generate_batches(fimgs, 2)))

uimgs = [Image.from_url_with_cache(img).convert("RGBA").resize_fixed_aspect(width=320) for img in df[df.group == "U"].image]
uk = Image.from_array(list(generate_batches(uimgs, 2)))

ireland = [Image.from_url_with_cache(img).convert("RGBA").resize_fixed_aspect(width=480) for img in df[df.group == "I"].image][0]

img = Image.from_row([france, ireland, uk], bg="black", yalign=1, padding=20)

label = Image.from_text("Classic computer games on stamps from France (2005), Ireland (2014) and the UK (2020)".upper(), sans(64, bold=True), max_width=1180, fg="white", bg=None)
img = img.place(label, align=(1,0), padding=80)
img.convert("RGB").save("output/stampsvideogames.jpg")
