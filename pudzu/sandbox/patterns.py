import argparse
import copy
import graphviz  # type: ignore
import json
import logging
import math
import random
import string
from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast, Any, Dict, Iterable, List, Optional, Set, Tuple, Union

from pudzu.utils import optional_import, merge_with, first  # type: ignore

State = Any  # really it's Union[str, Tuple['State']]
Move = Enum("Move", "EMPTY ALL")
Input = Union[str, Move]
Transitions = Dict[Tuple[State, Input], Set[State]]

logger = logging.getLogger("patterns")

DEBUG = False
DICTIONARY_FSM = None
EXPLICIT_FSM = None
SUBPATTERNS = {}


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
        self.states = {self.start, self.end} | {s for s, _ in self.transitions.keys()} | {t for ts in self.transitions.values() for t in ts}

    def __repr__(self) -> str:
        return f"NFA(start={self.start}, end={self.end}, transitions={self.transitions})"

    def match(self, string: str) -> bool:
        """Match the NFA against a string input."""
        states = self.expand_epsilons({self.start})
        for c in string:
            states = {t for s in states for t in self.transitions.get((s, c), self.transitions.get((s, Move.ALL), set()))}
            states = self.expand_epsilons(states)
        return self.end in states

    def expand_epsilons(self, states: Iterable[State]) -> Set[State]:
        """Expand a collection of states along all ε-moves"""
        old: Set[State] = set()
        new = states
        while new:
            old.update(new)
            new = {t for s in new for t in self.transitions.get((s, Move.EMPTY), set()) if t not in old}
        return old

    def remove_redundant_states(self, aggressive: bool = False) -> None:
        """Trim the NFA, removing unnecessary states and transitions."""
        # remove states not reachable from the start
        reachable, new = set(), {self.start}
        while new:
            reachable.update(new)
            new = {t for (s, i), ts in self.transitions.items() if s in new for t in ts if t not in reachable}
        self.states = reachable | {self.start, self.end}
        self.transitions = {(s, i): ts for (s, i), ts in self.transitions.items() if s in reachable}
        # remove states that can't reach the end (and any transitions to those states)
        acceptable, new = set(), {self.end}
        while new:
            acceptable.update(new)
            new = {s for (s, i), ts in self.transitions.items() if any(t in new for t in ts) and s not in acceptable}
        self.states = acceptable | {self.start, self.end}
        self.transitions = {
            (s, i): {t for t in ts if t in acceptable}
            for (s, i), ts in self.transitions.items()
            if s in acceptable and (any(t in acceptable for t in ts) or (s, Move.ALL) in self.transitions)
        }
        # remove transitions that are equivalent to *
        unnecessary: List[Tuple[State, Input]] = []
        for (s, i), t in self.transitions.items():
            if not isinstance(i, Move) and t == self.transitions.get((s, Move.ALL), set()):
                unnecessary.append((s, i))
        for k in unnecessary:
            del self.transitions[k]

        if aggressive:
            # remove states that only go to self.end
            # (don't call this from MatchBoth as it would break assumptions of some calling functions)
            removable = set()
            not_removable = set()
            for (s, i), t in self.transitions.items():
                if s != self.start and i == Move.EMPTY and t == {self.end}:
                    removable.add(s)
                else:
                    not_removable.add(s)
            removable = removable - not_removable
            if removable:
                unnecessary = []
                for (s, i), ts in self.transitions.items():
                    if s in removable:
                        unnecessary.append((s, i))
                    elif any(t in removable for t in ts):
                        self.transitions[(s, i)] = {t for t in ts if t not in removable} | {self.end}
                for k in unnecessary:
                    del self.transitions[k]
                self.states -= removable

    def render(self, name: str, console: bool = False) -> None:
        """Render the NFA as a dot.svg file."""
        bg = "transparent" if console else "white"
        fg = "white" if console else "black"
        g = graphviz.Digraph(format="svg")
        g.attr(rankdir="LR", bgcolor=bg)
        for s in self.states:
            if s == self.start:
                g.node(str(s), root="true", label="", color=fg)
                g.node("prestart", style="invisible")
                g.edge("prestart", str(s), style="bold", color=fg)
            elif s == self.end:
                g.node(str(s), shape="doublecircle", label="", color=fg)
            else:
                g.node(str(s), label="", color=fg)
        for (s, i), ts in self.transitions.items():
            if not ts:
                g.node(str(("fail", s)), label="", color=fg)
            for t in ts or {("fail", s)}:
                g.edge(str(s), str(t), label={Move.ALL: "*", Move.EMPTY: "ε", "": ""}.get(i, i), color=fg, fontcolor=fg)

        g.render(filename=name + ".dot")

    def example(self, min_length: int = 0, max_length: Optional[int] = None) -> Optional[str]:
        """Generate a random matching string. Assumes NFA has been trimmed of states that can't reach the end."""
        nfa = MatchBoth(self, MatchLength(min_length, max_length)) if min_length or max_length is not None else self
        output = ""
        state = nfa.start
        try:
            while state != nfa.end:
                choices = [i for (s, i) in nfa.transitions if s == state]
                non_empty = [i for i in choices if nfa.transitions[(state, i)]]
                i = random.choice(non_empty)
                if i == Move.ALL:
                    # TODO: match with supported scripts
                    options = list(set(string.ascii_letters + string.digits + " '") - set(choices))
                    output += random.choice(options)
                elif isinstance(i, str):
                    output += i
                state = random.choice(list(nfa.transitions[(state, i)]))
        except IndexError:
            return None
        return output

    def regex(self) -> "Regex":
        """Generate a regex corresponding to the NFA."""
        L = {(i, j): RegexEmpty() if i == j else RegexUnion() for i in self.states for j in self.states}
        for (i, a), js in self.transitions.items():
            for j in js:
                if a == Move.ALL:
                    L[i, j] += RegexNegatedChars("".join(b for k, b in self.transitions if i == k and isinstance(b, str)))
                elif a == Move.EMPTY:
                    L[i, j] += RegexEmpty()
                else:
                    L[i, j] += RegexChars(a)
        remaining = set(self.states)
        for k in self.states:
            if k == self.start or k == self.end:
                continue
            remaining.remove(k)
            for i in remaining:
                for j in remaining:
                    L[i, i] += RegexConcat(L[i, k], RegexStar(L[k, k]), L[k, i])
                    L[j, j] += RegexConcat(L[j, k], RegexStar(L[k, k]), L[k, j])
                    L[i, j] += RegexConcat(L[i, k], RegexStar(L[k, k]), L[k, j])
                    L[j, i] += RegexConcat(L[j, k], RegexStar(L[k, k]), L[k, i])
        return L[self.start, self.end]

    def min_length(self) -> Optional[int]:
        """ The minimum possible length match. """
        # use Dijkstra to find shortest path
        unvisited = set(self.states)
        distances = {s: 0 if s == self.start else math.inf for s in self.states}
        current = self.start
        while True:
            base = distances[current]
            for (r, i), ss in self.transitions.items():
                if r == current:
                    weight = base + (i != Move.EMPTY)
                    for s in ss:
                        if s in unvisited:
                            distances[s] = min(distances[s], weight)
            unvisited.remove(current)
            if current == self.end:
                return int(distances[self.end])
            current, distance = min(distances.items(), key=lambda x: math.inf if x[0] not in unvisited else x[1])
            if distance == math.inf:
                return None

    def max_length(self) -> Optional[int]:
        """ The maximum possible length match. """
        # converts to a regex, though there's probably a more efficient way
        max_length = self.regex().max_length()
        return int(max_length) if math.isfinite(max_length) else None


# NFA constructors
def merge_trans(*args):
    """Merge multiple transitions, unioning target states."""
    return merge_with(lambda x: set.union(*x), *args)


def MatchEmpty() -> NFA:
    """RegexEmpty match"""
    return NFA("1", "2", {("1", Move.EMPTY): {"2"}})


def MatchIn(characters: str) -> NFA:
    """Handles: a, [abc]"""
    return NFA("1", "2", {("1", c): {"2"} for c in characters})


def MatchNotIn(characters: str) -> NFA:
    """Handles: [^abc], ."""
    return NFA("1", "2", merge_trans({("1", Move.ALL): {"2"}}, {("1", c): set() for c in characters}))


def MatchWords(words: Iterable[str]) -> NFA:
    # generate a prefix tree
    start, end = ("0",), ("1",)
    transitions: Transitions = {}
    for word in words:
        for i in range(len(word)):
            transitions.setdefault((word[:i] or start, word[i]), set()).add(word[: i + 1])
        transitions[(word, Move.EMPTY)] = {end}
    return NFA(start, end, transitions)


def MatchDictionary(path: Path) -> NFA:
    """Handles: \w"""
    with open(str(path), "r", encoding="utf-8") as f:
        return MatchWords(w.rstrip("\n") for w in f)


def ExplicitFSM(path: Path) -> NFA:
    """Handles: \f"""
    transitions: Transitions = {}
    with open(str(path), "r", encoding="utf-8") as f:
        for line in f:
            args = line.split()
            if args:
                x: Input
                start, x, *end = args
                x = {"EMPTY": Move.EMPTY, "ALL": Move.ALL}.get(x, x)
                if isinstance(x, str) and len(x) > 1:
                    raise ValueError(f"Unexpected FSM input `{x}`: should be character, ALL or EMPTY")
                elif start == "END":
                    raise ValueError("END state should have no outbound arrows")
                elif "START" in end:
                    raise ValueError("START state should have no inbound arrows")
                transitions.setdefault((start, x), set()).update(end)
    return NFA("START", "END", transitions)


def MatchAfter(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: AB"""
    t1 = {(("1", s), i): {("1", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    t2 = {
        (("1", nfa1.end) if s == nfa2.start else ("2", s), i): {("1", nfa1.end) if t == nfa2.start else ("2", t) for t in ts}
        for (s, i), ts in nfa2.transitions.items()
    }
    return NFA(("1", nfa1.start), ("2", nfa2.end), merge_trans(t1, t2))


def MatchEither(*nfas: NFA) -> NFA:
    """Handles: A|B (and arbitrary alternation too)"""
    tis = []
    for n, nfa in enumerate(nfas, 1):
        tis.append({((str(n), s), i): {(str(n), t) for t in ts} for (s, i), ts in nfa.transitions.items()})
    tstart = {("1", Move.EMPTY): {(str(n), nfa.start) for n, nfa in enumerate(nfas, 1)}}
    tend = {((str(n), nfa.end), Move.EMPTY): {"2"} for n, nfa in enumerate(nfas, 1)}
    return NFA("1", "2", merge_trans(tstart, tend, *tis))


def MatchRepeated(nfa: NFA, repeat: bool = False, optional: bool = False) -> NFA:
    """Handles: A*, A+, A?"""
    transitions: Transitions = {(("0", s), i): {("0", t) for t in ts} for (s, i), ts in nfa.transitions.items()}
    transitions[("1", Move.EMPTY)] = {("0", nfa.start)}
    if optional:
        transitions[("1", Move.EMPTY)].add("2")
    transitions[(("0", nfa.end), Move.EMPTY)] = {"2"}
    if repeat:
        transitions[(("0", nfa.end), Move.EMPTY)].add(("0", nfa.start))
    return NFA("1", "2", transitions)


def MatchRepeatedN(nfa: NFA, minimum: int, maximum: int) -> NFA:
    """Handles: A{2,5}"""
    if minimum == maximum == 0:
        return MatchEmpty()
    elif minimum == maximum == 1:
        return nfa
    elif minimum > 0:
        return MatchAfter(nfa, MatchRepeatedN(nfa, minimum - 1, maximum - 1))
    elif maximum == 1:
        return MatchRepeated(nfa, optional=True)
    else:
        return MatchRepeated(MatchAfter(nfa, MatchRepeatedN(nfa, 0, maximum - 1)), optional=True)


def MatchRepeatedNplus(nfa: NFA, minimum: int) -> NFA:
    """Handles: A{2,}"""
    if minimum == 0:
        return MatchRepeated(nfa, repeat=True, optional=True)
    elif minimum == 1:
        return MatchRepeated(nfa, repeat=True)
    else:
        return MatchAfter(nfa, MatchRepeatedNplus(nfa, minimum - 1))


def MatchLength(minimum: int = 0, maximum: Optional[int] = None) -> NFA:
    if maximum is None:
        return MatchRepeatedNplus(MatchNotIn(""), minimum)
    else:
        return MatchRepeatedN(MatchNotIn(""), minimum, maximum)


def MatchDFA(nfa: NFA, negate: bool) -> NFA:
    """Handles: (?D:A), ¬A"""
    # convert to DFA via powerset construction (and optionally invert accepted/rejected states)
    start_state = tuple(sorted(nfa.expand_epsilons({nfa.start}), key=str))
    to_process = [start_state]
    processed_states = set()
    accepting_states = set()
    transitions: Transitions = {}
    while to_process:
        current_state = to_process.pop()
        processed_states.add(current_state)
        if any(s == nfa.end for s in current_state):
            accepting_states.add(current_state)
        moves = {i for (s, i) in nfa.transitions if s in current_state and i != Move.EMPTY}
        for i in moves:
            next_state = {t for s in current_state for t in nfa.transitions.get((s, i), nfa.transitions.get((s, Move.ALL), set()))}
            next_state_sorted = tuple(sorted(nfa.expand_epsilons(next_state), key=str))
            transitions[(current_state, i)] = {next_state_sorted}
            if next_state_sorted not in processed_states:
                to_process.append(next_state_sorted)

    # transition accepting/non-accepting states to a single final state
    for final_state in (processed_states - accepting_states) if negate else accepting_states:
        transitions.setdefault((final_state, Move.EMPTY), set()).add("2")

    # if negating, transition non-moves to a new accepting, consuming state
    if negate:
        for state in processed_states:
            if (state, Move.ALL) not in transitions:
                transitions[(state, Move.ALL)] = {"1"}
                transitions.setdefault(("1", Move.ALL), {"1"})
                transitions.setdefault(("1", Move.EMPTY), {"2"})

    nfa = NFA(start_state, "2", transitions)
    nfa.remove_redundant_states(aggressive=True)
    return nfa


def MatchBoth(nfa1: NFA, nfa2: NFA, start_from: Optional[Set[State]] = None, stop_at: Optional[Set[State]] = None) -> NFA:
    """Handles: A&B"""
    # generate transitions on cartesian product (with special handling for *-transitions)
    # warning: some of the other methods currently depend on the implementation of this (which is naughty)
    transitions: Transitions = {}
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
                ts1o = nfa1.transitions.get((s1, Move.ALL))
                if ts1o is not None:
                    transitions = merge_trans(transitions, {((s1, s2), i): set(product(ts1o, ts2))})
    if start_from:
        transitions[("1", Move.EMPTY)] = start_from
    if stop_at:
        transitions = merge_trans(transitions, {(s, Move.EMPTY): {"2"} for s in stop_at})
    nfa = NFA("1" if start_from else (nfa1.start, nfa2.start), "2" if stop_at else (nfa1.end, nfa2.end), transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchContains(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A<B, A<<B, A>B, A>>B"""
    # transition from (2) A to (3) AxB to (5) A states
    # for proper containment, also use (1) A and (4) A states
    t1, t1e, t4, t4e = {}, {}, {}, {}
    if proper:
        t1 = {(("1", s), i): {("1", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(("1", s), i): {("2", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
    t2 = {(("2", s), i): {("2", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    t2e = {(("2", s), Move.EMPTY): {("3", s, nfa2.start)} for s in nfa1.states}
    t3 = {(("3", s, q), i): {("3", s, t) for t in ts} for (q, i), ts in nfa2.transitions.items() for s in nfa1.states}
    t3e = {(("3", s, nfa2.end), Move.EMPTY): {(("4", s) if proper else ("5", s))} for s in nfa1.states}
    if proper:
        t4 = {(("4", s), i): {("4", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t4e = {(("4", s), i): {("5", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
    t5 = {(("5", s), i): {("5", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e, t5)
    nfa = NFA(("1", nfa1.start) if proper else ("2", nfa1.start), ("5", nfa1.end), transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchInterleaved(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A^B, A^^B"""
    # transition between (2) AxB and (3) AxB states
    # for proper interleaving, also use (1) A and (4) A states
    t1, t1e, t4, t4e = {}, {}, {}, {}
    if proper:
        t1 = {(("1", s), i): {("1", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(("1", s), i): {("2", t, nfa2.start) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
    t2 = {(("2", s, q), i): {("2", t, q) for t in ts} for (s, i), ts in nfa1.transitions.items() for q in nfa2.states}
    t2e = {(("2", q, s), Move.EMPTY): {("3", q, s)} for q in nfa1.states for s in nfa2.states}
    t3 = {(("3", q, s), i): {("3", q, t) for t in ts} for (s, i), ts in nfa2.transitions.items() for q in nfa1.states}
    t3e = {(("3", q, s), Move.EMPTY): {("2", q, s)} for q in nfa1.states for s in nfa2.states}
    if proper:
        t4 = {(("2", s, nfa2.end), i): {("4", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        t4e = {(("4", s), i): {("4", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e)
    nfa = NFA(("1", nfa1.start) if proper else ("2", nfa1.start, nfa2.start), ("4", nfa1.end) if proper else ("3", nfa1.end, nfa2.end), transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchAlternating(nfa1: NFA, nfa2: NFA, ordered: bool) -> NFA:
    """Handles: A#B, A##B"""
    # transition between (1) AxB and (2) AxB states
    # for order agnostic alternation, also use an additional (0) start state
    t0 = {("0", Move.EMPTY): {("1", nfa1.start, nfa2.start), ("2", nfa1.start, nfa2.start)}} if not ordered else {}
    t1 = {(("1", s, q), i): {("1" if i == Move.EMPTY else "2", t, q) for t in ts} for (s, i), ts in nfa1.transitions.items() for q in nfa2.states}
    t2 = {(("2", q, s), i): {("2" if i == Move.EMPTY else "1", q, t) for t in ts} for (s, i), ts in nfa2.transitions.items() for q in nfa1.states}
    # handle final transitions
    t1e = {(("1", nfa1.end, s), i): {("1", nfa1.end, t) for t in ts} for (s, i), ts in nfa2.transitions.items() if i == Move.EMPTY}
    t2e = {(("2", s, nfa2.end), i): {("2", t, nfa2.end) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
    t21 = {(("2", nfa1.end, nfa2.end), Move.EMPTY): {("1", nfa1.end, nfa2.end)}}
    transitions = merge_trans(t0, t1, t1e, t2, t2e, t21)
    nfa = NFA("0" if not ordered else ("1", nfa1.start, nfa2.start), ("1", nfa1.end, nfa2.end), transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchSubtract(nfa1: NFA, nfa2: NFA, from_right: bool, negate: bool) -> NFA:
    """Handles: A-B, A_-B (and used in slicing)"""
    # rewire end/start state of nfa1 based on partial intersection with nfa2
    if from_right:
        both = MatchBoth(nfa1, nfa2, start_from={(a, nfa2.start) for a in nfa1.states})
    else:
        both = MatchBoth(nfa1, nfa2, stop_at={(a, nfa2.end) for a in nfa1.states})
    if negate:
        return both
    transitions: Transitions = {(("1", s), i): {("1", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    if from_right:
        midpoints = {a for a, _ in both.transitions.get((both.start, Move.EMPTY), set())}
        transitions = merge_trans(transitions, {(("1", s), Move.EMPTY): {"1"} for s in midpoints})
        nfa = NFA(("1", nfa1.start), "1", transitions)
    else:
        midpoints = {a for ((a, b), i), cs in both.transitions.items() if i == Move.EMPTY and both.end in cs}
        transitions[("0", Move.EMPTY)] = {("1", s) for s in midpoints}
        nfa = NFA("0", ("1", nfa1.end), transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchSubtractInside(nfa1: NFA, nfa2: NFA, proper: bool, replace: Optional[NFA] = None) -> NFA:
    """Handles: A->B, A->>B"""
    # like MatchContains, but link (2) and (4)/(5) using partial intersection
    t1, t1e, t3, t3e, t4, t4e = {}, {}, {}, {}, {}, {}
    if proper:
        t1 = {(("1", s), i): {("1", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(("1", s), i): {("2", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
    t2 = {(("2", s), i): {("2", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    t2es = []
    if replace:
        t3 = {(("3", s, q), i): {("3", s, t) for t in ts} for (q, i), ts in replace.transitions.items() for s in nfa1.states}
        t3e = {(("3", s, replace.end), Move.EMPTY): {(("4", s) if proper else ("5", s))} for s in nfa1.states}
    for s in nfa1.states:
        both = MatchBoth(nfa1, nfa2, start_from={(s, nfa2.start)}, stop_at={(a, nfa2.end) for a in nfa1.states})
        new_end = {a for a, _ in both.transitions.get((both.start, Move.EMPTY), set())}
        new_start = {a[0] for (a, i), cs in both.transitions.items() if i == Move.EMPTY and both.end in cs}
        t2es.append({(("2", e), Move.EMPTY): {(("3", s, replace.start) if replace else ("4", s) if proper else ("5", s)) for s in new_start} for e in new_end})
    if proper:
        t4 = {(("4", s), i): {("4", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t4e = {(("4", s), i): {("5", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
    t5 = {(("5", s), i): {("5", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    transitions = merge_trans(t1, t1e, t2, *t2es, t3, t3e, t4, t4e, t5)
    nfa = NFA(("1", nfa1.start) if proper else ("2", nfa1.start), ("5", nfa1.end), transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchSubtractOutside(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A-<B, A-<<B"""
    # Use partial intersections to generate collections of alternatives.
    both_start = MatchBoth(nfa1, nfa2, stop_at={(a, b) for a in nfa1.states for b in nfa2.states})
    both_end = MatchBoth(nfa1, nfa2, start_from={(a, b) for a in nfa1.states for b in nfa2.states})
    both_start_end = {s for (s, i), cs in both_start.transitions.items() if i == Move.EMPTY and both_start.end in cs}
    both_end_start = both_end.transitions.get((both_end.start, Move.EMPTY), set())

    if proper:
        # ensure partial intersections are (potentially) non-empty
        both_start_proper = MatchBoth(both_start, MatchLength(1))
        both_start_end = {
            s[0] for (s, i), cs in both_start_proper.transitions.items() if i == Move.EMPTY and both_start_proper.end in cs and s[0] != both_start.end
        }
        both_end_proper = MatchBoth(both_end, MatchLength(1))
        both_end_start = {s[0] for s in both_end_proper.transitions.get((both_end_proper.start, Move.EMPTY), set()) if s[0] != both_end.start}

    nfas: List[NFA] = []
    midpoints = {b for a, b in both_start_end if any(b == b2 for a2, b2 in both_end_start)}
    for m in midpoints:
        transitions: Transitions = {(("1", s), i): {("1", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
        transitions["0", Move.EMPTY] = {("1", a) for a, b in both_start_end if b == m}
        for a in {a for a, b in both_end_start if b == m}:
            transitions.setdefault((("1", a), Move.EMPTY), set()).add("1")
        nfa = NFA("0", "1", transitions)
        nfa.remove_redundant_states()
        nfas.append(nfa)
    return MatchEither(*nfas)


def MatchSubtractAlternating(nfa1: NFA, nfa2: NFA, ordered: bool, from_right: bool = True) -> NFA:
    """Handles: A-#B, A_-#B, A-##B"""
    # Expand transitions in A with one from A&B (tracking both A and B states)
    both = MatchBoth(nfa1, nfa2, stop_at={(a, b) for a in nfa1.states for b in nfa2.states}, start_from={(a, b) for a in nfa1.states for b in nfa2.states})
    transitions: Transitions = {}
    for (s, i), ts in nfa1.transitions.items():
        for b in nfa2.states:
            if i == Move.EMPTY:
                states = {(t, b) for t in ts}
            else:
                ts = nfa1.expand_epsilons(ts)
                states = {u for (r, i), us in both.transitions.items() for t in ts if r == (t, b) and i != Move.EMPTY for u in us}
            transitions[((s, b), i)] = states
            if b == nfa2.end and nfa1.end in ts:
                transitions.setdefault(((s, b), i), set()).add((nfa1.end, nfa2.end))
    for (b, i), cs in nfa2.transitions.items():
        for s in nfa1.states:
            if i == Move.EMPTY:
                transitions[((s, b), i)] = {(s, c) for c in cs}
    start_state = set()
    if not ordered or not from_right:
        ts = {(nfa1.start, nfa2.start)}
        ts = both.expand_epsilons(ts)
        start_state |= {u for (s, i), us in both.transitions.items() if s in ts and i != Move.EMPTY for u in us}
    if not ordered or from_right:
        start_state |= {(nfa1.start, nfa2.start)}
    if len(start_state) == 1:
        nfa = NFA(first(start_state), (nfa1.end, nfa2.end), transitions)
    else:
        transitions[("0", Move.EMPTY)] = start_state
        nfa = NFA("0", (nfa1.end, nfa2.end), transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchSubtractInterleaved(nfa1: NFA, nfa2: NFA, proper: bool, from_right: bool = True) -> NFA:
    """Handles: A-^B, A-^^B, A_-^^B"""
    # Combine transitions from A with empty transitions from A&B (tracking both A and B states)
    both = MatchBoth(nfa1, nfa2, stop_at={(a, b) for a in nfa1.states for b in nfa2.states}, start_from={(a, b) for a in nfa1.states for b in nfa2.states})
    transitions: Transitions = {}
    for (a, i), ts in nfa1.transitions.items():
        for b in nfa2.states:
            transitions[(a, b), i] = {(t, b) for t in ts}
    for (ab, i), tus in both.transitions.items():
        if ab != "1":
            transitions.setdefault((ab, Move.EMPTY), set()).update(tus - {"2"})

    if not proper:
        transitions[((nfa1.end, nfa2.end), Move.EMPTY)] = {"1"}
        nfa = NFA((nfa1.start, nfa2.start), "1", transitions)
    elif from_right:
        t1 = {(("1", s), i): {("1", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(("1", s), i): {("2", (t, nfa2.start)) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        t2 = {(("2", s), i): {("2", t) for t in ts} for (s, i), ts in transitions.items()}
        t2e = {(("2", (s, nfa2.end)), i): {("3", t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        t3 = {(("3", s), i): {("3", t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
        transitions = merge_trans(t1, t1e, t2, t2e, t3)
        nfa = NFA(("1", nfa1.start), ("3", nfa1.end), transitions)
    else:
        ts = both.expand_epsilons({(nfa1.start, nfa2.start)})
        start_states = {u for (s, i), us in both.transitions.items() if s in ts and i != Move.EMPTY for u in us}
        ts = set()
        for t in both.states:
            if (nfa1.end, nfa2.end) in both.expand_epsilons({t}):
                ts.add(t)
        end_states = {s for (s, i), us in both.transitions.items() if any(u in ts for u in us) and i != Move.EMPTY}

        transitions[("0", Move.EMPTY)] = start_states
        for s in end_states:
            transitions[(s, Move.EMPTY)] = {"1"}
        nfa = NFA("0", "1", transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchReversed(nfa: NFA) -> NFA:
    """Handles: (?r:A)"""
    # just reverse the edges (with special handling for *-transitions)
    transitions: Transitions = {}
    for (s, i), ts in nfa.transitions.items():
        for t in ts:
            if i == Move.ALL:
                if any(r != s and t in vs for (r, j), vs in nfa.transitions.items()):
                    extra_state = ("r", s, t)
                    transitions.setdefault((t, Move.EMPTY), set()).add(extra_state)
                    t = extra_state
                for (r, j), _ in nfa.transitions.items():
                    if r == s and not isinstance(j, Move):
                        transitions.setdefault((t, j), set())
            transitions.setdefault((t, i), set()).add(s)
    nfa = NFA(nfa.end, nfa.start, transitions)
    nfa.remove_redundant_states()
    return nfa


def MatchInsensitively(nfa: NFA) -> NFA:
    """Handles: (?i:A)"""
    transitions: Transitions = {}
    for (s, i), ts in nfa.transitions.items():
        if isinstance(i, str):
            transitions.setdefault((s, i.lower()), set()).update(ts)
            transitions.setdefault((s, i.upper()), set()).update(ts)
        else:
            transitions[(s, i)] = ts
    return NFA(nfa.start, nfa.end, transitions)


def MatchShifted(nfa: NFA, shift: int) -> NFA:
    """Handles: (?sn:A)"""
    transitions: Transitions = {}
    for (s, i), ts in nfa.transitions.items():
        for alphabet in (string.ascii_lowercase, string.ascii_uppercase):
            if isinstance(i, str) and i in alphabet:
                i = alphabet[(alphabet.index(i) + shift) % 26]
                break
        transitions[(s, i)] = ts
    return NFA(nfa.start, nfa.end, transitions)


def MatchRotated(nfa: NFA, shift: int) -> NFA:
    """Handles (?Rn:A)"""
    # slice off start/end and for each possibility move it to the other side
    if shift == 0:
        return nfa

    rotations: List[NFA] = []
    if shift < 0:
        window = MatchLength(-shift, -shift)
        intersection = MatchBoth(nfa, window, stop_at={(a, window.end) for a in nfa.states})
        intersection_ends = {s[0] for (s, i), cs in intersection.transitions.items() if i == Move.EMPTY and intersection.end in cs and s[0] != nfa.end}
        for middle in intersection_ends:
            move = MatchBoth(nfa, window, stop_at={(middle, window.end)})
            keep = NFA(middle, nfa.end, nfa.transitions)
            rotated = MatchAfter(keep, move)
            rotated.remove_redundant_states()
            rotations.append(rotated)
    else:
        window = MatchLength(shift, shift)
        intersection = MatchBoth(nfa, window, start_from={(a, window.start) for a in nfa.states})
        intersection_starts = {s[0] for s in intersection.transitions.get(("1", Move.EMPTY), set()) if s[0] != nfa.start}
        for middle in intersection_starts:
            move = MatchBoth(nfa, window, start_from={(middle, window.start)})
            keep = NFA(nfa.start, middle, nfa.transitions)
            rotated = MatchAfter(move, keep)
            rotated.remove_redundant_states()
            rotations.append(rotated)

    rotation = MatchEither(*rotations)
    rotation.remove_redundant_states()
    return rotation


def MatchSlice(nfa: NFA, start: Optional[int], end: Optional[int], step: int) -> NFA:
    """Handles: (?S:A)[3:5], (?S:A)[-1::-2]"""
    # reverse slice is equivalent to slice of reverse
    if step < 0:
        return MatchSlice(MatchReversed(nfa), None if end is None else end + 1, None if start is None else start + 1, -step)
    assert step != 0
    # slice off start
    start = start or 0
    if start > 0:
        nfa = MatchSubtract(nfa, MatchLength(start, start), from_right=False, negate=False)
    elif start < 0:
        nfa = MatchSubtract(nfa, MatchLength(-start, -start), from_right=True, negate=True)
    # slice off end
    if end is not None:
        if end >= 0:
            assert end >= start >= 0
            nfa = MatchSubtract(nfa, MatchLength(end - start, end - start), from_right=False, negate=True)
        else:
            assert start >= 0 or end >= start
            nfa = MatchSubtract(nfa, MatchLength(-end, -end), from_right=True, negate=False)
    # expand transitions by step-count-minus-one
    if step > 1:

        def expand_steps(nfa: NFA, states: Set[State], n: int) -> Tuple[Set[State], bool]:
            hit_end = False
            for _ in range(n):
                states = nfa.expand_epsilons(states)
                hit_end |= nfa.end in states
                states = {t for s in states for (r, i), ts in nfa.transitions.items() if r == s and i != Move.EMPTY for t in ts}
            return states, hit_end

        transitions: Transitions = {}
        for (s, i), ts in nfa.transitions.items():
            if i == Move.EMPTY:
                transitions[(s, i)] = ts
            else:
                next_states, hit_end = expand_steps(nfa, ts, step - 1)
                transitions[(s, i)] = next_states
                if hit_end:
                    transitions[(s, i)].add(nfa.end)
        nfa = NFA(nfa.start, nfa.end, transitions)
        nfa.remove_redundant_states()
    return nfa


# Patterns
def op_reduce(l):
    if len(l) == 1:
        return l[0]
    else:
        return op_reduce([l[1](l[0], l[2]), *l[3:]])


class Pattern:
    """Regex-style pattern supporting novel spatial operators and modifiers."""

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.nfa = self.expr.parseString(pattern, parseAll=True)[0]

    def __repr__(self):
        return f"Pattern({self.pattern!r})"

    def match(self, string: str) -> bool:
        return self.nfa.match(string)

    def example(self, min_length: int = 0, max_length: Optional[int] = None) -> str:
        return self.nfa.example(min_length, max_length)

    # parsing (TODO: should really go via an AST here)
    from pyparsing import Forward, Group, Literal, OneOrMore, Optional, ParserElement, Word, alphanums, alphas, infixNotation, nums, oneOf, opAssoc  # type: ignore

    ParserElement.setDefaultWhitespaceChars("")
    ParserElement.enablePackrat()

    # TODO: character escaping, supported scripts?
    _0_to_99 = Word(nums, min=1, max=2).setParseAction(lambda t: int("".join(t[0])))
    _m99_to_99 = (Optional("-") + _0_to_99).setParseAction(lambda t: t[-1] * (-1 if len(t) == 2 else 1))
    _id = Word(alphas + "_", alphanums + "_")

    characters = alphanums + " '"
    literal = Word(characters, exact=1).setParseAction(lambda t: MatchIn(t[0]))
    dot = Literal(".").setParseAction(lambda t: MatchNotIn(""))
    set = ("[" + Word(characters, min=1) + "]").setParseAction(lambda t: MatchIn(t[1]))
    nset = ("[^" + Word(characters, min=1) + "]").setParseAction(lambda t: MatchNotIn(t[1]))
    words = Literal(r"\w").setParseAction(lambda t: DICTIONARY_FSM)
    fsm = Literal(r"\f").setParseAction(lambda t: EXPLICIT_FSM)

    expr = Forward()
    group = (
        ("(" + expr + ")").setParseAction(lambda t: t[1])
        | ("(?D:" + expr + ")").setParseAction(lambda t: MatchDFA(t[1], negate=False))
        | ("(?M:" + expr + ")").setParseAction(lambda t: MatchDFA(MatchReversed(MatchDFA(MatchReversed(t[1]), negate=False)), negate=False))
        | ("(?i:" + expr + ")").setParseAction(lambda t: MatchInsensitively(t[1]))
        | ("(?r:" + expr + ")").setParseAction(lambda t: MatchReversed(t[1]))
        | ("(?s" + _m99_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchShifted(t[3], t[1]))
        | ("(?s:" + expr + ")").setParseAction(lambda t: MatchEither(*[MatchShifted(t[1], i) for i in range(1, 26)]))
        | ("(?R" + _m99_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchRotated(t[3], t[1]))
        | ("(?R<=" + _0_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchEither(*[MatchRotated(t[3], i) for i in range(-t[1], t[1] + 1) if i != 0]))
        | (
            "(?S:" + expr + ")[" + Optional(_m99_to_99, None) + ":" + Optional(_m99_to_99, None) + Optional(":" + Optional(_m99_to_99, 1), 1) + "]"
        ).setParseAction(lambda t: MatchSlice(t[1], t[3], t[5], t[-2]))
        | ("(?/" + expr + "/" + expr + "/" + expr + "/" + Optional("s") + ")").setParseAction(
            lambda t: MatchSubtractInside(t[1], t[3], proper=(t[7] == "s"), replace=t[5])
        )
        | ("(?&" + _id + "=" + expr + ")").setParseAction(lambda t: SUBPATTERNS.update({t[1]: t[3]}) or MatchEmpty())
        | ("(?&" + _id + ")").setParseAction(lambda t: SUBPATTERNS[t[1]])
    )
    atom = literal | dot | set | nset | words | fsm | group
    item = (
        (atom + "+").setParseAction(
            lambda t: MatchRepeated(
                t[0],
                repeat=True,
            )
        )
        | (atom + "*").setParseAction(lambda t: MatchRepeated(t[0], repeat=True, optional=True))
        | (atom + "?").setParseAction(lambda t: MatchRepeated(t[0], optional=True))
        | (atom + "{" + _0_to_99 + "}").setParseAction(lambda t: MatchRepeatedN(t[0], t[2], int(t[2])))
        | (atom + "{" + _0_to_99 + ",}").setParseAction(lambda t: MatchRepeatedNplus(t[0], t[2]))
        | (atom + "{" + _0_to_99 + "," + _0_to_99 + "}").setParseAction(lambda t: MatchRepeatedN(t[0], t[2], t[4]))
        | ("¬" + atom).setParseAction(lambda t: MatchDFA(t[1], negate=True))
        | atom
    )
    items = OneOrMore(item).setParseAction(lambda t: reduce(MatchAfter, t))

    spatial_ops = (
        # conjunction
        Literal(">>").setParseAction(lambda _: lambda x, y: MatchContains(x, y, proper=True))
        | Literal(">").setParseAction(lambda _: lambda x, y: MatchContains(x, y, proper=False))
        | Literal("<<").setParseAction(lambda _: lambda x, y: MatchContains(y, x, proper=True))
        | Literal("<").setParseAction(lambda _: lambda x, y: MatchContains(y, x, proper=False))
        | Literal("^^").setParseAction(lambda _: lambda x, y: MatchInterleaved(x, y, proper=True))
        | Literal("^").setParseAction(lambda _: lambda x, y: MatchInterleaved(x, y, proper=False))
        | Literal("##").setParseAction(lambda _: lambda x, y: MatchAlternating(x, y, ordered=True))
        | Literal("#").setParseAction(lambda _: lambda x, y: MatchAlternating(x, y, ordered=False))
        |
        # subtraction
        Literal("->>").setParseAction(lambda _: lambda x, y: MatchSubtractInside(x, y, proper=True))
        | Literal("->").setParseAction(lambda _: lambda x, y: MatchSubtractInside(x, y, proper=False))
        | Literal("-<<").setParseAction(lambda _: lambda x, y: MatchSubtractOutside(x, y, proper=True))
        | Literal("-<").setParseAction(lambda _: lambda x, y: MatchSubtractOutside(x, y, proper=False))
        | Literal("-##").setParseAction(lambda _: lambda x, y: MatchSubtractAlternating(x, y, ordered=True, from_right=True))
        | Literal("_-##").setParseAction(lambda _: lambda x, y: MatchSubtractAlternating(x, y, ordered=True, from_right=False))
        | Literal("-#").setParseAction(lambda _: lambda x, y: MatchSubtractAlternating(x, y, ordered=False))
        | Literal("-^^").setParseAction(lambda _: lambda x, y: MatchSubtractInterleaved(x, y, proper=True, from_right=True))
        | Literal("_-^^").setParseAction(lambda _: lambda x, y: MatchSubtractInterleaved(x, y, proper=True, from_right=False))
        | Literal("-^").setParseAction(lambda _: lambda x, y: MatchSubtractInterleaved(x, y, proper=False))
        | Literal("-").setParseAction(lambda _: lambda x, y: MatchSubtract(x, y, from_right=True, negate=False))
        | Literal("_-").setParseAction(lambda _: lambda x, y: MatchSubtract(x, y, from_right=False, negate=False))
    )
    expr <<= infixNotation(
        items,
        [
            ("&", 2, opAssoc.LEFT, lambda t: reduce(MatchBoth, t[0][::2])),
            (spatial_ops, 2, opAssoc.LEFT, lambda t: op_reduce(t[0])),
            ("|", 2, opAssoc.LEFT, lambda t: MatchEither(*t[0][::2])),
        ],
    )


# Regex reconstructions (extra hacky)
# TODO: simplification, repetition


class Regex(ABC):
    @abstractmethod
    def members(self) -> Any:
        """Members, used for equality testing."""

    @abstractmethod
    def to_string(self) -> str:
        """Regex string representation."""

    @abstractmethod
    def min_length(self) -> float:
        """Minimum match length (-inf for no match)."""

    @abstractmethod
    def max_length(self) -> float:
        """Maximum match length (-inf for no match, inf for infinite)."""

    def __repr__(self):
        return f"{self.to_string()}"

    def __eq__(self, other):
        if type(other) is type(self):
            return self.members() == other.members()
        elif isinstance(other, Regex):
            return False
        else:
            return NotImplemented

    def __hash__(self):
        return hash((type(self), self.members()))

    def __add__(self, other):
        if isinstance(other, Regex):
            return RegexUnion(self, other)
        else:
            raise NotImplemented


class RegexEmpty(Regex):
    def members(self):
        return ()

    def to_string(self):
        return ""  # should only appear by itself

    def min_length(self):
        return 0

    def max_length(self):
        return 0


class RegexChars(Regex):
    def __new__(cls, chars):
        if not chars:
            return RegexUnion()
        return super().__new__(cls)

    def __init__(self, chars):
        self.chars = "".join(sorted(set(chars)))

    def members(self):
        return self.chars

    def to_string(self):
        return self.chars if len(self.chars) == 1 else f"[{self.chars}]"  # TODO: escape when needed

    def min_length(self):
        return 1

    def max_length(self):
        return 1


class RegexNegatedChars(Regex):
    def __init__(self, chars):
        self.chars = "".join(sorted(set(chars)))

    def members(self):
        return self.chars

    def to_string(self, brackets=False):
        return "." if not self.chars else f"[^{self.chars}]"  # TODO: escape when needed

    def min_length(self):
        return 1

    def max_length(self):
        return 1


class RegexStar(Regex):
    regex: Regex

    def __new__(cls, regex: Regex):
        if isinstance(regex, RegexEmpty) or isinstance(regex, RegexStar):
            return regex
        elif regex == RegexUnion():
            return RegexEmpty()
        elif isinstance(regex, RegexUnion) and RegexEmpty() in regex.regexes:
            regex = RegexUnion(*[r for r in regex.regexes if r != RegexEmpty()])
        elif isinstance(regex, RegexConcat) and all(isinstance(r, RegexStar) for r in regex.regexes):
            regex = RegexUnion(cast(RegexStar, r).regex for r in regex.regexes)
        obj = super().__new__(cls)
        obj.regex = regex
        return obj

    def members(self):
        return self.regex

    def to_string(self):
        return f"{self.regex}*"

    def min_length(self):
        return 0

    def max_length(self):
        return 0 if self.regex.max_length() == 0 else math.inf


class RegexUnion(Regex):
    regexes: Tuple[Regex]

    def __new__(cls, *regexes):
        all_ = {r for x in (r.regexes if isinstance(r, RegexUnion) else [r] for r in regexes) for r in x}
        regexes = set()
        # Merge character classes
        if any(isinstance(r, RegexNegatedChars) for r in all_):
            regexes.add(
                RegexNegatedChars(
                    set.intersection(*[set(r.chars) for r in all_ if isinstance(r, RegexNegatedChars)])
                    - {c for r in all_ if isinstance(r, RegexChars) for c in r.chars}
                )
            )
        elif any(isinstance(r, RegexChars) for r in all_):
            chars = {c for r in all_ if isinstance(r, RegexChars) for c in r.chars}
            if chars:
                regexes.add(RegexChars(chars))
        # Don't include epsilon if there's a star already
        if RegexEmpty() in all_ and not (any(isinstance(r, RegexStar) for r in all_)):
            regexes.add(RegexEmpty())
        # Add the rest...
        regexes |= {r for r in all_ if all(not (isinstance(r, c)) for c in (RegexNegatedChars, RegexChars, RegexEmpty))}

        # TODO: apply distributivity
        # AB + AC + AD = A(B+C+D) and ditto for rhs
        # AB + AC + A = A(B+C)? and ditto for rhs

        if len(regexes) == 1:
            return first(regexes)
        obj = super().__new__(cls)
        obj.regexes = tuple(regexes)
        return obj

    def members(self):
        return self.regexes

    def to_string(self):
        if not self.regexes:
            return "∅"

        def debracket(r, optional=False):
            s = str(r)
            if optional:
                return s + "?"
            return s[1:-1] if s.startswith("(") else s

        has_empty = RegexEmpty() in self.regexes
        regexes = [debracket(r, i == 0 and has_empty) for i, r in enumerate(r for r in self.regexes if r != RegexEmpty())]
        return "({})".format("|".join(regexes))

    def min_length(self):
        return -math.inf if not self.regexes else min(*[r.min_length() for r in self.regexes])

    def max_length(self):
        return -math.inf if not self.regexes else max(*[r.max_length() for r in self.regexes])


class RegexConcat(Regex):
    regexes: Tuple[Regex]

    def __new__(cls, *regexes):
        if any(r == RegexUnion() for r in regexes):
            return RegexUnion()
        regexes = tuple(r for x in (r.regexes if isinstance(r, RegexConcat) else [r] for r in regexes) for r in x if not isinstance(r, RegexEmpty))

        if len(regexes) == 1:
            return first(regexes)
        elif len(regexes) == 0:
            return RegexEmpty()
        obj = super().__new__(cls)
        obj.regexes = regexes
        return obj

    def members(self):
        return self.regexes

    def to_string(self):
        # TODO: replace AA* or A*A by A+ (but what about A B (AB)* ?)
        return "({})".format("".join(map(str, self.regexes)))

    def min_length(self):
        return sum(r.min_length() for r in self.regexes)

    def max_length(self):
        return sum(r.max_length() for r in self.regexes)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=r"""NFA-based pattern matcher supporting novel spatial conjunction and modifiers.
Supported syntax:

CHARACTERS
- a        character literal
- .        wildcard character
- [abc]    character class
- [^abc]   negated character class

LOGICAL OPERATORS
- P|Q      P or Q
- ¬P       not P
- P&Q      P and Q
- (P)      scope and precedence

QUANTIFIERS
- P?       0 or 1 occurences
- P*       0 or more occurences
- P+       1 or more occurences
- P{n}     n occurences
- P{n,}    n or more occurences
- P{m,n}   m to n occurences

SEPARATING OPERATORS
- PQ       concatenation
- P<Q      P inside Q
- P<<Q     P strictly inside Q
- P>Q      P outside Q
- P>>Q     P strictly outside Q
- P^Q      P interleaved with Q
- P^^Q     P interleaved inside Q
- P#Q      P alternating with Q
- P##Q     P alternating before Q

SUBTRACTION OPERATORS
- P-Q      subtraction on right
- P_-Q     subtraction on left
- P->Q     subtraction inside
- P->>Q    subtraction strictly inside
- P-<Q     subtraction outside
- P-<<Q    subtraction strictly outside
- P-#Q     subtraction alternating
- P-##Q    subtraction alternating after
- P_-##Q   subtraction alternating before
- P-^Q     subtraction interleaved
- P-^^Q    subtraction interleaved inside
- P_-^^Q   subtraction interleaved outside

OTHER MODIFIERS
- (?i:P)        case-insensitive match
- (?r:P)        reversed match
- (?sn:P)       cipher-shifted by n characters
- (?s:P)        cipher-shifted by 1 to 25 characters
- (?Rn:P)       rotated by n characters right
- (?R<=n:P)     rotated by 1 to n characters left or right
- (?S:P)[m:n]   sliced match
- (?S:P)[m:n:s] sliced match with step
- (?/P/Q/R/)    replace Q inside P by R
- (?/P/Q/R/s)   replace Q strictly inside P by R
- (?D:P)        convert NFA to DFA
- (?M:P)        convert NFA to minimal DFA

REFERENCES
- (?&ID=P) define subpattern for subsequent use
- (?&ID)   use subpattern
- \w       match word from dictionary file
- \f       match FSM from external file
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("pattern", type=str, help="pattern to compile")
    parser.add_argument("files", type=str, nargs="*", help="filenames to search")
    parser.add_argument("-d", dest="dict", metavar="PATH", type=str, help="dictionary file to use for \\w", default=None)
    parser.add_argument("-f", dest="fsm", metavar="PATH", type=str, help="FSM file to use for \\f", default=None)
    parser.add_argument("-D", dest="DFA", action="store_true", help="convert NFA to DFA", default=None)
    parser.add_argument("-M", dest="min", action="store_true", help="convert NFA to minimal DFA ", default=None)
    parser.add_argument("-i", dest="case_insensitive", action="store_true", help="case insensitive match")
    parser.add_argument("-v", dest="invert", action="store_true", help="invert match")
    parser.add_argument("-s", dest="svg", metavar="NAME", default=None, help="save FSM diagram")
    parser.add_argument("-c", dest="console", action="store_true", help="generate FSM image for console")
    parser.add_argument("-x", dest="example", action="store_true", help="generate an example matching string")
    parser.add_argument("-r", dest="regex", action="store_true", help="generate a standard equivalent regex")
    args = parser.parse_args()
    global DICTIONARY_FSM, EXPLICIT_FSM

    if args.dict:
        logger.info(f"Compiling dictionary from '{args.dict}'")
        DICTIONARY_FSM = MatchDictionary(Path(args.dict))
    if args.fsm:
        logger.info(f"Compiling FSM from '{args.fsm}'")
        EXPLICIT_FSM = ExplicitFSM(Path(args.fsm))

    pattern = args.pattern
    if args.case_insensitive:
        pattern = f"(?i:{pattern})"
    if args.invert:
        pattern = f"!({pattern})"
    if args.min:
        pattern = f"(?M:{pattern})"
    elif args.DFA:
        pattern = f"(?D:{pattern})"

    logger.info(f"Compiling pattern '{pattern}'")
    pattern = Pattern(pattern)

    if args.svg:
        logger.info(f"Rendering NFA diagram to '{args.svg}.dot.svg'")
        pattern.nfa.render(args.svg)

    if args.console:
        logger.info(f"Rendering NFA console diagram to 'console.dot.svg'")
        pattern.nfa.render("fsm_console", console=True)

    if args.example:
        logger.info(f"Example match: {pattern.example()!r}")

    if args.regex:
        regex = pattern.nfa.regex()
        logger.info(f"Equivalent regex: {'^'+str(regex)+'$' if regex!=RegexUnion() else None!r}")
        min_length = regex.min_length()
        max_length = regex.max_length()
        if min_length == -math.inf:
            lengths = None
        elif min_length == max_length:
            lengths = min_length
        elif max_length == math.inf:
            lengths = f"{min_length}+"
        else:
            lengths = f"{min_length}-{max_length}"
        logger.info(f"Match lengths: {lengths}")

    for file in args.files:
        logger.info(f"Matching pattern against '{file}'")
        with open(file, "r", encoding="utf-8") as f:
            for w in f:
                word = w.rstrip("\n")
                if pattern.match(word):
                    print(word, flush=True)


if __name__ == "__main__":
    main()
