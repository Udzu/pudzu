from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import json

# Some adhoc utilities for generating d3 datamaps (including one for converting them to raster map templates)

atlas = pd.read_csv("../dataviz/datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')

def codify_countries(datamap):
    extras = { 
        "KSV": "kosovo", "CYP": "northern_cyprus", "SOM": "somaliland", 
        "DNK": ("GRL", "FRO"), "NLD": "SXM", "FIN": "ALA", "NOR": "SJM",
        "FRA": ("GUF", "GLP", "MTQ", "PYF", "ATF", "MAF", "NCL", "REU"),
        "GBR": ("GIB", "FLK", "SGS"),
        "USA": ("PRI", "GUM", "ASM")
    }
    codified = keymap(lambda c: atlas.code.get(c, c), datamap)
    for old, news in extras.items():
        for new in make_iterable(news):
            if old in codified and new not in codified:
                codified[new] = codified[old]
    return codified

def dict_from_vals(**kwargs):
    return { v : k for k, vs in kwargs.items() for v in vs }
    
def generate_datamap(name, datamap, palette={}, width=2500, height=1000,
                     map_path="libraries/datamaps.world.hires.js", codifier=codify_countries,
                     geography={"borderWidth": 0.8}, default_fill="#BBBBBB", crisp_edges=False):
    """Generate a D3 datamap html file with a button for saving as a PNG."""
    TEMPLATE = r"""<!DOCTYPE html>
<html>
<body>
<script src="../libraries/d3.min.js"></script>
<script src="../libraries/saveSvgAsPng.js"></script>
<script src="../libraries/topojson.min.js"></script>
<script src="../{{map_path}}"></script>
<button onclick='saveSvgAsPng(document.getElementsByTagName("svg")[0], "{{name}}.png")'>Save image...</button>
<div id="container"/>
<script>
    var map = new Datamap({
      element: document.getElementById('container'),
      width: {{width}},
      height: {{height}},
      geographyConfig: {{geography_config}},
      fills: {{fills}},
      data: {{data}}
    });
    {{crispy}}
</script>
</body>"""
    palette = merge({ "defaultFill": default_fill }, palette)
    def datavalmap(k):
        if k not in palette:
            k = RGBA(k).to_hex()
            palette[k] = k
        return {"fillKey": k}
    codifier = codifier or identity
    data = indent_all_but_first(json.dumps(codifier(valmap(datavalmap, datamap)), indent=4), 6)
    fills = indent_all_but_first(json.dumps(valmap(lambda p: RGBA(p).to_hex(), palette), indent=4), 6)
    geography_config = indent_all_but_first(json.dumps(geography, indent=4), 6)
    crispy = 'document.getElementsByTagName("svg")[0].setAttribute("shape-rendering", "crispEdges ")' * crisp_edges
    html = substitute(TEMPLATE, **locals())
    with open("temp/"+name+".html", "w", encoding="utf-8") as f:
        f.write("\n".join(l for l in html.split("\n") if l.strip()))

def generate_map_chart(name, regions, width=2500, height=1000,
                       map_path="libraries/datamaps.world.hires.js", codifier=codify_countries):
    def colfn(i): return RGBA(255, i % 200, i // 200)
    sea, background, border = RGBA("#FFFFFF"), RGBA("#BBBBBB"), RGBA("#EEEEEE")
    data = { k : colfn(i) for i, k in enumerate(regions) }
    generate_datamap(name, data, width=width, height=height, map_path=map_path, codifier=codifier,
                     geography={"borderWidth": 1, "borderColor": border.to_hex()}, crisp_edges=True)
    data = merge( { "Sea": sea, "Unknown": background, "Borders": border }, data )
    labels = [{ 'color': "|".join(map(str,c[:3])), 'name': k, 'label_align': "" } for k,c in data.items()]
    pd.DataFrame(labels).to_csv("temp/"+name_csv_path(name), index=False, encoding="utf-8")
    
