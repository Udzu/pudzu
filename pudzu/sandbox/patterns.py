import copy
import json
from functools import reduce
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import *
from pudzu.utils import *

State = Union[int, Collection['State']]
Move = Enum('Move', 'EMPTY ALL')
Input = Union[str, Move]
Transitions = Dict[Tuple[State, Input], AbstractSet[State]]

renderer = optional_import("PySimpleAutomata.automata_IO")

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
        self.states = {self.start, self.end} | {s for s,_ in self.transitions.keys()} | {t for ts in self.transitions.values() for t in ts}

    def __repr__(self) -> str:
        return f"NFA(start={self.start}, end={self.end}, transitions={self.transitions})"

    def render(self, name: str, path: str = './') -> None:
        states = {s : str(i) for i,s in enumerate(self.states)}
        def move(i): return {Move.ALL: '*', Move.EMPTY: 'ε'}.get(i, i)
        alphabet = {move(i) for (_,i),_ in self.transitions.items()}
        nfa_json = {
            "alphabet": set(sorted(alphabet)),
            "states": set(sorted(states.values())),
            "initial_states": {states[self.start]},
            "accepting_states": {states[self.end]},
            "transitions": {(states[s],move(i)): {states[t] for t in ts} or {states[s]+"'"} for (s,i),ts in self.transitions.items()}
        }
        renderer.nfa_to_dot(nfa_json, name, path)

    def match(self, string: str) -> bool:
        states = self._expand_epsilons({ self.start })
        for c in string:
            states = {t for s in states for t in self.transitions.get((s, c), self.transitions.get((s, Move.ALL), set()))}
            states = self._expand_epsilons(states)
        return self.end in states

    def _expand_epsilons(self, states: AbstractSet[State]) -> AbstractSet[State]:
        old, new = set(), states
        while new:
            old.update(new)
            new = {t for s in new for t in self.transitions.get((s, Move.EMPTY), set()) if t not in old}
        return old
        
    def remove_unreachable_states(self) -> None:
        reachable, new = set(), {self.start}
        while new:
            reachable.update(new)
            new = {t for (s,i),ts in self.transitions.items() if s in new for t in ts if t not in reachable}
        self.states = reachable | { self.start, self.end }
        self.transitions = {(s,i): ts for (s,i),ts in self.transitions.items() if s in reachable}

# NFA constructors
def merge_trans(*args):
    """Merge multiple transitions, unioning target states."""
    return merge_with(lambda x: set.union(*x), *args)

def MatchIn(characters: str) -> NFA:
    """Handles: a, [abc]"""
    return NFA(0, 1, {(0, c): {1} for c in characters})

def MatchNotIn(characters: str) -> NFA:
    """Handles: [^abc], ."""
    return NFA(0, 1, merge_trans({(0, Move.ALL): {1}}, {(0, c): set() for c in characters}))

def MatchAfter(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: ab"""
    t1 = {((s,1),i): {(t,1) for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2 = {((nfa1.end, 1) if s == nfa2.start else (s,2),i): {(nfa1.end, 1) if t == nfa2.start else (t,2) for t in ts} for (s,i),ts in nfa2.transitions.items()}
    return NFA((nfa1.start, 1), (nfa2.end, 2), merge_trans(t1, t2))

def MatchEither(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: a|b"""
    t1 = {((s,1),i): {(t,1) for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2 = {((s,2),i): {(t,2) for t in ts} for (s,i),ts in nfa2.transitions.items()}
    t12 = {(0, Move.EMPTY): {(nfa1.start, 1), (nfa2.start, 2)}, ((nfa1.end, 1), Move.EMPTY): {1}, ((nfa2.end, 2), Move.EMPTY): {1}}
    return NFA(0, 1, merge_trans(t1, t2, t12))

def MatchRepeated(nfa: NFA, repeat: bool, optional: bool) -> NFA:
    """Handles: a*, a+, a?"""
    transitions = copy.deepcopy(nfa.transitions)
    if optional: transitions.setdefault((nfa.start, Move.EMPTY), set()).add(nfa.end)
    if repeat: transitions.setdefault((nfa.end, Move.EMPTY), set()).add(nfa.start)
    return NFA(nfa.start, nfa.end, transitions)

def MatchBoth(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: a&b"""
    # generate transitions on cartesian product (take care when handling *-transitions)
    transitions = {}
    for (s1, i), ts1 in nfa1.transitions.items():
        for s2 in nfa2.states:
            if i == Move.EMPTY:
                transitions = merge_trans(transitions, {((s1, s2), i): set(product(ts1, {s2}))})
            else:
                ts2 = nfa2.transitions.get((s2, i), nfa2.transitions.get((s2, Move.ALL)))
                if ts2 is not None:
                    transitions = merge_trans(transitions, {((s1, s2), i): set(product(ts1, ts2))})
    for (s2, i), ts2 in nfa2.transitions.items():
        for s1 in nfa1.states:
            if i == Move.EMPTY:
                transitions = merge_trans(transitions, {((s1, s2), i): set(product({s1}, ts2))})
            elif (s1, i) not in nfa1.transitions:  # (we've done those already!)
                ts1 = nfa1.transitions.get((s1, Move.ALL))
                if ts1 is not None:
                    transitions = merge_trans(transitions, {((s1, s2), i): set(product(ts1, ts2))})
    nfa = NFA((nfa1.start, nfa2.start), (nfa1.end, nfa2.end), transitions)
    nfa.remove_unreachable_states()
    return nfa

def MatchNot(nfa: NFA) -> NFA:
    raise NotImplementedError

def MatchReversed(nfa: NFA) -> NFA:
    transitions = {}
    for (s,i),ts in nfa.transitions.items():
        for t in ts:
            transitions.setdefault((t,i),set()).add(s)
            if i == Move.ALL:
                # handle *-transitions (if it's not too difficult)
                if any(u==t and vs-{s} for (u,j),vs in transitions.items()):
                    raise NotImplementedError  # TODO?
                for (r,j),_ in nfa.transitions.items():
                    if r == s and not isinstance(j, Move):
                        transitions.setdefault((t,j),set())
    nfa = NFA(nfa.end, nfa.start, transitions)
    nfa.remove_unreachable_states()
    return nfa

# Parser
class Pattern:
    from pyparsing import (
        Word, Optional, oneOf, Forward, OneOrMore, alphas, Group, Literal, infixNotation, opAssoc,
        ParserElement
    )
    ParserElement.setDefaultWhitespaceChars('')

    # TODO: escaping, unicode
    literal = Word(alphas + " '-", exact=1).setParseAction(lambda t: MatchIn(t[0]))
    dot = Literal(".").setParseAction(lambda t: MatchNotIn(""))
    set = ("[" + Word(alphas, min=1) + "]").setParseAction(lambda t: MatchIn(t[1]))
    nset = ("[^" + Word(alphas, min=1) + "]").setParseAction(lambda t: MatchNotIn(t[1]))

    expr = Forward()
    group = ("(" + expr + ")").setParseAction(lambda t: t[1])
    atom = literal | dot | set | nset | group
    item = (
        (atom + "+").setParseAction(lambda t: MatchRepeated(t[0], repeat=True, optional=False)) |
        (atom + "*").setParseAction(lambda t: MatchRepeated(t[0], repeat=True, optional=True)) |
        (atom + "?").setParseAction(lambda t: MatchRepeated(t[0], repeat=False, optional=True)) |
        # TODO: {m,n}, {m,}
        ("!" + atom).setParseAction(lambda t: MatchNot(t[1])) |
        ("@r" + atom).setParseAction(lambda t: MatchReversed(t[1])) |
        atom
    )
    items = OneOrMore(item).setParseAction(lambda t: reduce(MatchAfter, t))
    
    expr <<= infixNotation(items, [
        ('&', 2, opAssoc.LEFT, lambda t: MatchBoth(t[0][0], t[0][2])),
        ('|', 2, opAssoc.LEFT, lambda t: MatchEither(t[0][0], t[0][2])),
    ])

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.nfa = self.expr.parseString(pattern, parseAll=True)[0]

    def __repr__(self):
        return f"Pattern({self.pattern!r})"
        
    def match(self, string: str) -> bool:
        return self.nfa.match(string)
