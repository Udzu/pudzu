from pudzu.pillar import *


for country in ["poland", "belgium", "polishpolish", "hungary"]:
    if country == "polishpolish":
        title = "Polish-themed stamps from around the world"
    else:
        title = f"Jewish-themed stamps from {country}"
    data = {}
    lines = Path(f'stamps{country}.txt').read_text().splitlines()
    page = None
    section = None
    for l in lines:
        if l.startswith("="):
            section = l.strip("=")
        elif l.startswith("*"):
            page = l.strip("*")
        elif section is not None and l.startswith("http"):
            data.setdefault(page, {}).setdefault(section, []).append(l)

    for i, (page, d) in enumerate(data.items(), 1):
        imgs = []
        labels = []
        for k, urls in d.items():
            img = Image.from_row(
                [Image.from_url_with_cache(url).resize_fixed_aspect(height=220) for url in urls]
            )
            imgs.append(img)
            labels.append(Image.from_text(k.rstrip("*").upper(), sans(28, bold=True), max_width=200))

        array = Image.from_array(list(zip(labels, imgs)), xalign=0, padding=5)
        img = Image.from_column([
            Image.from_column([
                Image.from_text(title.upper(), sans(32, bold=True)),
                Image.from_text(page.upper(), sans(64, bold=True)),
            ], padding=5),
            array
        ], padding=20, bg="white")
        img.convert("RGB").save(f"output/stamps{country}{i}.jpg")
