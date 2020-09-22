from collections import namedtuple
from turtle import *

from pudzu.utils import *

wn = Screen()


class LSystem:

    Rule = namedtuple("Rule", "predecessor successor weight", defaults=(1.0,))

    def __init__(self, axiom, rules, angle=4):
        self.axiom = axiom
        self.angle = 360 / angle
        self.rules = {}
        self.weights = {}
        for rule in rules:
            pr = self.Rule(*rule)
            self.rules.setdefault(pr.predecessor, []).append(pr.successor)
            self.weights.setdefault(pr.predecessor, []).append(pr.weight)

    def expand(self, iterations):
        state = self.axiom
        for _ in range(iterations):
            state = "".join([weighted_choice(self.rules.get(c, [c]), self.weights.get(c, [1])) for c in state])
        return state

    def plot(self, iterations, size, reset=True, tracer=(0, 0)):
        if reset:
            wn.clearscreen()
        wn.tracer(*tracer)
        stack = []
        for c in self.expand(iterations):
            if c == "F":
                fd(size)
            elif c == "G":
                pu()
                fd(size)
                pd()
            elif c == "+":
                rt(self.angle)
            elif c == "-":
                lt(self.angle)
            elif c == "[":
                stack.append((position(), heading()))
            elif c == "]":
                p, h = stack.pop()
                pu()
                setposition(p)
                setheading(h)
                pd()
        wn.update()


Koch = LSystem("F--F--F", [("F", "F+F--F+F")], 6)
Dragon = LSystem("FX", [("F", ""), ("Y", "+FX--FY+"), ("X", "-FX++FY-")], 8)
Plant07 = LSystem("Z", [("Z", "ZFX[+Z][-Z]"), ("X", "X[-FFF][+FFF]FX")], 14)
Plant08 = LSystem("SLFFF", [("S", "[+++Z][---Z]TS"), ("Z", "+H[-Z]L"), ("H", "-Z[+H]L"), ("T", "TL"), ("L", "[-FFF][+FFF]F")], 20)
Sierpinski = LSystem("AF", [("A", "BF+AF+BF"), ("B", "AF-BF-AF"), ("F", "")], 6)
Barnsley = LSystem("X", [("X", "F+[[X]-X]-F[-FX]+X"), ("F", "FF")], 14.4)
RandomWalk = LSystem("F", [("F", "FF"), ("F", "F+F"), ("F", "F++F"), ("F", "F-F")], 4)
