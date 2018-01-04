import sys
import matplotlib.pyplot as plt
sys.path.append('..')
from pillar import *
from scipy import signal

# naive gravity calculation that's good enough because numpy

np.seterr(divide='ignore', invalid='ignore')

def inverse_square_components(rows, cols):
    xs = np.fromfunction(lambda i,j: (rows-1-i), (2*rows-1, 2*cols-1))
    ys = np.fromfunction(lambda i,j: (cols-1-j), (2*rows-1, 2*cols-1))
    n3 = (xs**2 + ys**2) ** (3/2)
    return np.nan_to_num(xs / n3), np.nan_to_num(ys / n3)

def gravity_components(arr):
    isqxs, isqys = inverse_square_components(*arr.shape)
    xs = np.rot90(signal.convolve2d(np.rot90(arr, 2), isqxs, 'same'), 2)
    ys = np.rot90(signal.convolve2d(np.rot90(arr, 2), isqys, 'same'), 2)
    return xs, ys

def gmag(arr, normalised=True):
    if isinstance(arr, Image.Image): arr = mask_to_array(arr)
    components = gravity_components(arr)
    mag = (components[0] ** 2 + components[1] ** 2) ** 0.5
    return mag / mag.max() if normalised else mag

# visualisation

def mask_to_array(img):
    return np.array(img.as_mask()) / 255
    
def heatmap(array, cmap=plt.get_cmap("hot")):
    return Image.fromarray(cmap(array, bytes=True))
   
def plot_box(data, width, filename):
    # TODO: zero at center, set axis limits?
    fig = plt.figure(figsize=(1,1), dpi=width)
    ax = fig.add_axes((0,0,1,1))
    ax.set_axis_off()
    ax.plot(data)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.savefig(filename, bbox_inches="tight", pad_inches=0, dpi=width)

# shapes TODO: circle, ellipse, core, hollow, mountain, plateau, two, two weighted, square, rectangle, ?, reddit

circle = Ellipse(95).pad(10, 0)
ellipse = Ellipse((95,55)).pad((10,30), 0)
core = Ellipse(95, (0,0,0,127)).place(Ellipse(31)).pad(10,0)

# mag = gmag(ellipse)
# heatmap(mag).save("cache/gravity_heatmap.png")
# plot_box(mag[round(mag.shape[0] / 2)], mag.shape[1], "cache/gravity_plot.png")

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
