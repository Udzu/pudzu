from pudzu.charts import *

FILES = {
 "israstine": "Some flags for a united Israel-Palestine",
 "saudi": "Some flags in the style of Saudi Arabia",
 "canada": "Some flags in the style of Canada",
}

for file, label in FILES.items():

    df = pd.read_csv(f"datasets/reddit{file}.csv")

    FONT = sans
    fg, bg="black", "#EEEEEE"
    default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/No_flag.svg/1024px-No_flag.svg.png"

    def process(d):
        if not d: return None
        name = get_non(d, 'name', '').replace(r'\n','\n').replace(', ','\n')
        description = "by /u/{}".format(get_non(d, 'author')) if get_non(d, 'author') else " "
        flag = Image.from_url_with_cache(get_non(d, 'url', default_img)).to_rgba()
        flag = flag.resize_fixed_aspect(height=248) if flag.width / flag.height < 1.3 else flag.resize((398,248))
        def t(a): return int(not any(alpha==0 for _,_,_,alpha in a))
        a = np.array(flag); padding = (t(a[:,0]), t(a[0]), t(a[:,-1]), t(a[-1]))
        flag= flag.pad(padding, "grey")
        return Image.from_column([
          Image.from_text(name, FONT(28, bold=True), align="center", beard_line=True, fg=fg, line_spacing=2) if name else Image.EMPTY_IMAGE,
          Image.from_text(description, FONT(24, italics=True), fg=fg, beard_line=True),
          flag
          ], padding=2, bg=bg, equal_widths=True)

    title = Image.from_text(label.upper(), FONT(68, bold=True), fg=fg, bg=bg, align="center").pad(30, bg).pad((0,0,0,10), bg)

    array = list(generate_batches([dict(r) for _,r in df.iterrows()], 4))
    data = pd.DataFrame(array)
    grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=0).pad((10,0),bg)

    print("Credits: {}".format(", ".join(f"/u/{a}" for a in df.author)))

    img = Image.from_column([title, grid], bg=bg)
    img.save(f"output/flags{file}.png")

