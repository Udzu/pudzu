import sys
sys.path.append('..')
from utils import *
from pillar import *
from bamboo import *
import json

def generate_datamap(name, data, palette,
                     width=2500, height=1000, border=0.8, defaultFill="#BBBBBB",
                     map="libraries/datamaps.world.hires.min.js"):
    """Generate a D3 datamap html file."""
    TEMPLATE = r"""<!DOCTYPE html>
<html>
<body>
<script src="libraries/d3.min.js"></script>
<script src="libraries/saveSvgAsPng.js"></script>
<script src="libraries/topojson.min.js"></script>
<script src="{{map}}"></script>
<div id="container"/>
<script>
    var map = new Datamap({
      element: document.getElementById('container'),
      width: {{width}},
      height: {{height}},
      geographyConfig: { borderWidth: {{border}} },
      fills: {{fills}},
      data: {{datamap}}
    });
    saveSvgAsPng(document.getElementsByTagName("svg")[0], "{{name}}.png");
</script>
</body>"""
    if "defaultFill" not in palette: palette["defaultFill"] = defaultFill
    fills = indent_all_but_first(json.dumps(valmap(lambda p: RGBA(p).to_hex(), palette), indent=4), 6)
    datamap = indent_all_but_first(json.dumps(valmap(lambda p: {"fillKey": p}, data), indent=4), 6)
    html = substitute(TEMPLATE, **locals())
    with open("temp/"+name+".html", "w", encoding="utf-8") as f:
        f.write(html)

# useful utilities
atlas = pd.read_csv("../dataviz/datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')

def codify_countries(**kwargs):
    data = {}
    for k, v in kwargs.items():
        for c in v:
            data[atlas.code[c]] = k
    return data

