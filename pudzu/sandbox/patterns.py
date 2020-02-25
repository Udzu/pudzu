import copy
from functools import reduce
from typing import *
from pudzu.utils import *

State = Union[int, Collection['State']]
Move = Enum('Move', 'EMPTY ALL')
Input = Union[str, Move]
Transitions = Dict[Tuple[State, Input], AbstractSet[State]]


class NFA:
    """Nondeterministic Finite Automata with
    - single start and end state
    - ε-moves (including potential ε loops)
    - *-moves (only used if there is no other matching move)
    """

    def __init__(self, start: State, end: State, transitions: Transitions):
        self.start = start
        self.end = end
        self.transitions = transitions
        
    def __repr__(self) -> str:
        return f"NFA(start={self.start}, end={self.end}, transitions={self.transitions})"
        
    def match(self, string: str) -> bool:
        states = self._expand_epsilons({ self.start })
        for c in string:
            states = { t for s in states for t in self.transitions.get((s, c), self.transitions.get((s, Move.ALL), set())) }
            states = self._expand_epsilons(states)
        return self.end in states

    def _expand_epsilons(self, states: AbstractSet[State]) -> AbstractSet[State]:
        old, new = set(), states
        while new:
            old.update(new)
            new = { t for s in new for t in self.transitions.get((s, Move.EMPTY), set()) if t not in old }
        return old
        
    def remove_unreachable_states(self) -> None:
        ...

        
def MatchIn(characters: str) -> NFA:
    """Handles: a, [abc]"""
    return NFA(0, 1, {(0, c): {1} for c in characters})

def MatchNotIn(characters: str) -> NFA:
    """Handles: [^abc], ."""
    return NFA(0, 1, merge({(0, Move.ALL): {1}}, {(0, c): set() for c in characters}))

def MatchAfter(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: ab"""
    t1 = {((s,1),i): {(t,1) for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2 = {((nfa1.end, 1) if s == nfa2.start else (s,2),i): {(t,2) for t in ts} for (s,i),ts in nfa2.transitions.items()}
    return NFA((nfa1.start, 1), (nfa2.end, 2), merge(t1, t2))
    
def MatchEither(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: a|b"""
    t1 = {((s,1),i): {(t,1) for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2 = {((s,2),i): {(t,2) for t in ts} for (s,i),ts in nfa2.transitions.items()}
    t12 = {(0, Move.EMPTY): {(nfa1.start, 1), (nfa2.start, 2)}, ((nfa1.end, 1), Move.EMPTY): {1}, ((nfa2.end, 2), Move.EMPTY): {1}}
    return NFA(0, 1, merge(t1, t2, t12))

def MatchRepeated(nfa: NFA, repeat: bool, optional: bool) -> NFA:
    """Handles: a*, a+, a?"""
    transitions = copy.deepcopy(nfa.transitions)
    if optional: transitions.setdefault((nfa.start, Move.EMPTY), set()).add(nfa.end)
    if repeat: transitions.setdefault((nfa.end, Move.EMPTY), set()).add(nfa.start)
    return NFA(nfa.start, nfa.end, transitions)


class Pattern:
    from pyparsing import Word, Optional, oneOf, Forward, OneOrMore, alphas, Group, Literal
    
    # TODO: parser actions, whitespace handling, braces, operators, unicode, escaping
    literal = Word(alphas, exact=1).setParseAction(lambda t: MatchIn(t[0]))
    dot = Literal(".").setParseAction(lambda t: MatchNotIn(""))
    set = ("[" + Word(alphas, min=1) + "]").setParseAction(lambda t: MatchIn(t[1]))
    negset = ("[^" + Word(alphas, min=1) + "]").setParseAction(lambda t: MatchNotIn(t[1]))
    postfix = oneOf("?+*")
    
    expr = Forward()
    group = Group("(" + expr + ")")
    atom = literal | dot | set | negset | group
    item = atom + Optional(postfix)
    items = OneOrMore(item).setParseAction(lambda t: reduce(MatchAfter, t))
    
    expr <<= items

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.nfa = self.expr.parseString(pattern)[0]

    def __repr__(self):
        return f"Pattern({self.pattern!r})"
        
    def match(self, string: str) -> bool:
        return self.nfa.match(string)
