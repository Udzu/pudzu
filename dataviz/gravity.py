import sys
sys.path.append('..')

import hashlib
import matplotlib.pyplot as plt
from scipy import signal
from functools import wraps
from pillar import *
from charts import *

logger.setLevel(logging.INFO)

# naive gravity calculation that's fast enough because numpy

np.seterr(divide='ignore', invalid='ignore')

def force_components(rows, cols, linear=False):
    xs = np.fromfunction(lambda i,j: (rows-1-i), (2*rows-1, 2*cols-1))
    ys = np.fromfunction(lambda i,j: (cols-1-j), (2*rows-1, 2*cols-1))
    n3 = (xs**2 + ys**2) ** (1 if linear else 3/2)
    return np.nan_to_num(xs / n3), np.nan_to_num(ys / n3)

def gravity_components(arr, linear=False):
    isqxs, isqys = force_components(*arr.shape, linear=linear)
    xs = np.rot90(signal.convolve2d(np.rot90(arr, 2), isqxs, 'same'), 2)
    ys = np.rot90(signal.convolve2d(np.rot90(arr, 2), isqys, 'same'), 2)
    return xs, ys

def gravity_magnitude(arr, normalised=True, linear=False, cached=True):
    components = gravity_components(arr, linear=linear)
    mag = (components[0] ** 2 + components[1] ** 2) ** 0.5
    return mag / mag.max() if normalised else mag
    
@wraps(gravity_magnitude)
def gravity_cached(arr, **kwargs):
    if isinstance(arr, Image.Image):
        arr = mask_to_array(arr)
    h = hashlib.sha1(arr.data.tobytes()).hexdigest()
    p = "cache/gravity_{}{}.npy".format(h, "".join("_{}_{}".format(k,v) for k,v in kwargs.items()))
    if os.path.exists(p):
        logger.log(logging.INFO, "Loading cached gravity array")
        mag = np.load(p)
    else:
        mag = gravity_magnitude(arr, **kwargs)
        logger.log(logging.INFO, "Saving cached gravity array")
        np.save(p, mag)
    return mag

# some adhoc visualisation helpers

def mask_to_array(img):
    return np.array(img.as_mask()) / 255
    
def mask_to_img(img, fg="grey", bg="white"):
    return MaskUnion(..., fg, bg, masks=img)
    
def shapeplot(shape, min=None, max=None):
    shape = mask_to_img(shape)
    shape = shape.place(MaskUnion(..., "green", masks=make_iterable(min))).place(MaskUnion(..., "red", masks=make_iterable(max)))
    return shape

def heatmap(array, cmap=plt.get_cmap("hot")):
    return Image.fromarray(cmap(array, bytes=True))
   
def minmax(array, low=2, high=10, lowcol="green", midcol="white", highcol="red"):
    # for figuring out low and high points; not pretty enough to actually use
    intervals = [low/2, low/2, 100-low-high, high/2, high/2]
    cmap = GradientColormap(lowcol, lowcol, midcol, midcol, highcol, highcol, intervals=intervals)
    return heatmap(array, cmap)
    
def minblend(shape, p=0.25, **kwargs):
    return ignoring_extra_args(shapeplot)(shape, **kwargs).blend(
        ignoring_extra_args(minmax)(ignoring_extra_args(gravity_cached)(shape, **kwargs), **kwargs), p=p)

def linechart(data, width, height, color, cache="cache/gravity_plot.png"):
    fig = plt.figure(figsize=(width/100,height/100), dpi=100)
    ax = fig.add_axes((0,0,1,1))
    ax.set_axis_off()
    ax.plot(data, color)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.ylim(0,1)
    plt.savefig(cache, dpi='figure', transparent=True)
    plt.close()
    return Image.open(cache)

def scanlines(array, directions):
    h, w = array.shape
    x, y = round(w / 2), round(h / 2)
    img = Rectangle((w,h//2), "white")
    if "d" in directions:
        diag, omit = np.diag(array, (w-h)//2), 1 - 0.5**0.5
        diag = diag[floor(len(diag)*omit/2):ceil(len(diag)*(1-omit/2))]
        img = img.place(linechart(diag, w, w//2, "#000080"))
    if "v" in directions: img = img.place(linechart(array[:,x], h, w//2, "#008000"))
    if "h" in directions: img = img.place(linechart(array[y], w, h//2, "#800000"))
    return img

def odd(n): return round(n) + (round(n)-1)%2

# sizes

FONT = arial
WIDTH = 120
PADDING = 20
BIGTEXT_SIZE = 28
TEXT_SIZE = 18
DOT_SIZE = 8
LINE_SIZE = 3
LEGEND_WIDTH = 900
TITLE_SIZE = 92

# shape config (max and min shapes are approximations based on minmax above but should be good enough for illustrative purposes)

SHAPES = CaseInsensitiveDict(base_factory=OrderedDict)

class ShapeOpts(namedtuple('ShapeOpts', 'name,shape,min,max,min_linear,max_linear,scanlines,description')):
    def __new__(cls, name, shape, min=None, max=None, min_linear=..., max_linear=..., scanlines="h", description="Some **interesting** point?"):
        return super().__new__(cls, name, shape, min, max, min if min_linear == ... else min_linear, max if max_linear == ... else max_linear, scanlines, description)
        
# actual shapes (the way I've ended up doing max and min shapes is really stupid for some reason, sorry)

base = Image.new("RGBA", (round(WIDTH*1.5), round(WIDTH*1.5)))
pw = odd(WIDTH*2/3)
ppw = odd(pw*3/4)
dot = Ellipse(DOT_SIZE)

circle = base.place(Ellipse(pw))
circle_max = MaskIntersection(..., masks=(Ellipse(pw+LINE_SIZE), Ellipse(pw-LINE_SIZE, invert=True)), include_missing=True)
circle_description = "With inverse force, gravity outside the circle behaves as if all the circle's mass were concentrated at the center, while inside it decreases linearly: just like constant density spheres in 3D. With inverse-square force, the nearer parts of the shell apply more force than the farther parts, resulting in greater attraction towards the surface."
SHAPES["circle"] = ShapeOpts("circle", circle, dot, circle_max, description=circle_description)

ellipse_height = odd(pw / 2)
ellipse = base.place(Ellipse((pw, ellipse_height)))
ellipse_max = Rectangle(pw,0).pin(dot,(pw//2+1,pw//2+ellipse_height//2+1)).pin(dot,(pw//2+1,pw//2-ellipse_height//2+1))
ellipse_description = "Standing on the pole of the ellipse places you closer to the center of mass (the //monopole// contribution), while standing on the equator directs more of the force downwards (the //quadrupole// contribution). The former wins out, though the latter cancels out most of the difference."
SHAPES["ellipse"] = ShapeOpts("ellipse", ellipse, dot, ellipse_max, scanlines="vh", description=ellipse_description)

core = base.place(Ellipse(pw, (0,0,0,100))).place(Ellipse(ppw))
core_max = MaskIntersection(..., masks=(Ellipse(ppw+LINE_SIZE), Ellipse(ppw-LINE_SIZE, invert=True)), include_missing=True)
core_description = "A dense enough core (like the Earth's) can result in gravity increasing as you approach it. With inverse force this increase is linear."
SHAPES["core"] = ShapeOpts("dense core", core, dot, core_max, description=core_description)

hollow = base.place(MaskIntersection(..., masks=(Ellipse(pw), Ellipse(ppw, invert=True)), include_missing=True))
hollow_min = MaskIntersection(..., masks=(Ellipse(round(pw*0.85)+LINE_SIZE), Ellipse(round(pw*0.85)-LINE_SIZE, invert=True)), include_missing=True).place(dot)
hollow_min_linear = Ellipse(ppw)
hollow_description = "With inverse force, a hollow shell applies //zero// net force to objects inside: an unintuitive result of the Shell Theorem. With inverse-square force, the nearer parts of the shell attract more."
SHAPES["hollow"] = ShapeOpts("hollow shell", hollow, hollow_min, circle_max, hollow_min_linear, description=hollow_description)

mountain = base.place(Ellipse(pw).pin(Triangle(odd(pw/3)), (pw//2+1, pw//20), align=(0.5,1)))
mountain_min = dot.pad((0,odd(pw/4),0,0), 0)
mountain_max = Rectangle((odd(pw*0.8),odd(pw*0.5)),0).pad((0,odd(pw/4),0,0), 0).pin(dot,(odd(pw*0.8),odd(pw/4))).pin(dot,(0,odd(pw/4)))
mountain_max_linear = Rectangle((odd(pw*0.55),odd(pw*0.95)),0).pad((0,odd(pw/4),0,0), 0).pin(dot,(odd(pw*0.55),odd(pw*0.95+pw/4))).pin(dot,(0,odd(pw*0.95+pw/4)))
mountain_description = "Similar to the ellipse scenario, the gravitational pull at the base of a mountain is greater than at its peak. The point of maximum attraction depends on the level of force decay."
SHAPES["mountain"] = ShapeOpts("mountain", mountain, mountain_min, mountain_max, ..., mountain_max_linear, scanlines="v", description=mountain_description)

square = base.place(Rectangle(pw))
offsets = Padding(0)
square_max = Rectangle(pw,0).pin(dot,(pw//2+1,0),offsets=offsets).pin(dot,(pw//2+1,pw),offsets=offsets).pin(dot,(0,pw//2+1),offsets=offsets).pin(dot,(pw,pw//2+1),offsets=offsets)
square_description = "A square is like four mountains at right angles to each other."
SHAPES["square"] = ShapeOpts("square", square, dot, square_max, scanlines="dh", description=square_description)

two = Image.from_row([circle, circle])
two_max = Rectangle((two.width,pw),0).pin(dot,((base.width-pw)//2+1,pw//2+1)).pin(dot,(two.width-((base.width-pw)//2+1),pw//2+1))
two_min = Rectangle((two.width,pw),0).pin(dot,(base.width,pw//2+1)).pin(dot,(base.width//2+1+pw//40,pw//2+1)).pin(dot,(two.width-(base.width//2+1+pw//40),pw//2+1))
two_min_linear = Rectangle((two.width,pw),0).pin(dot,(base.width,pw//2+1)).pin(dot,(base.width//2+1+pw//20,pw//2+1)).pin(dot,(two.width-(base.width//2+1+pw//20),pw//2+1))
two_description = "Two circles a fixed distance apart apply zero net force at three points: two points inside the circles, and one at the midpoint. In 3D the Lagrange points are typically more relevant as they take centrifugal force into account; however, stable orbits are not possible with inverse force, a consequence of Bertrand's Theorem."
SHAPES["two"] = ShapeOpts("two circles", two, two_min, two_max, two_min_linear, description=two_description)

moon = Image.from_row([circle, base.place(Ellipse(odd(pw/2)))])
moon_max = Rectangle((two.width,pw),0).pin(dot,((base.width-pw)//2+1,pw//2+1))
moon_min = Rectangle((two.width,pw),0).pin(dot,(base.width+int(pw*0.4),pw//2+1)).pin(dot,(base.width//2+1+pw//160,pw//2+1)).pin(dot,(two.width-(base.width//2+1+pw//80),pw//2+1))
moon_min_linear = Rectangle((two.width,pw),0).pin(dot,(base.width+int(pw*0.6),pw//2+1)).pin(dot,(base.width//2+1+pw//40,pw//2+1)).pin(dot,(two.width-(base.width//2+1+pw//20),pw//2+1))
moon_description = "If one circle is significantly larger than the other, the point of zero net force moves closer to the smaller one. This serves as a plot point in Jules Verne's (scientifically inaccurate) novel //From the Earth to the Moon//."
SHAPES["moon"] = ShapeOpts("earth and moon", moon, moon_min, moon_max, moon_min_linear, description=moon_description)

reddit = base.convert("L").place(Image.open("icons/reddit.png").convert("L").resize_fixed_aspect(width=odd(WIDTH)))
reddit_min = Rectangle(WIDTH,0).pin(dot,(WIDTH//2+1,int(WIDTH*0.65)))
reddit_min_linear = Rectangle(WIDTH,0).pin(dot,(WIDTH//2+1,int(WIDTH*0.45)))
reddit_max = Rectangle(WIDTH,0).pin(dot,(int(WIDTH*0.26),int(WIDTH*0.49)))
reddit_max_linear =  Rectangle(WIDTH,0).pin(dot,(int(WIDTH*0.38),int(WIDTH*0.25)))
reddit_description = "In case you ever find yourself stranded on a 2D Snoo-shaped asteroid and are worried about floating into space..."
SHAPES["reddit"] = ShapeOpts("snoo", reddit, reddit_min, reddit_max, reddit_min_linear, reddit_max_linear, scanlines="hv", description=reddit_description)  #TODO

# put it all together

def plot_shape(shape): 
    logger.log(logging.INFO, "Generating {} [inverse square]".format(shape.name))
    mag = gravity_cached(shape.shape, linear=False)
    logger.log(logging.INFO, "Generating {} [inverse linear]".format(shape.name))
    mag_linear = gravity_cached(shape.shape, linear=True)
    h, w = mag.shape
    y = round(h / 2)
    grid = Image.from_array([
        [shapeplot(shape.shape, shape.min, shape.max),
         shapeplot(shape.shape, shape.min_linear, shape.max_linear)][::-1],
        [heatmap(mag),
         heatmap(mag_linear)][::-1],
        [scanlines(mag, shape.scanlines).pad((0,PADDING),"white"),
         scanlines(mag_linear, shape.scanlines).pad((0,PADDING),"white")][::-1]
        ], padding=0, bg="white")
    markup = Image.from_markup(shape.description, partial(FONT, TEXT_SIZE), max_width=w*2, hyphenator=language_hyphenator())
    markup = Rectangle((w*2, markup.height), "white").place(markup, align=0)
    return Image.from_column([
        Image.from_text(shape.name.upper(), FONT(BIGTEXT_SIZE, bold=True)),
        grid,
        markup
        ], padding=0, bg="white")

rows = tmap_leafs(lambda shape: plot_shape(SHAPES[shape]), generate_batches(SHAPES, 6))
padded = tmap_leafs(lambda img: img.pad((5,0), "white") if img.width > base.width * 2 else img, rows)
chart = Image.from_column([Image.from_row(row, yalign=0, padding=5, bg="white") for row in padded], bg="white", xalign=0, padding=10)
    
# legend

def shape_box(alpha=0,min=None,max=None):
    return shapeplot(Rectangle(40,(0,0,0,alpha)), min=min and Rectangle(40,0).place(min), max=max and Rectangle(40,0).place(max))
def line_box(color):
    return Rectangle(40, 0).place(Rectangle((40,3), color))

introduction = generate_legend([], [], header="Why is there two of everything?".upper(), padding=5, footer="There are two possible ways to extend gravity to two dimensions. The first is to keep the inverse square law, which emulates a 3D mass squashed into the plane. The second is to instead use a linear inverse law, which corresponds to the geometric dilution of point-source radiation in 2D. The first approach (right) behaves more like gravity in 3D but is artificial; the second (left) displays all the expected symmetries but looks different in terms of strength and orbits.", border=False, max_width=LEGEND_WIDTH, fonts=partial(FONT, BIGTEXT_SIZE))
shape_legend = generate_legend([shape_box(255), shape_box(100), shape_box(0), shape_box(min=dot), shape_box(max=dot)],["high density solid", "low density solid", "empty space", "minimum gravity", "maximum gravity"], padding=5, header="SHAPES AND EXTREMA", border=False, fonts=partial(FONT, BIGTEXT_SIZE))
heatmap_legend = generate_legend([Image.from_gradient(plt.get_cmap("hot"), (40, 180), direction=(0,-1)).add_grid((1,8))], [["maximum gravity", "50% gravity", "minimum gravity"]], header="GRAVITY HEATMAPS", padding=5, border=False, fonts=partial(FONT, BIGTEXT_SIZE))
graph_legend = generate_legend([line_box("#800000"), line_box("#008000"), line_box("#000080")], ["horizontal intersection", "vertical intersection", "diagonal intersection"], header="INTERSECTION PLOTS", padding=5, border=False, fonts=partial(FONT, BIGTEXT_SIZE))
legend=Image.from_row([introduction, shape_legend, heatmap_legend, graph_legend], bg="white", padding=(10,0), yalign=0).pad(2, "black")

# title

title = Image.from_text("Visualizing gravity in 2 Dimensions".upper(), FONT(TITLE_SIZE, bold=True))
img = Image.from_column([title, legend, chart], bg="white", padding=BIGTEXT_SIZE)
img = img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10)
img.convert("RGB").save("output/gravity.jpg")

# unused quadtree implementation from before I figured out how to use numpy properly

class QuadTree(object):

    def __new__(cls, array, x=0, y=0):
        """Generate hierarchical QuadTree object, or None if the array is zero."""
        w,h = array.shape[0], array.shape[1]
        assert w == h, "QuadTree input array must be a square"
        if array.size == 1: # leaf node
            if array[0,0] == 0: return None
            children = None
        else: # internal node
            assert w % 2 == 0, "QuadTree input array size be a power of two"
            children = [QuadTree(array[i:i+w//2,j:j+h//2], x+i, y+j) for (i,j) in itertools.product([0,w//2],[0,h//2])]
            if not any(children): return None
        self = super(QuadTree, cls).__new__(cls)
        self.children = children
        return self

    def __init__(self, array, x=0, y=0):
        """Initialize a QuadTree object."""
        self.width = array.shape[0]
        if array.size == 1:
            self.mass = array[0,0]
            self.com = np.array([x,y])
        else:
            self.mass = sum(c.mass for c in self.children if c is not None)
            self.com = sum(c.com * c.mass for c in self.children if c is not None) / self.mass
            
    def __repr__(self):
        return "<QuadTree mass={} com={}>".format(self.mass, self.com)

def qtree_gravity(qtree, loc, theta):
    v = loc - qtree.com
    d = np.linalg.norm(v)
    if qtree.width == 1 or d > 0 and qtree.width / d < theta:
        return 0 if d == 0 else v * qtree.mass / (d**3)
    return sum(qtree_gravity(c, loc, theta) for c in qtree.children if c is not None)
   
def qtree_gravity_array(arr, theta=0.8):
    padded_size = 1 << (max(arr.shape)-1).bit_length()
    padded = np.pad(arr, [(0, padded_size - arr.shape[0]), (0, padded_size - arr.shape[1])], mode='constant')
    qtree = QuadTree(padded)
    def calculate(i, j): return qtree_gravity(qtree, np.array([i, j]), theta)
    return np.fromfunction(np.frompyfunc(calculate, 2, 1), arr.shape, dtype=int)
