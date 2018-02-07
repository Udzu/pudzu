import sys
sys.path.append('..')
import pandas as pd
from pillar import *

def generate_photoset(path, size=(600,200)):
    df = pd.read_csv(path)
    dirname = "output/{}".format(os.path.splitext(os.path.basename(path))[0])
    os.makedirs(dirname, exist_ok=True)
    for i,(_,d) in enumerate(df.iterrows(), 1):
        img = Image.from_url_with_cache(d.image)
        img = img.cropped_resize(size, align=get_non(d, 'align', (0.5,0.25)), upsize=False, pad_bg="white", pad_align=(0,0.5))
        img.convert("RGB").save("{}/{}. {}.jpg".format(dirname, i, d.label))
