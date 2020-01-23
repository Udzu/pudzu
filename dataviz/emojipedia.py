from pudzu.tureen import *
from pudzu.charts import *
requests_cache = optional_import("requests_cache")

CACHE_PATH = "cache"
CACHE = requests if CACHE_PATH is None else requests_cache.CachedSession(CACHE_PATH)
HEADERS = {'User-Agent': 'Mozilla/5.0'}
BASE_URL = "https://emojipedia.org/"
SETS = {
    "Apple iOS 13.2": "Apple",
    "Google Android 10.0": "Google", 
    "Twitter Twemoji 12.1.4": "Twitter",
    "Samsung One UI 1.5": "Samsung",
    "Facebook 4.0": "Facebook",
    "Microsoft Windows 10 May 2019 Update": "Microsoft",
    "WhatsApp 2.19.244": "WhatsApp",
}

GENDER_URLS = (
"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/samsung/220/neuter_26b2.png",
"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/samsung/220/female-sign_2640.png",
"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/samsung/220/male-sign_2642.png",
#"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/whatsapp/224/male-with-stroke-and-male-and-female-sign_26a7-fe0f.png",
#"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/whatsapp/224/female-sign_2640.png",
#"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/whatsapp/224/male-sign_2642.png",
)
GN, F, M = [Image.from_url_with_cache(u).to_rgba().resize_fixed_aspect(width=50+10*(i==0)).pad(5*(i!=0),"white").pad((2,0),"white") for i,u in enumerate(GENDER_URLS)]

def load_emoji(path):
    response = CACHE.get(BASE_URL + path, headers=HEADERS)
    soup = bs4.BeautifulSoup(response.content, "lxml")
    images = soup.find_all(width=range(100,121))
    return {re.search(".* on (.*)", i.attrs["alt"]).group(1): i.attrs["src"] for i in images}

def extract_people():
    professions = []
    categories = ["people/", "activity/"]
    for category in categories:
        response = CACHE.get(BASE_URL + category, headers=HEADERS)
        soup = bs4.BeautifulSoup(response.content, "lxml")
        for w in soup.find_all(text=re.compile("Woman|Women")):
            s = str(w)
            # if "Blond Hair" in s: continue
            m = soup.find(text=s.replace("Woman", "Man").replace("Women", "Men"))
            p = soup.find(text=s.replace("Woman", "Person").replace("Women", "People")) or soup.find(text=re.sub("(Woman|Women) *","",s))
            if all((p, w, m)): professions.append((p, w, m))
    professions = sorted(professions, key=lambda pwm: (-("Person" in pwm[0]), pwm[0].replace(":"," ")))
    return { str(pwm[0]).strip(): tuple(str(p.parent.attrs['href']) for p in pwm) for pwm in professions }

def load_icon(url):
    return Image.from_url_with_cache(url).to_rgba().resize_fixed_aspect(width=60)
    
def make_grid():
    labels = [Image.from_text("Average representation".upper(), sans(24, bold=True), padding=(0,5))] + \
             [Image.from_text(set.upper(), sans(24, bold=True), padding=(0,7)) for set in SETS.values()]
    grid = [labels]
    for name, pwm in extract_people().items():
        row = []
        emojis = [load_emoji(p) for p in pwm]
        genders = []
        for type in SETS:
            urls = [e[type] for e in emojis]
            icons = [with_retries(load_icon, max_retries=100, interval=10)(url) for url in urls]
            gender = F if icons[0] == icons[1] else M if icons[0] == icons[2] else GN
            # exceptions
            if "Samsung" in type and "Raising Hand" in name: gender = F
            elif "Microsoft" in type and ("Police" in name or "Detective" in name): gender = M
            genders.append(gender)
            icons.insert(0, gender)
            row.append(Image.from_row(icons, padding=2))
        gender = M if genders.count(M) > genders.count(F) else F if genders.count(M) < genders.count(F) else GN
        label = Image.from_row([gender, Image.from_text(name.upper(), sans(24, bold=True))], padding=2)
        row.insert(0, label)
        grid.append(row)
    
    return Image.from_array(grid, bg="white", padding=(20,5), xalign=[0]+[0.5]*len(SETS))

grid = make_grid()
TITLE = "Gender representations of gender-neutral people emoji"
SUBTITLE = "based on the latest emoji fonts from Apple, Google, Twitter, Samsung, Facebook, Microsoft and WhatsApp*"
FOOTER = "*November 2019 fonts: Apple iOS 13.2, Google Android 10.0, Twitter Twemoji 12.1.4, Samsung One UI 1.5, Facebook 4.0, Microsoft Windows 10 May 2019, WhatsApp 2.19.244"
title = Image.from_text_justified(TITLE.upper(), grid.width-50, 80, partial(sans, bold=True), bg="white", padding=(0,20,0,10))
subtitle = Image.from_text_justified(SUBTITLE, grid.width-50, 80, sans, bg="white", padding=(0,0,0,20))
footer  = Image.from_text_justified(FOOTER, grid.width-150, 80, partial(sans, italics=True), bg="white", padding=(0,20,0,20))

img = Image.from_column([title, subtitle, grid, footer], bg="white")
img.place(Image.from_text("/u/Udzu", sans(12), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=5, copy=False)

img.convert("RGB").save("output/emojigender.jpg")


