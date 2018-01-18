import sys
import matplotlib.pyplot as plt
sys.path.append('..')
from pillar import *
from charts import *
from scipy import signal

# slow gravity calculation that's fast enough because numpy

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

def gravity_magnitude(arr, normalised=True, linear=False):
    if isinstance(arr, Image.Image): arr = mask_to_array(arr)
    components = gravity_components(arr, linear=linear)
    mag = (components[0] ** 2 + components[1] ** 2) ** 0.5
    return mag / mag.max() if normalised else mag

# some visualisation helpers

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
        ignoring_extra_args(minmax)(ignoring_extra_args(gravity_magnitude)(shape, **kwargs), **kwargs), p=p)

def linechart(data, width, height, color, cache="cache/gravity_plot.png"):
    if height is None: height = width
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

# shape config (max and min shapes are approximations based on minmax above but should be good enough for illustrative purposes)

WIDTH = 60 # TODO
TITLE_SIZE = 16
TEXT_SIZE = 12
PADDING = 20
SHAPES = CaseInsensitiveDict(base_factory=OrderedDict)

class ShapeOpts(namedtuple('ShapeOpts', 'name,shape,min,max,min_linear,max_linear,scanlines,description')):
    def __new__(cls, name, shape, min=None, max=None, min_linear=..., max_linear=..., scanlines="h", description="Some **interesting** point?"):
        return super().__new__(cls, name, shape, min, max, min if min_linear == ... else min_linear, max if max_linear == ... else max_linear, scanlines, description)
        
# actual shapes

base = Image.new("RGBA", (round(WIDTH*1.5), round(WIDTH*1.5)))
pwidth = odd(WIDTH*2/3)
ppwdith = odd(pwidth*3/4)
dot = Ellipse(5)

circle = base.place(Ellipse(pwidth))
circle_max = MaskIntersection(..., masks=(Ellipse(pwidth+2), Ellipse(pwidth-2, invert=True)), include_missing=True)
circle_description = "With inverse force, gravity //outside// the circle behaves as if all the circle's mass were concentrated in the centre, while //inside// it decreases linearly (just like constant density spheres in the real world). With inverse-square force, the nearer parts of the shell apply more force than the further parts, resulting in greater attraction towards the surface."
SHAPES["circle"] = ShapeOpts("circle", circle, dot, circle_max, description=circle_description)

ellipse = base.place(Ellipse((pwidth, odd(pwidth / 2))))
ellipse_description = "?" # TODO
SHAPES["ellipse"] = ShapeOpts("ellipse", ellipse, dot, scanlines="vh", description=ellipse_description)

core = base.place(Ellipse(pwidth, (0,0,0,100))).place(Ellipse(ppwdith))
core_max = MaskIntersection(..., masks=(Ellipse(ppwdith+2), Ellipse(ppwdith-2, invert=True)), include_missing=True)
core_description = "A dense enough core (like the Earth's) can result in gravity increasing closer to the second. With inverse force this increase is linear."
SHAPES["core"] = ShapeOpts("dense core", core, dot, core_max, description=core_description)

hollow = base.place(MaskIntersection(..., masks=(Ellipse(pwidth), Ellipse(ppwdith, invert=True)), include_missing=True))
hollow_min = MaskIntersection(..., masks=(Ellipse(round(pwidth*0.85)+2), Ellipse(round(pwidth*0.85)-2, invert=True)), include_missing=True).place(dot)
hollow_min_linear = Ellipse(ppwdith)
hollow_description = "With inverse force, a hollow shell applies //zero// net force to objects inside: an unintuitive result of the Shell Theorem. With inverse-square force the nearer part of the shell do attract more."
SHAPES["hollow"] = ShapeOpts("hollow shell", hollow, hollow_min, circle_max, hollow_min_linear, description=hollow_description)

mountain = base.place(Ellipse(pwidth).pin(Triangle(odd(pwidth/3)), (pwidth//2+1, pwidth//20), align=(0.5,1)))
mountain_min = dot.pad((0,odd(pwidth/4),0,0), 0)
mountain_max = Rectangle((odd(pwidth*0.8),odd(pwidth*0.5)),(0,0,0,0)).pad((0,odd(pwidth/4),0,0), 0).pin(dot,(odd(pwidth*0.8),odd(pwidth/4))).pin(dot,(0,odd(pwidth/4)))
mountain_max_linear = Rectangle((odd(pwidth*0.55),odd(pwidth*0.95)),(0,0,0,0)).pad((0,odd(pwidth/4),0,0), 0).pin(dot,(odd(pwidth*0.55),odd(pwidth*0.95+pwidth/4))).pin(dot,(0,odd(pwidth*0.95+pwidth/4)))
mountain_description = "Not enough to offset shell effect."
SHAPES["mountain"] = ShapeOpts("mountain", mountain, mountain_min, mountain_max, ..., mountain_max_linear, scanlines="v", description=mountain_description)

square = base.place(Rectangle(pwidth))
offsets = Padding(0)
square_max = Rectangle(pwidth,(0,0,0,0)).pin(dot,(pwidth//2+1,0),offsets=offsets).pin(dot,(pwidth//2+1,pwidth),offsets=offsets).pin(dot,(0,pwidth//2+1),offsets=offsets).pin(dot,(pwidth,pwidth//2+1),offsets=offsets)
square_description = "Like four mountains"
SHAPES["square"] = ShapeOpts("square", square, dot, square_max, scanlines="dh", description=square_description)

two = Image.from_row([circle, circle])
two_description = "?" #TODO
SHAPES["two"] = ShapeOpts("two circles", two, description=two_description)

moon = Image.from_row([circle, base.place(Ellipse(odd(pwidth/2)))])
moon_description = "?" #TODO
SHAPES["moon"] = ShapeOpts("moon", moon, description=moon_description)

reddit = base.convert("L").place(Image.open("icons/reddit.png").convert("L").resize_fixed_aspect(width=odd(WIDTH)))
reddit_description = "?" #TODO
SHAPES["reddit"] = ShapeOpts("snoo", reddit, scanlines="hv", description=reddit_description)

# put it all together

def plot_shape(shape): 
    mag = gravity_magnitude(shape.shape, linear=False)
    mag_linear = gravity_magnitude(shape.shape, linear=True)
    w, h = mag.shape
    y = round(h / 2)
    grid = Image.from_array([
        [shapeplot(shape.shape, shape.min, shape.max),
         shapeplot(shape.shape, shape.min_linear, shape.max_linear)][::-1],
        [heatmap(mag),
         heatmap(mag_linear)][::-1],
        [scanlines(mag, shape.scanlines).pad((0,PADDING),"white"),
         scanlines(mag_linear, shape.scanlines).pad((0,PADDING),"white")][::-1]
        ], padding=0, bg="white")
    markup = Image.from_markup(shape.description, partial(arial, TEXT_SIZE), max_width=w*2, hyphenator=language_hyphenator())
    markup = Rectangle((w*2, markup.height), "white").place(markup, align=0)
    return Image.from_column([
        Image.from_text(shape.name.upper(), arial(TITLE_SIZE, bold=True)),
        grid,
        markup
        ], padding=0, bg="white")

# rows = tmap_leafs(lambda shape: plot_shape(SHAPES[shape]), generate_batches(SHAPES, 6))
# padded = tmap_leafs(lambda img: img.pad((5,0), "white") if img.width > base.width * 2 else img, rows)
# chart = Image.from_column([Image.from_row(row, yalign=0, padding=5, bg="white") for row in padded], bg="white", xalign=0, padding=10)

title = Image.from_text("Visualizing gravity in 2 Dimensions".upper(), arial(48, bold=True))

def shape_box(alpha=0,min=None,max=None):
    return shapeplot(Rectangle(40,(0,0,0,alpha)), min=min and Rectangle(40,0).place(min), max=max and Rectangle(40,0).place(max))
def line_box(color):return Rectangle(40, 0).place(Rectangle((40,3), color))
    
introduction = generate_legend([], [], header="Some sort of blurb".upper(), footer="Some sort of explanation", border=False)
shape_legend = generate_legend([shape_box(255), shape_box(100), shape_box(0), shape_box(min=dot), shape_box(max=dot)],["high density", "low density", "empty space", "minimum gravity", "maximum gravity"], header="SHAPES AND EXTREMA", border=False)
heatmap_legend = generate_legend([Image.from_gradient(plt.get_cmap("hot"), (40, 180), direction=(0,-1)).add_grid((1,8))], [["max gravity", "50% gravity", "min gravity"]], header="GRAVITY HEATMAPS", border=False)
graph_legend = generate_legend([line_box("#800000"), line_box("#008000"), line_box("#000080")], ["horizontal intersection", "vertical intersection", "diagonal intersection"], header="INTERSECTION PLOTS", border=False)
legend=Image.from_row([introduction, shape_legend, heatmap_legend, graph_legend], bg="white", padding=10, yalign=0).pad(2, "black")

# https://physics.stackexchange.com/questions/30652/what-is-the-2d-gravity-potential

# gravity in 2d
# inverse square, squashed into plane
# inverse, 2d version, orbits are oscillations

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
