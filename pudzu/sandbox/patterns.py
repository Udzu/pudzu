import argparse
import copy
import json
from functools import reduce
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import *
from pudzu.utils import *

State =  Union[str, Collection['State']]
Move = Enum('Move', 'EMPTY ALL')
Input = Union[str, Move]
Transitions = Dict[Tuple[State, Input], AbstractSet[State]]

renderer = optional_import("PySimpleAutomata.automata_IO")

class NFA:
    """Nondeterministic Finite Automata with
    - single start state (with no inbounds) and end state (with no outbounds)
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
        def label(s): 
            # TODO: enumerate states by depth
            if isinstance(s, str): return "".join(reversed(s))
            else: return "("+ "|".join(label(t) for t in s) + ")"
        states = {s : label(s) for s in self.states}
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
        
    def remove_redundant_states(self) -> None:
        # remove states not reachable from the start
        reachable, new = set(), {self.start}
        while new:
            reachable.update(new)
            new = {t for (s,i),ts in self.transitions.items() if s in new for t in ts if t not in reachable}
        self.states = reachable | { self.start, self.end }
        self.transitions = {(s,i): ts for (s,i),ts in self.transitions.items() if s in reachable}
        # remove states that can't reach the end (and any transitions to those states)
        acceptable, new = set(), {self.end}
        while new:
            acceptable.update(new)
            new = {s for (s,i),ts in self.transitions.items() if any(t in new for t in ts) and s not in acceptable}
        self.states = acceptable | { self.start, self.end }
        self.transitions = {(s,i): {t for t in ts if t in acceptable} for (s,i),ts in self.transitions.items()
                            if s in acceptable and (any(t in acceptable for t in ts) or (s,Move.ALL) in self.transitions)}
        # TODO: remove redundant ε states?


# NFA constructors
def merge_trans(*args):
    """Merge multiple transitions, unioning target states."""
    return merge_with(lambda x: set.union(*x), *args)

def MatchIn(characters: str) -> NFA:
    """Handles: a, [abc]"""
    return NFA("1", "2", {("1", c): {"2"} for c in characters})

def MatchNotIn(characters: str) -> NFA:
    """Handles: [^abc], ."""
    return NFA("1", "2", merge_trans({("1", Move.ALL): {"2"}}, {("1", c): set() for c in characters}))

def MatchAfter(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: AB"""
    t1 = {(s+"1",i): {t+"1" for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2 = {(nfa1.end+"1" if s == nfa2.start else s+"2",i): {nfa1.end+"1" if t == nfa2.start else t+"2" for t in ts} for (s,i),ts in nfa2.transitions.items()}
    return NFA(nfa1.start+"1", nfa2.end+"2", merge_trans(t1, t2))

def MatchEither(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: A|B"""
    t1 = {(s+"1",i): {t+"1" for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2 = {(s+"2",i): {t+"2" for t in ts} for (s,i),ts in nfa2.transitions.items()}
    t12 = {("1", Move.EMPTY): {nfa1.start+"1", nfa2.start+"2"}, (nfa1.end+"1", Move.EMPTY): {"2"}, (nfa2.end+"2", Move.EMPTY): {"2"}}
    return NFA("1", "2", merge_trans(t1, t2, t12))

def MatchRepeated(nfa: NFA, repeat: bool = False, optional: bool = False) -> NFA:
    """Handles: A*, A+, A?"""
    transitions = {(s+"0",i): {t+"0" for t in ts} for (s,i),ts in nfa.transitions.items()}
    transitions[("1", Move.EMPTY)] = {nfa.start+"0"}
    if optional: transitions[("1", Move.EMPTY)].add("2")
    transitions[(nfa.end+"0", Move.EMPTY)] = {"2"}
    if repeat: transitions[(nfa.end+"0", Move.EMPTY)].add(nfa.start+"0")
    return NFA("1", "2", transitions)

def MatchRepeatedN(nfa: NFA, minimum: int, maximum: int) -> NFA:
    """Handles: A{2,5}"""
    if minimum == maximum == 0:
        return NFA("1", "2", {("1", Move.EMPTY): {"2"}})
    elif minimum == maximum == 1:
        return nfa
    elif minimum > 0:
        return MatchAfter(nfa, MatchRepeatedN(nfa, minimum-1, maximum-1))
    elif maximum == 1:
        return MatchRepeated(nfa, optional=True)
    else:
        return MatchRepeated(MatchAfter(nfa, MatchRepeatedN(nfa, 0, maximum-1)), optional=True)
    
def MatchRepeatedNplus(nfa: NFA, minimum: int) -> NFA:
    """Handles: A{2,}"""
    if minimum == 0:
        return MatchRepeated(nfa, repeat = True, optional=True)
    elif minimum == 1:
        return MatchRepeated(nfa, repeat = True)
    else:
        return MatchAfter(nfa, MatchRepeatedNplus(nfa, minimum-1))
    
def MatchBoth(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: A&B"""
    # generate transitions on cartesian product (with special handling for *-transitions)
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
    nfa.remove_redundant_states()
    return nfa

def MatchNot(nfa: NFA) -> NFA:
    """Handles: !A"""
    raise NotImplementedError

def MatchReversed(nfa: NFA) -> NFA:
    """Handles: @r(A)"""
    # just reverse the edges
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
    nfa.remove_redundant_states()
    return nfa

def MatchContains(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A<B, A<<B, A>B, A>>B"""
    # transition between (2) A, (3) AxB, and (5) A states
    # for proper, also use (1) A and (4) A states
    t1, t1e, t4, t4e = {}, {}, {}, {}

    if proper:
        t1 = {(s+"1",i): {t+"1" for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(s+"1",i): {t+"2" for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}

    t2 = {(s+"2",i): {t+"2" for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2e = {(s+"2", Move.EMPTY): {(s+"3",nfa2.start)} for s in nfa1.states}

    t3 = {((s+"3",q), i): {(s+"3",t) for t in ts} for (q,i),ts in nfa2.transitions.items() for s in nfa1.states}
    t3e = {((s+"3",nfa2.end), Move.EMPTY): {(s+"4" if proper else s+"5")} for s in nfa1.states}

    if proper:
        t4 = {(s+"4",i): {t+"4" for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
        t4e = {(s+"4",i): {t+"5" for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}

    t5 = {(s+"5",i): {t+"5" for t in ts} for (s,i),ts in nfa1.transitions.items()}

    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e, t5)
    nfa = NFA(nfa1.start+"1" if proper else nfa1.start+"2", nfa1.end+"5", transitions)
    nfa.remove_redundant_states()
    return nfa

def MatchInterleaved(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A^B, A^^B"""
    # transition between (2) AxB and (3) AxB states
    # for proper, also use (1) A and (4) A states
    t1, t1e, t4, t4e = {}, {}, {}, {}

    if proper:
        t1 = {(s+"1",i): {t+"1" for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(s+"1",i): {(t+"2",nfa2.start) for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}

    t2 = {((s+"2",q), i): {(t+"2",q) for t in ts} for (s,i),ts in nfa1.transitions.items() for q in nfa2.states}
    t2e = {((q+"2",s), Move.EMPTY): {(q+"3",s)} for q in nfa1.states for s in nfa2.states}
    
    t3 = {((q+"3",s), i): {(q+"3",t) for t in ts} for (s,i),ts in nfa2.transitions.items() for q in nfa1.states}
    t3e = {((q+"3",s), Move.EMPTY): {(q+"2",s)} for q in nfa1.states for s in nfa2.states}
    
    if proper:
        t4 = {((s+"2",nfa2.end),i): {t+"4" for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}
        t4e = {(s+"4",i): {t+"4" for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
    
    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e)
    nfa = NFA(nfa1.start+"1" if proper else (nfa1.start+"2", nfa2.start), 
              nfa1.end+"4" if proper else (nfa1.end+"3", nfa2.end), transitions)
    nfa.remove_redundant_states()
    return nfa

def MatchAlternating(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A#B, A##B"""
    raise NotImplementedError

# Parser
class Pattern:
    from pyparsing import (
        Word, Optional, oneOf, Forward, OneOrMore, alphas, Group, Literal, infixNotation, opAssoc,
        ParserElement, nums
    )
    ParserElement.setDefaultWhitespaceChars('')

    # TODO: escaping, unicode
    _0_to_19 = Group(Optional("1") + Word(nums, exact=1)).setParseAction(lambda t: ''.join(t[0]))
    literal = Word(alphas + " '-", exact=1).setParseAction(lambda t: MatchIn(t[0]))
    dot = Literal(".").setParseAction(lambda t: MatchNotIn(""))
    set = ("[" + Word(alphas, min=1) + "]").setParseAction(lambda t: MatchIn(t[1]))
    nset = ("[^" + Word(alphas, min=1) + "]").setParseAction(lambda t: MatchNotIn(t[1]))

    expr = Forward()
    group = ("(" + expr + ")").setParseAction(lambda t: t[1])
    atom = literal | dot | set | nset | group
    item = (
        (atom + "+").setParseAction(lambda t: MatchRepeated(t[0], repeat=True,)) |
        (atom + "*").setParseAction(lambda t: MatchRepeated(t[0], repeat=True, optional=True)) |
        (atom + "?").setParseAction(lambda t: MatchRepeated(t[0], optional=True)) |
        (atom + "{" + _0_to_19 + "}").setParseAction(lambda t: MatchRepeatedN(t[0], int(t[2]), int(t[2]))) |
        (atom + "{" + _0_to_19 + ",}").setParseAction(lambda t: MatchRepeatedNplus(t[0], int(t[2]))) |
        (atom + "{" + _0_to_19 + "," + _0_to_19 + "}").setParseAction(lambda t: MatchRepeatedN(t[0], int(t[2]), int(t[4]))) |
        # TODO: not
        ("@r" + atom).setParseAction(lambda t: MatchReversed(t[1])) |
        atom
    )
    items = OneOrMore(item).setParseAction(lambda t: reduce(MatchAfter, t))
    
    expr <<= infixNotation(items, [
        ('&', 2, opAssoc.LEFT, lambda t: MatchBoth(t[0][0], t[0][2])),
        (oneOf(('>', '<', '>>', '<<', '^', '^^')), 2, opAssoc.LEFT, lambda t:
            MatchContains(t[0][0], t[0][2], proper=True) if t[0][1] == '>>' else
            MatchContains(t[0][2], t[0][0], proper=True) if t[0][1] == '<<' else
            MatchContains(t[0][0], t[0][2], proper=False) if t[0][1] == '>' else
            MatchContains(t[0][2], t[0][0], proper=False) if t[0][1] == '<' else
            MatchInterleaved(t[0][0], t[0][2], proper=True) if t[0][1] == '^^' else
            MatchInterleaved(t[0][0], t[0][2], proper=False) # '^'
            # TODO: alternating
         ),
        ('|', 2, opAssoc.LEFT, lambda t: MatchEither(t[0][0], t[0][2])),
    ])

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.nfa = self.expr.parseString(pattern, parseAll=True)[0]

    def __repr__(self):
        return f"Pattern({self.pattern!r})"
        
    def match(self, string: str) -> bool:
        return self.nfa.match(string)

def main():
    # TODO: case-insensitive, predefined character ranges (in cfg)?
    parser = argparse.ArgumentParser(description = 'NFA-based pattern matcher')
    parser.add_argument("pattern", type=str, help="pattern to match against")
    parser.add_argument("file", type=str, help="filename to search")
    parser.add_argument("-n", "--nfa", action="store_true", help="generate nfa diagram")
    args = parser.parse_args()
    
    pattern = Pattern(args.pattern)
    if args.nfa: pattern.nfa.render("nfa")
    with open(args.file, "r", encoding="utf-8") as f:
        for w in f:
            word = w.rstrip("\n")
            if pattern.match(word):
                print(word, flush=True)

if __name__ == '__main__':
    main()