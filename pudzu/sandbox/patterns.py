import argparse
import logging
import math
import random
import re
import string
import warnings
from abc import ABC, abstractmethod
from enum import Enum
from functools import lru_cache, reduce
from itertools import groupby, product
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple, Union, cast

import graphviz
from pudzu.utils import first, merge, merge_with
from pyparsing import ParseException
from pyparsing import printables as ascii_printables
from pyparsing import pyparsing_unicode as ppu
from pyparsing import srange

State = Any  # really it's Union[str, Tuple['State']]
Move = Enum("Move", "EMPTY ALL")
Input = Union[str, Move]
Transitions = Dict[Tuple[State, Input], Set[State]]
CaptureGroup = str
Captures = Dict[Tuple[State, Input], Set[CaptureGroup]]
CaptureOutput = Dict[CaptureGroup, str]

logger = logging.getLogger("patterns")

DEBUG = False
DICTIONARY_FSM = None
EXPLICIT_FSM = None
SUBPATTERNS = {}
EXTRA_PRINTABLES = ""
SLOW_SIMPLIFICATION = True


class NFA:
    """Nondeterministic Finite Automata with
    - single start state (with no inbounds) and end state (with no outbounds)
    - ε-moves (including potential ε loops)
    - *-moves (only used if there is no other matching move)
    """

    def __init__(self, start: State, end: State, transitions: Transitions, captures: Optional[Captures] = None):
        self.start = start
        self.end = end
        self.transitions = transitions
        self.captures = captures or {}
        self.states = {self.start, self.end} | {s for s, _ in self.transitions.keys()} | {t for ts in self.transitions.values() for t in ts}

    def __repr__(self) -> str:
        return f"NFA(start={self.start}, end={self.end}, transitions={self.transitions})"

    def match(self, string: str) -> Optional[CaptureOutput]:
        """Match the NFA against a string input. Returns a CaptureOutput if found, or None otherwise."""
        old_states: Dict[State, CaptureOutput] = {self.start: {}}
        for c in string:
            new_states: Dict[State, CaptureOutput] = {}
            for s, co in old_states.items():
                for se in self.expand_epsilons({s}):
                    for t in self.transitions.get((se, c), self.transitions.get((se, Move.ALL), set())):
                        if t not in new_states:
                            cgs = self.captures.get((se, c), set()) if (se, c) in self.transitions else self.captures.get((se, Move.ALL), set())
                            tco = merge(co, {cg: co.get(cg, "") + c for cg in cgs})
                            new_states[t] = tco
            old_states = new_states
        for s, co in old_states.items():
            if self.end in self.expand_epsilons({s}):
                return co
        return None

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

        # remove capture information for trimmed transitions
        self.captures = {(s, i): cs for (s, i), cs in self.captures.items() if (s, i) in self.transitions and i != Move.EMPTY}

        if aggressive:
            # remove states that only go via empty to self.end
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

        # states
        for s in self.states:
            if s == self.start:
                g.node(str(s), root="true", label="", color=fg)
                g.node("prestart", style="invisible")
                g.edge("prestart", str(s), style="bold", color=fg)
            elif s == self.end:
                g.node(str(s), shape="doublecircle", label="", color=fg)
            else:
                g.node(str(s), label="", color=fg)

        # transitions
        reverse_dict: Dict[State, Dict[Tuple[State, FrozenSet[CaptureGroup]], Set[Input]]] = {}
        for (s, i), ts in self.transitions.items():
            if not ts:
                g.node(str(("fail", s)), label="", color=fg)
            for t in ts or {("fail", s)}:
                c = frozenset(self.captures.get((s, i), set()))
                reverse_dict.setdefault(s, {}).setdefault((t, c), set()).add(i)

        for s, d in reverse_dict.items():
            for (t, c), ii in d.items():
                for move in (i for i in ii if isinstance(i, Move)):
                    label = {Move.ALL: "*", Move.EMPTY: "ε"}[move]
                    if c:
                        label += f" {{{','.join(c)}}}"
                    g.edge(str(s), str(t), label=label, color=fg, fontcolor=fg)
                input = "".join(sorted(i for i in ii if isinstance(i, str)))
                if len(input) >= 1:
                    label = "SPACE" if input == " " else char_class(input)
                    if c:
                        label += f" {{{','.join(c)}}}"
                    g.edge(str(s), str(t), label=label, color=fg, fontcolor=fg)

        g.render(filename=name + ".dot")

    def save(self, name: str, renumber_states: bool = True) -> None:
        """Save FSM as a .fsm file."""
        # TODO: save and load capture groups

        def sort_key(s):
            # Q: is there a better state ordering?
            return "" if s == self.start else ")" if s == self.end else str(s)

        sorted_states = sorted(self.states, key=sort_key)

        def label(s):
            return (
                "START"
                if s == self.start
                else "END"
                if s == self.end
                else str(sorted_states.index(s))
                if renumber_states
                else str(s).replace("'", "").replace(" ", "")
            )

        with open(name + ".fsm", "w", encoding="utf-8") as f:
            reverse_dict: Dict[State, Dict[FrozenSet[State], Set[Input]]] = {}
            for (s, i), ts in self.transitions.items():
                reverse_dict.setdefault(s, {}).setdefault(frozenset(ts), set()).add(i)
            for state in sorted_states:
                from_label = label(state)
                for fts, ii in reverse_dict.get(state, {}).items():
                    to_labels = " ".join(label(t) for t in fts)
                    for move in (i for i in ii if isinstance(i, Move)):
                        print(f"{from_label} {str(move).replace('Move.','')} {to_labels}", file=f)
                    input = "".join(sorted(i for i in ii if isinstance(i, str)))
                    if len(input) >= 1:
                        input_label = "SPACE" if input == " " else char_class(input)
                        print(f"{from_label} {input_label} {to_labels}", file=f)

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
                    # TODO: match with supported scripts?
                    options = list(set(string.ascii_letters + string.digits + " '") - set(i for i in choices if isinstance(i, str)))
                    output += random.choice(options)
                elif isinstance(i, str):
                    output += i
                state = random.choice(list(nfa.transitions[(state, i)]))
        except IndexError:
            return None
        return output

    def bound(self, lower_bound: bool, max_length: int) -> Optional[str]:
        """Generate a lower/upper lexicographic bound for the FSM."""
        bound = ""
        minmax = min if lower_bound else max
        states = self.expand_epsilons({self.start})
        while (not lower_bound or self.end not in states) and len(bound) < max_length:
            least_char = None
            next_state = None
            for state in states:
                least_trans = minmax([i for (s, i), ts in self.transitions.items() if s == state and ts and isinstance(i, str)], default=None)
                if least_trans and (not least_char or least_trans == minmax((least_trans, least_char))):
                    least_char, next_state = least_trans, first(self.transitions[(state, least_trans)])
                if self.transitions.get((state, Move.ALL)):
                    # TODO: match with supported scripts?
                    least_any = minmax(set(ascii_printables + " ") - {i for (s, i) in self.transitions if s == state})
                    if not least_char or least_any == minmax((least_any, least_char)):
                        least_char, next_state = least_any, first(self.transitions[(state, Move.ALL)])
            if not least_char:
                break
            bound += least_char
            states = self.expand_epsilons({next_state})
        else:
            if not lower_bound:
                bound = bound[:-1] + chr(ord(bound[-1]) + 1)

        return bound

    def regex(self) -> "Regex":
        """Generate a regex corresponding to the NFA."""
        L = {(i, j): RegexConcat() if i == j else RegexUnion() for i in self.states for j in self.states}
        for (i, a), js in self.transitions.items():
            for j in js:
                if a == Move.ALL:
                    L[i, j] |= RegexNegatedChars("".join(b for k, b in self.transitions if i == k and isinstance(b, str)))
                elif a == Move.EMPTY:
                    L[i, j] |= RegexConcat()
                else:
                    L[i, j] |= RegexChars(a)
        remaining = set(self.states)
        for k in self.states:
            if k == self.start or k == self.end:
                continue
            remaining.remove(k)
            for i in remaining:
                for j in remaining:
                    L[i, i] |= RegexConcat((L[i, k], RegexStar(L[k, k]), L[k, i]))
                    L[j, j] |= RegexConcat((L[j, k], RegexStar(L[k, k]), L[k, j]))
                    L[i, j] |= RegexConcat((L[i, k], RegexStar(L[k, k]), L[k, j]))
                    L[j, i] |= RegexConcat((L[j, k], RegexStar(L[k, k]), L[k, i]))

        return L[self.start, self.end]

    def min_length(self) -> Optional[int]:
        """ The minimum possible length match. """
        # use Dijkstra to find shortest path
        unvisited = set(self.states)
        distances = {s: 0 if s == self.start else math.inf for s in self.states}
        current = self.start
        while current in unvisited:
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
        return None

    def max_length(self) -> Optional[int]:
        """ The maximum possible length match. """
        # converts to a regex, though there's probably a more efficient way
        max_length = self.regex().max_length()
        return int(max_length) if math.isfinite(max_length) else None


def char_class(chars: str, negated: bool = False) -> str:
    """Generate a character class description of the given characters"""
    if len(chars) == 0 and negated:
        return "."
    elif len(chars) == 1:
        if negated or chars in Pattern.literal_exclude:
            return f"[{'^'*negated}{chars}]"
        return chars

    # find runs of length 4+
    ordered = sorted(set(chars))
    runs, i = [], 0
    ords = [ord(c) - i for i, c in enumerate(ordered)]
    for _, g in groupby(ords):
        n = len([*g])
        runs += ordered[i : i + n] if n < 4 else [ordered[i] + "-" + ordered[i + n - 1]]
        i += n

    # order things to minimise likelihood of having to escape anything
    def sort_key(r):
        if "]" in r:
            return 0
        if "-" in r[::2]:
            return 1 if r[0] == "-" and "]" not in ordered else 4
        if "^" in r:
            return 3
        else:
            return 2

    runs.sort(key=lambda s: sort_key(s))

    # TODO: escape -^\] when needed once we can parse that
    return f"[{'^'*negated}{''.join(runs)}]"


# pylint: disable=unbalanced-tuple-unpacking
def new_states(*names: str) -> List[Callable[..., State]]:
    """Return functions for generating new state names using the given labels.
    Note that names are sorted alphabetically when generating FSM descriptions."""
    generators = []
    for name in names:
        generators.append((lambda name: (lambda *args: (name, *args) if args else name))(name))
    return generators


# NFA constructors
def merge_trans(*args):
    """Merge multiple transitions, unioning target states."""
    return merge_with(lambda x: set.union(*x), *args)


def MatchEmpty() -> NFA:
    """Empty match"""
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
    r"""Handles: \w"""
    with open(str(path), "r", encoding="utf-8") as f:
        return MatchWords(w.rstrip("\n") for w in f)


def ExplicitFSM(path: Path) -> NFA:
    r"""Handles: \f"""
    transitions: Transitions = {}
    with open(str(path), "r", encoding="utf-8") as f:
        for line in f:
            args = line.split()
            if args:
                x: Input
                start, x, *end = args
                if start == "END":
                    raise ValueError("END state should have no outbound arrows")
                elif "START" in end:
                    raise ValueError("START state should have no inbound arrows")
                elif x == "SPACE":
                    x = " "
                if re.match(r"^\[\^.+]$", x):
                    transitions.setdefault((start, Move.ALL), set()).update(end)
                    for x in srange(x):
                        transitions.setdefault((start, x), set())
                elif re.match(r"^\[.+]$", x):
                    for x in srange(x):
                        transitions.setdefault((start, x), set()).update(end)
                elif x in {"EMPTY", "ALL"}:
                    x = {"EMPTY": Move.EMPTY, "ALL": Move.ALL}[x]
                    transitions.setdefault((start, x), set()).update(end)
                elif len(x) > 1:
                    raise ValueError(f"Unexpected FSM input `{x}`: should be character, class, ALL or EMPTY")
                else:
                    transitions.setdefault((start, x), set()).update(end)
    return NFA("START", "END", transitions)


def MatchCapture(nfa: NFA, id: CaptureGroup) -> NFA:
    """Handles: (?<id>A)"""
    captures = {(s, i): {id} for (s, i) in nfa.transitions if i != Move.EMPTY}
    return NFA(nfa.start, nfa.end, nfa.transitions, merge_trans(nfa.captures, captures))


def MatchAfter(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: AB"""
    First, Second = new_states("a", "b")
    t1 = {(First(s), i): {First(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    c1 = {(First(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t2 = {
        (First(nfa1.end) if s == nfa2.start else Second(s), i): {First(nfa1.end) if t == nfa2.start else Second(t) for t in ts}
        for (s, i), ts in nfa2.transitions.items()
    }
    c2 = {(First(nfa1.end) if s == nfa2.start else Second(s), i): cs for (s, i), cs in nfa2.captures.items()}
    return NFA(First(nfa1.start), Second(nfa2.end), merge_trans(t1, t2), merge_trans(c1, c2))


def MatchEither(*nfas: NFA) -> NFA:
    """Handles: A|B (and arbitrary alternation too)"""
    Start, End, *Option = new_states("a", "z", *[str(n) for n in range(1, len(nfas) + 1)])
    tis, cis = [], []
    for n, nfa in enumerate(nfas):
        tis.append({(Option[n](s), i): {Option[n](t) for t in ts} for (s, i), ts in nfa.transitions.items()})
        cis.append({(Option[n](s), i): cs for (s, i), cs in nfa.captures.items()})
    tstart = {(Start(), Move.EMPTY): {Option[n](nfa.start) for n, nfa in enumerate(nfas)}}
    tend = {(Option[n](nfa.end), Move.EMPTY): {End()} for n, nfa in enumerate(nfas)}
    return NFA(Start(), End(), merge_trans(tstart, tend, *tis), merge_trans(*cis))


def MatchRepeated(nfa: NFA, repeat: bool = False, optional: bool = False) -> NFA:
    """Handles: A*, A+, A?"""
    Start, End, Star = new_states("a", "z", "*")
    transitions: Transitions = {(Star(s), i): {Star(t) for t in ts} for (s, i), ts in nfa.transitions.items()}
    captures: Captures = {(Star(s), i): cs for (s, i), cs in nfa.captures.items()}
    transitions[(Start(), Move.EMPTY)] = {Star(nfa.start)}
    if optional:
        transitions[(Start(), Move.EMPTY)].add(End())
    transitions[(Star(nfa.end), Move.EMPTY)] = {End()}
    if repeat:
        transitions[(Star(nfa.end), Move.EMPTY)].add(Star(nfa.start))
    return NFA(Start(), End(), transitions, captures)


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
    if nfa.captures and not negate:
        raise NotImplementedError("Cannot convert NFA with submatch captures to a DFA")

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
    captures: Captures = {}
    for (s1, i), ts1 in nfa1.transitions.items():
        for s2 in nfa2.states:
            if i == Move.EMPTY:
                transitions = merge_trans(transitions, {((s1, s2), i): set(product(ts1, {s2}))})
            else:
                ts2 = nfa2.transitions.get((s2, i), nfa2.transitions.get((s2, Move.ALL)))
                if ts2 is not None:
                    transitions = merge_trans(transitions, {((s1, s2), i): set(product(ts1, ts2))})
                    cs2 = nfa1.captures.get((s1, i), set()) | nfa2.captures.get((s2, i), nfa2.captures.get((s2, Move.ALL), set()))
                    if cs2:
                        captures = merge_trans(captures, {((s1, s2), i): cs2})
    for (s2, i), ts2 in nfa2.transitions.items():
        for s1 in nfa1.states:
            if i == Move.EMPTY:
                transitions = merge_trans(transitions, {((s1, s2), i): set(product({s1}, ts2))})
            elif (s1, i) not in nfa1.transitions:  # (as we've done those already!)
                ts1o = nfa1.transitions.get((s1, Move.ALL))
                if ts1o is not None:
                    transitions = merge_trans(transitions, {((s1, s2), i): set(product(ts1o, ts2))})
                    cs1o = nfa2.captures.get((s2, i), set()) | nfa1.captures.get((s1, Move.ALL), set())
                    if cs1o:
                        captures = merge_trans(captures, {((s1, s2), i): cs1o})
    if start_from:
        transitions[("1", Move.EMPTY)] = start_from
    if stop_at:
        transitions = merge_trans(transitions, {(s, Move.EMPTY): {"2"} for s in stop_at})
    nfa = NFA("1" if start_from else (nfa1.start, nfa2.start), "2" if stop_at else (nfa1.end, nfa2.end), transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchContains(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A<B, A<<B, A>B, A>>B"""
    # transition from (2) A to (3) AxB to (5) A states
    # for proper containment, also use (1) A and (4) A states
    LeftFirst, Left, Middle, RightFirst, Right = new_states("<l1", "<l2", "<m", "<r1", "<r2")
    t1, t1e, c1, t4, t4e, c4 = {}, {}, {}, {}, {}, {}
    if proper:
        t1 = {(LeftFirst(s), i): {LeftFirst(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(LeftFirst(s), i): {Left(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        c1 = {(LeftFirst(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t2 = {(Left(s), i): {Left(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    c2 = {(Left(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t2e = {(Left(s), Move.EMPTY): {Middle(s, nfa2.start)} for s in nfa1.states}
    t3 = {(Middle(s, q), i): {Middle(s, t) for t in ts} for (q, i), ts in nfa2.transitions.items() for s in nfa1.states}
    c3 = {(Middle(s, q), i): cs for (q, i), cs in nfa2.captures.items() for s in nfa1.states}
    t3e = {(Middle(s, nfa2.end), Move.EMPTY): {(RightFirst(s) if proper else Right(s))} for s in nfa1.states}
    if proper:
        t4 = {(RightFirst(s), i): {RightFirst(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t4e = {(RightFirst(s), i): {Right(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        c4 = {(RightFirst(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t5 = {(Right(s), i): {Right(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    c5 = {(Right(s), i): cs for (s, i), cs in nfa1.captures.items()}
    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e, t5)
    captures = merge_trans(c1, c2, c3, c4, c5)
    nfa = NFA(LeftFirst(nfa1.start) if proper else Left(nfa1.start), Right(nfa1.end), transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchInterleaved(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A^B, A^^B"""
    # transition between (2) AxB and (3) AxB states
    # for proper interleaving, also use (1) A and (4) A states
    First, Left, Right, Last = new_states("^a", "^l", "^r", "^z")
    t1, t1e, c1, t4, t4e, c4 = {}, {}, {}, {}, {}, {}
    if proper:
        t1 = {(First(s), i): {First(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(First(s), i): {Left(t, nfa2.start) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        c1 = {(First(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t2 = {(Left(s, q), i): {Left(t, q) for t in ts} for (s, i), ts in nfa1.transitions.items() for q in nfa2.states}
    c2 = {(Left(s, q), i): cs for (s, i), cs in nfa1.captures.items() for q in nfa2.states}
    t2e = {(Left(q, s), Move.EMPTY): {Right(q, s)} for q in nfa1.states for s in nfa2.states}
    t3 = {(Right(q, s), i): {Right(q, t) for t in ts} for (s, i), ts in nfa2.transitions.items() for q in nfa1.states}
    c3 = {(Right(q, s), i): cs for (s, i), cs in nfa2.captures.items() for q in nfa1.states}
    t3e = {(Right(q, s), Move.EMPTY): {Left(q, s)} for q in nfa1.states for s in nfa2.states}
    if proper:
        t4 = {(Left(s, nfa2.end), i): {Last(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        c4 = {(Left(s, nfa2.end), i): cs for (s, i), cs in nfa1.captures.items()}
        t4e = {(Last(s), i): {Last(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e)
    captures = merge_trans(c1, c2, c3, c4)
    nfa = NFA(First(nfa1.start) if proper else Left(nfa1.start, nfa2.start), Last(nfa1.end) if proper else Right(nfa1.end, nfa2.end), transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchAlternating(nfa1: NFA, nfa2: NFA, ordered: bool) -> NFA:
    """Handles: A#B, A##B"""
    # transition between (1) AxB and (2) AxB states
    # for order agnostic alternation, also use an additional (0) start state
    Start, Left, Right = new_states("#a", "#l", "#r")
    t0 = {(Start(), Move.EMPTY): {Left(nfa1.start, nfa2.start), Right(nfa1.start, nfa2.start)}} if not ordered else {}
    t1 = {(Left(s, q), i): {(Left if i == Move.EMPTY else Right)(t, q) for t in ts} for (s, i), ts in nfa1.transitions.items() for q in nfa2.states}
    c1 = {(Left(s, q), i): cs for (s, i), cs in nfa1.captures.items() for q in nfa2.states}
    t2 = {(Right(q, s), i): {(Right if i == Move.EMPTY else Left)(q, t) for t in ts} for (s, i), ts in nfa2.transitions.items() for q in nfa1.states}
    c2 = {(Right(q, s), i): cs for (s, i), cs in nfa2.captures.items() for q in nfa1.states}
    # handle final transitions
    t1e = {(Left(nfa1.end, s), Move.EMPTY): {Left(nfa1.end, t) for t in ts} for (s, i), ts in nfa2.transitions.items() if i == Move.EMPTY}
    t2e = {(Right(s, nfa2.end), Move.EMPTY): {Right(t, nfa2.end) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
    t21 = {(Right(nfa1.end, nfa2.end), Move.EMPTY): {Left(nfa1.end, nfa2.end)}}
    transitions = merge_trans(t0, t1, t1e, t2, t2e, t21)
    captures = merge_trans(c1, c2)
    nfa = NFA(Start() if not ordered else Left(nfa1.start, nfa2.start), Left(nfa1.end, nfa2.end), transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchSubtract(nfa1: NFA, nfa2: NFA, from_right: bool, negate: bool) -> NFA:
    """Handles: A-B, A_-B (and used in slicing)"""
    # rewire end/start state of nfa1 based on partial intersection with nfa2
    Start, Middle, End = new_states("-a", "-m", "-e")
    if from_right:
        both = MatchBoth(nfa1, nfa2, start_from={(a, nfa2.start) for a in nfa1.states})
    else:
        both = MatchBoth(nfa1, nfa2, stop_at={(a, nfa2.end) for a in nfa1.states})
    if negate:
        return both
    transitions: Transitions = {(Middle(s), i): {Middle(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    captures: Captures = {(Middle(s), i): cs for (s, i), cs in nfa1.captures.items()}
    if from_right:
        midpoints = {a for a, _ in both.transitions.get((both.start, Move.EMPTY), set())}
        transitions = merge_trans(transitions, {(Middle(s), Move.EMPTY): {End()} for s in midpoints})
        nfa = NFA(Middle(nfa1.start), End(), transitions, captures)
    else:
        midpoints = {a for ((a, b), i), cs in both.transitions.items() if i == Move.EMPTY and both.end in cs}
        transitions[(Start(), Move.EMPTY)] = {Middle(s) for s in midpoints}
        nfa = NFA(Start(), Middle(nfa1.end), transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchSubtractInside(nfa1: NFA, nfa2: NFA, proper: bool, replace: Optional[NFA] = None) -> NFA:
    """Handles: A->B, A->>B"""
    # like MatchContains, but link (2) and (4)/(5) using partial intersection
    LeftFirst, Left, Replace, RightFirst, Right = new_states("->l1", "->l2", "->m", "->r1", "->r2")
    t1, t1e, c1, t3, c3, t3e, t4, t4e, c4 = {}, {}, {}, {}, {}, {}, {}, {}, {}
    if proper:
        t1 = {(LeftFirst(s), i): {LeftFirst(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(LeftFirst(s), i): {Left(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        c1 = {(LeftFirst(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t2 = {(Left(s), i): {Left(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    c2 = {(Left(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t2es = []
    if replace:
        t3 = {(Replace(s, q), i): {Replace(s, t) for t in ts} for (q, i), ts in replace.transitions.items() for s in nfa1.states}
        c3 = {(Replace(s, q), i): cs for (q, i), cs in replace.captures.items() for s in nfa1.states}
        t3e = {(Replace(s, replace.end), Move.EMPTY): {(RightFirst(s) if proper else Right(s))} for s in nfa1.states}
    for s in nfa1.states:
        both = MatchBoth(nfa1, nfa2, start_from={(s, nfa2.start)}, stop_at={(a, nfa2.end) for a in nfa1.states})
        new_end = {a for a, _ in both.transitions.get((both.start, Move.EMPTY), set())}
        new_start = {a[0] for (a, i), cs in both.transitions.items() if i == Move.EMPTY and both.end in cs}
        t2es.append(
            {(Left(e), Move.EMPTY): {(Replace(s, replace.start) if replace else RightFirst(s) if proper else Right(s)) for s in new_start} for e in new_end}
        )
    if proper:
        t4 = {(RightFirst(s), i): {RightFirst(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t4e = {(RightFirst(s), i): {Right(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        c4 = {(RightFirst(s), i): cs for (s, i), cs in nfa1.captures.items()}
    t5 = {(Right(s), i): {Right(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
    c5 = {(Right(s), i): cs for (s, i), cs in nfa1.captures.items()}
    transitions = merge_trans(t1, t1e, t2, *t2es, t3, t3e, t4, t4e, t5)
    captures = merge_trans(c1, c2, c3, c4, c5)
    nfa = NFA(LeftFirst(nfa1.start) if proper else Left(nfa1.start), Right(nfa1.end), transitions, captures)
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
        Start, Middle, End = new_states("-<a", "-<m", "-<z")
        transitions: Transitions = {(Middle(s), i): {Middle(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
        captures: Captures = {(Middle(s), i): cs for (s, i), cs in nfa1.captures.items()}
        transitions[Start(), Move.EMPTY] = {Middle(a) for a, b in both_start_end if b == m}
        for a in {a for a, b in both_end_start if b == m}:
            transitions.setdefault((Middle(a), Move.EMPTY), set()).add(End())
        nfa = NFA(Start(), End(), transitions, captures)
        nfa.remove_redundant_states()
        nfas.append(nfa)
    return MatchEither(*nfas)


def MatchSubtractAlternating(nfa1: NFA, nfa2: NFA, ordered: bool, from_right: bool = True) -> NFA:
    """Handles: A-#B, A_-#B, A-##B"""
    # Expand transitions in A with one from A&B (tracking both A and B states)
    both = MatchBoth(nfa1, nfa2, stop_at={(a, b) for a in nfa1.states for b in nfa2.states}, start_from={(a, b) for a in nfa1.states for b in nfa2.states})
    transitions: Transitions = {}
    captures: Captures = {}
    for (s, i), ts in nfa1.transitions.items():
        for b in nfa2.states:
            if i == Move.EMPTY:
                states = {(t, b) for t in ts}
            else:
                ts = nfa1.expand_epsilons(ts)
                states = {u for (r, i), us in both.transitions.items() for t in ts if r == (t, b) and i != Move.EMPTY for u in us}
            transitions[((s, b), i)] = states
            if (s, i) in nfa1.captures:
                captures[((s, b), i)] = nfa1.captures[(s, i)]
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
        nfa = NFA(first(start_state), (nfa1.end, nfa2.end), transitions, captures)
    else:
        transitions[("a", Move.EMPTY)] = start_state
        nfa = NFA("a", (nfa1.end, nfa2.end), transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchSubtractInterleaved(nfa1: NFA, nfa2: NFA, proper: bool, from_right: bool = True) -> NFA:
    """Handles: A-^B, A-^^B, A_-^^B"""
    # Combine transitions from A with empty transitions from A&B (tracking both A and B states)
    both = MatchBoth(nfa1, nfa2, stop_at={(a, b) for a in nfa1.states for b in nfa2.states}, start_from={(a, b) for a in nfa1.states for b in nfa2.states})
    transitions: Transitions = {}
    captures: Captures = {}
    for (a, i), ts in nfa1.transitions.items():
        for b in nfa2.states:
            transitions[(a, b), i] = {(t, b) for t in ts}
            if (a, i) in nfa1.captures:
                captures[(a, b), i] = nfa1.captures[(a, i)]
    for (ab, i), tus in both.transitions.items():
        if ab != both.start:
            transitions.setdefault((ab, Move.EMPTY), set()).update(tus - {both.end})

    if not proper:
        transitions[((nfa1.end, nfa2.end), Move.EMPTY)] = {"z"}
        nfa = NFA((nfa1.start, nfa2.start), "z", transitions, captures)
    elif from_right:
        First, Middle, Last = new_states("-^a", "-^m", "-^z")
        t1 = {(First(s), i): {First(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(First(s), i): {Middle((t, nfa2.start)) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        c1 = {(First(s), i): cs for (s, i), cs in nfa1.captures.items()}
        t2 = {(Middle(s), i): {Middle(t) for t in ts} for (s, i), ts in transitions.items()}
        c2 = {(Middle(s), i): cs for (s, i), cs in captures.items()}
        t2e = {(Middle((s, nfa2.end)), i): {Last(t) for t in ts} for (s, i), ts in nfa1.transitions.items() if i != Move.EMPTY}
        t3 = {(Last(s), i): {Last(t) for t in ts} for (s, i), ts in nfa1.transitions.items()}
        c3 = {(Last(s), i): cs for (s, i), cs in nfa1.captures.items()}
        transitions = merge_trans(t1, t1e, t2, t2e, t3)
        captures = merge_trans(c1, c2, c3)
        nfa = NFA(First(nfa1.start), Last(nfa1.end), transitions, captures)
    else:
        ts = both.expand_epsilons({(nfa1.start, nfa2.start)})
        start_states = {u for (s, i), us in both.transitions.items() if s in ts and i != Move.EMPTY for u in us}
        ts = set()
        for t in both.states:
            if (nfa1.end, nfa2.end) in both.expand_epsilons({t}):
                ts.add(t)
        end_states = {s for (s, i), us in both.transitions.items() if any(u in ts for u in us) and i != Move.EMPTY}

        transitions[("a", Move.EMPTY)] = start_states
        for s in end_states:
            transitions[(s, Move.EMPTY)] = {"z"}
        nfa = NFA("a", "z", transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchReversed(nfa: NFA) -> NFA:
    """Handles: (?r:A)"""
    # just reverse the edges (with special handling for *-transitions)
    transitions: Transitions = {}
    captures: Captures = {}
    (Extra,) = new_states("r")
    for (s, i), ts in nfa.transitions.items():
        for t in ts:
            if i == Move.ALL:
                if any(r != s and t in vs for (r, j), vs in nfa.transitions.items()):
                    extra_state = Extra(s, t)
                    transitions.setdefault((t, Move.EMPTY), set()).add(extra_state)
                    t = extra_state
                for (r, j), _ in nfa.transitions.items():
                    if r == s and not isinstance(j, Move):
                        transitions.setdefault((t, j), set())
            transitions.setdefault((t, i), set()).add(s)
            if (s, i) in nfa.captures:
                captures.setdefault((t, i), set()).update(nfa.captures[(s, i)])
    nfa = NFA(nfa.end, nfa.start, transitions, captures)
    nfa.remove_redundant_states()
    return nfa


def MatchInsensitively(nfa: NFA) -> NFA:
    """Handles: (?i:A)"""
    transitions: Transitions = {}
    captures: Captures = {}
    for (s, i), ts in nfa.transitions.items():
        if isinstance(i, str):
            transitions.setdefault((s, i.lower()), set()).update(ts)
            transitions.setdefault((s, i.upper()), set()).update(ts)
            if nfa.captures.get((s, i), set()):
                captures.setdefault((s, i.lower()), set()).update(nfa.captures.get((s, i), set()))
                captures.setdefault((s, i.upper()), set()).update(nfa.captures.get((s, i), set()))
        else:
            transitions[(s, i)] = ts
    return NFA(nfa.start, nfa.end, transitions, captures)


def MatchShifted(nfa: NFA, shift: int) -> NFA:
    """Handles: (?sn:A)"""
    transitions: Transitions = {}
    captures: Captures = {}
    for (s, i), ts in nfa.transitions.items():
        c = nfa.captures.get((s, i), None)
        for alphabet in (string.ascii_lowercase, string.ascii_uppercase):
            if isinstance(i, str) and i in alphabet:
                i = alphabet[(alphabet.index(i) + shift) % 26]
                break
        transitions[(s, i)] = ts
        if c is not None:
            captures[(s, i)] = c
    return NFA(nfa.start, nfa.end, transitions, captures)


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
            keep = NFA(middle, nfa.end, nfa.transitions, nfa.captures)
            rotated = MatchAfter(keep, move)
            rotated.remove_redundant_states()
            rotations.append(rotated)
    else:
        window = MatchLength(shift, shift)
        intersection = MatchBoth(nfa, window, start_from={(a, window.start) for a in nfa.states})
        intersection_starts = {s[0] for s in intersection.transitions.get((intersection.start, Move.EMPTY), set()) if s[0] != nfa.start}
        for middle in intersection_starts:
            move = MatchBoth(nfa, window, start_from={(middle, window.start)})
            keep = NFA(nfa.start, middle, nfa.transitions, nfa.captures)
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
        captures: Captures = {}
        for (s, i), ts in nfa.transitions.items():
            if i == Move.EMPTY:
                transitions[(s, i)] = ts
            else:
                next_states, hit_end = expand_steps(nfa, ts, step - 1)
                transitions[(s, i)] = next_states
                if (s, i) in nfa.captures:
                    captures[(s, i)] = nfa.captures[(s, i)]
                if hit_end:
                    transitions[(s, i)].add(nfa.end)
        nfa = NFA(nfa.start, nfa.end, transitions, captures)
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

    def match(self, string: str) -> Optional[CaptureOutput]:
        return self.nfa.match(string)

    def example(self, min_length: int = 0, max_length: Optional[int] = None) -> str:
        return self.nfa.example(min_length, max_length)

    # parsing (should really go via an AST here)
    from pyparsing import Forward, Group, Literal, OneOrMore
    from pyparsing import Optional as Option
    from pyparsing import ParserElement, Word, alphanums, alphas, infixNotation, nums, oneOf, opAssoc

    ParserElement.setDefaultWhitespaceChars("")
    ParserElement.enablePackrat()

    # TODO: character escaping, supported scripts
    _0_to_99 = Word(nums, min=1, max=2).setParseAction(lambda t: int("".join(t[0])))
    _m99_to_99 = (Option("-") + _0_to_99).setParseAction(lambda t: t[-1] * (-1 if len(t) == 2 else 1))
    _id = Word(alphas + "_", alphanums + "_")

    printables = ppu.Latin1.printables + " " + EXTRA_PRINTABLES
    literal_exclude = r"()+*.?<>#{}^_&|$\[]-"
    set_exclude = r"\]"

    literal = Word(printables, excludeChars=literal_exclude, exact=1).setParseAction(lambda t: MatchIn(t[0]))
    dot = Literal(".").setParseAction(lambda t: MatchNotIn(""))
    nset = ("[^" + Word(printables, excludeChars=set_exclude, min=1) + "]").setParseAction(lambda t: MatchNotIn(srange(f"[{t[1]}]")))
    set = ("[" + Word(printables, excludeChars=set_exclude, min=1) + "]").setParseAction(lambda t: MatchIn(srange(f"[{t[1]}]")))
    words = Literal(r"\w").setParseAction(lambda t: DICTIONARY_FSM)
    fsm = Literal(r"\f").setParseAction(lambda t: EXPLICIT_FSM)

    expr = Forward()
    group = (
        ("(" + expr + ")").setParseAction(lambda t: t[1])
        | ("(?D:" + expr + ")").setParseAction(lambda t: MatchDFA(t[1], negate=False))
        | ("(?M:" + expr + ")").setParseAction(lambda t: MatchDFA(MatchReversed(MatchDFA(MatchReversed(t[1]), negate=False)), negate=False))
        | ("(?i:" + expr + ")").setParseAction(lambda t: MatchInsensitively(t[1]))
        | ("(?r:" + expr + ")").setParseAction(lambda t: MatchReversed(t[1]))
        | ("(?<" + _id + ">" + expr + ")").setParseAction(lambda t: MatchCapture(t[3], t[1]))
        | ("(?s" + _m99_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchShifted(t[3], t[1]))
        | ("(?s:" + expr + ")").setParseAction(lambda t: MatchEither(*[MatchShifted(t[1], i) for i in range(1, 26)]))
        | ("(?R" + _m99_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchRotated(t[3], t[1]))
        | ("(?R<=" + _0_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchEither(*[MatchRotated(t[3], i) for i in range(-t[1], t[1] + 1) if i != 0]))
        | ("(?S:" + expr + ")[" + Option(_m99_to_99, None) + ":" + Option(_m99_to_99, None) + Option(":" + Option(_m99_to_99, 1), 1) + "]").setParseAction(
            lambda t: MatchSlice(t[1], t[3], t[5], t[-2])
        )
        | ("(?/" + expr + "/" + expr + "/" + expr + "/" + Option("s") + ")").setParseAction(
            lambda t: MatchSubtractInside(t[1], t[3], proper=(t[7] == "s"), replace=t[5])
        )
        | ("(?&" + _id + "=" + expr + ")").setParseAction(lambda t: SUBPATTERNS.update({t[1]: t[3]}) or MatchEmpty())
        | ("(?&" + _id + ")").setParseAction(lambda t: SUBPATTERNS[t[1]])
    )
    atom = literal | dot | nset | set | words | fsm | group
    item = (
        (atom + "+").setParseAction(
            lambda t: MatchRepeated(
                t[0],
                repeat=True,
            )
        )
        | (atom + "*").setParseAction(lambda t: MatchRepeated(t[0], repeat=True, optional=True))
        | (atom + "?").setParseAction(lambda t: MatchRepeated(t[0], optional=True))
        | (atom + "{" + _0_to_99 + "}").setParseAction(lambda t: MatchRepeatedN(t[0], t[2], t[2]))
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


# Regex reconstructions


class Regex(ABC):
    @abstractmethod
    def members(self) -> Any:
        """Members, used for equality testing and hashing."""

    @abstractmethod
    def to_string(self) -> str:
        """Regex string representation."""

    @abstractmethod
    def min_length(self) -> float:
        """Minimum match length (-inf for no match)."""

    @abstractmethod
    def max_length(self) -> float:
        """Maximum match length (-inf for no match, inf for infinite)."""

    @abstractmethod
    def first_character(self, from_end: bool = False) -> "Regex":
        """A Regex describing the first (or last) matching character."""

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
            return RegexConcat((self, other))
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, Regex):
            return RegexUnion((self, other))
        else:
            return NotImplemented


class RegexChars(Regex):

    chars: str

    def __new__(cls, chars):
        # [] = ∅
        if not chars:
            return RegexUnion()

        obj = super().__new__(cls)
        obj.chars = "".join(sorted(set(chars)))
        return obj

    def members(self):
        return self.chars

    def to_string(self):
        return char_class(self.chars, negated=False)

    def min_length(self):
        return 1

    def max_length(self):
        return 1

    def first_character(self, from_end: bool = False) -> Regex:
        return self


class RegexNegatedChars(Regex):
    def __init__(self, chars):
        self.chars = "".join(sorted(set(chars)))

    def members(self):
        return self.chars

    def to_string(self):
        return char_class(self.chars, negated=True)

    def min_length(self):
        return 1

    def max_length(self):
        return 1

    def first_character(self, from_end: bool = False) -> Regex:
        return self


class RegexStar(Regex):

    regex: Regex

    def __new__(cls, regex: Regex):

        # ε* = ε
        if regex == RegexConcat():
            return regex
        # (A*)* = A*
        elif isinstance(regex, RegexStar):
            return regex

        # (ε|A|B|C)* = (A|B|C)*
        if isinstance(regex, RegexUnion) and RegexConcat() in regex.regexes:
            regex = RegexUnion(r for r in regex.regexes if r != RegexConcat())
        # (A*B*C*)* = (A|B|C)*
        if isinstance(regex, RegexConcat) and all(isinstance(r, RegexStar) for r in regex.regexes):
            regex = RegexUnion(cast(RegexStar, r).regex for r in regex.regexes)

        if isinstance(regex, RegexUnion):
            regexes = set(regex.regexes)
            for r in list(regexes):
                # (A*|B|C)* = (A|B|C)*
                if isinstance(r, RegexStar):
                    regexes.remove(r)
                    r = r.regex
                    regexes.add(r)
                # (A|B|C)* = (B|C)* if A => B*
                if any(regex_implies(r, RegexStar(s)) for s in regexes - {r}):
                    regexes.remove(r)
            regex = RegexUnion(regexes)

        # (ABC)* = B* if all(ABC => B*)
        if isinstance(regex, RegexConcat):
            for r in regex.regexes:
                star = RegexStar(r)
                if all(regex_implies(s, star) for s in regex.regexes):
                    regex = r
                    break

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

    def first_character(self, from_end: bool = False) -> Regex:
        return RegexConcat() | self.regex.first_character(from_end)


class RegexUnion(Regex):

    regexes: FrozenSet[Regex]

    def __new__(cls, regexes: Iterable[Regex] = ()):

        # (A|(B|C)|D)=(A|B|C|D)
        regexes = {s for x in (r.regexes if isinstance(r, RegexUnion) else [r] for r in regexes) for s in x}

        # A|B|C = B|C if A=>B
        for r in list(regexes):
            if any(regex_implies(r, s) for s in regexes - {r}):
                regexes.remove(r)

        # ([^ab]|[ac]|C) = ([^b]|C)
        if any(isinstance(r, RegexNegatedChars) for r in regexes):
            nchars = RegexNegatedChars(
                set.intersection(*[set(r.chars) for r in regexes if isinstance(r, RegexNegatedChars)])
                - {c for r in regexes if isinstance(r, RegexChars) for c in r.chars}
            )
            regexes -= {r for r in regexes if isinstance(r, RegexNegatedChars) or isinstance(r, RegexChars)}
            if not any(regex_implies(nchars, s) for s in regexes):
                regexes.add(nchars)

        # ([ab]|[ac]|C) = ([abc]|C)
        elif any(isinstance(r, RegexChars) for r in regexes):
            chars = RegexChars({c for r in regexes if isinstance(r, RegexChars) for c in r.chars})
            regexes -= {r for r in regexes if isinstance(r, RegexChars)}
            if not any(regex_implies(chars, s) for s in regexes):
                regexes.add(chars)

        # AB|AC|D = A(B|C|ε)
        prefix = first(first(r.regexes) for r in regexes if isinstance(r, RegexConcat))
        if prefix and all(isinstance(r, RegexConcat) and first(r.regexes) == prefix or r == prefix for r in regexes):
            stripped = {RegexConcat(r.regexes[1:]) if isinstance(r, RegexConcat) else RegexConcat() for r in regexes}
            return RegexConcat((prefix, RegexUnion(stripped)))

        # BA|CA|DA = (B|C|ε)A
        suffix = first(r.regexes[-1] for r in regexes if isinstance(r, RegexConcat) and r.regexes)
        if suffix and all(isinstance(r, RegexConcat) and r.regexes and r.regexes[-1] == suffix or r == suffix for r in regexes):
            stripped = {RegexConcat(r.regexes[:-1]) if isinstance(r, RegexConcat) else RegexConcat() for r in regexes}
            return RegexConcat((RegexUnion(stripped), suffix))

        # AA*|ε = A*|ε
        if any(r.min_length() == 0 for r in regexes):
            for r in {
                r
                for r in regexes
                if isinstance(r, RegexConcat) and len(r.regexes) == 2 and isinstance(r.regexes[-1], RegexStar) and r.regexes[0] == r.regexes[-1].regex
            }:
                regexes.remove(r)
                regexes.add(r.regexes[-1])
                if RegexConcat() in regexes:
                    regexes.remove(RegexConcat())

        # (A)=A
        if len(regexes) == 1:
            return first(regexes)

        obj = super().__new__(cls)
        obj.regexes = frozenset(regexes)
        return obj

    def members(self):
        return self.regexes

    def to_string(self):
        if not self.regexes:
            return "∅"

        ss = [re.sub(r"^\((.*)\)$", r"\1", str(r)) for r in self.regexes if r != RegexConcat()]
        unbracketed = len(ss) == 1 and len(ss[0]) == 1 or ss[0].startswith("[")
        return ("{}{}" if unbracketed else "({}){}").format("|".join(ss), "?" * (RegexConcat() in self.regexes))

    def min_length(self):
        return -math.inf if not self.regexes else min([r.min_length() for r in self.regexes])

    def max_length(self):
        return -math.inf if not self.regexes else max([r.max_length() for r in self.regexes])

    def first_character(self, from_end: bool = False) -> Regex:
        return RegexUnion(r.first_character(from_end) for r in self.regexes)


class RegexConcat(Regex):

    regexes: Tuple[Regex]

    def __new__(cls, regexes: Iterable[Regex] = ()):

        # (A∅B) = ∅
        if any(r == RegexUnion() for r in regexes):
            return RegexUnion()
        # (A(BC)D) = (ABCD)
        regexes = [s for x in (r.regexes if isinstance(r, RegexConcat) else [r] for r in regexes) for s in x]

        # peephole optimizer
        while True:
            # A* A = A A* (canonical form)
            i = first(i for i in range(len(regexes) - 1) if isinstance(regexes[i], RegexStar) and cast(RegexStar, regexes[i]).regex == regexes[i + 1])
            if i is not None:
                regexes[i], regexes[i + 1] = regexes[i + 1], regexes[i]
                continue
            # A* B* = A* if A => B
            i = first(
                i
                for i in range(len(regexes) - 1)
                if isinstance(regexes[i], RegexStar)
                and isinstance(regexes[i + 1], RegexStar)
                and regex_implies(cast(RegexStar, regexes[i]).regex, cast(RegexStar, regexes[i + 1]).regex)
            )
            if i is not None:
                del regexes[i]
                continue
            # A* B* = B* if B => A
            i = first(
                i
                for i in range(len(regexes) - 1)
                if isinstance(regexes[i], RegexStar)
                and isinstance(regexes[i + 1], RegexStar)
                and regex_implies(cast(RegexStar, regexes[i + 1]).regex, cast(RegexStar, regexes[i]).regex)
            )
            if i is not None:
                del regexes[i + 1]
                continue
            # nothing left to optimize
            break

        # (A) = A
        if len(regexes) == 1:
            return first(regexes)

        obj = super().__new__(cls)
        obj.regexes = tuple(regexes)
        return obj

    def members(self):
        return self.regexes

    def to_string(self):
        ss = [str(r) for r in self.regexes]
        while True:
            # replace A A* with A+
            i = first(i for i in range(len(ss) - 1) if ss[i] + "*" == ss[i + 1])
            if i is not None:
                ss[i + 1] = ss[i + 1][:-1] + "+"
                del ss[i]
                continue
            break
        return ".{0}" if not self.regexes else "({})".format("".join(ss))

    def min_length(self):
        return sum(r.min_length() for r in self.regexes)

    def max_length(self):
        return sum(r.max_length() for r in self.regexes)

    def first_character(self, from_end: bool = False) -> Regex:
        fc = RegexUnion()
        for r in self.regexes[:: -1 if from_end else 1]:
            fcr = r.first_character(from_end)
            if isinstance(fcr, RegexUnion) and RegexConcat() in fcr.regexes:
                fc = RegexUnion([fc, *[r for r in fcr.regexes if r != RegexConcat()]])
            else:
                fc |= fcr
                break
        else:
            fc |= RegexConcat()
        return fc


@lru_cache(maxsize=None)
def regex_implies(a: Regex, b: Regex) -> bool:
    """Whether one regex implies the other."""
    # A < B
    if a == b:
        return True
    # [ab] < [abc]
    if isinstance(a, RegexChars) and isinstance(b, RegexChars):
        return set(a.chars) <= set(b.chars)
    # [ab] < [^cd]
    elif isinstance(a, RegexChars) and isinstance(b, RegexNegatedChars):
        return not (set(a.chars) & set(b.chars))
    # [^ab] < [^a]
    elif isinstance(a, RegexNegatedChars) and isinstance(b, RegexNegatedChars):
        return set(a.chars) >= set(b.chars)
    # [^...] !< [...]
    elif isinstance(a, RegexNegatedChars) and isinstance(b, RegexChars):
        return False
    # A* < B* iff A < B
    elif isinstance(a, RegexStar) and isinstance(b, RegexStar):
        return regex_implies(a.regex, b.regex)
    # A|B|C < D iff all(ABC < D)
    elif isinstance(a, RegexUnion):
        return all(regex_implies(r, b) for r in a.regexes)
    # A < B|C|D iff any(A < BCD)
    elif isinstance(b, RegexUnion):
        return any(regex_implies(a, r) for r in b.regexes)
    # ε => A*
    elif a == RegexConcat() and isinstance(b, RegexStar):
        return True
    # A < B* if A < B
    elif isinstance(b, RegexStar) and regex_implies(a, b.regex):
        return True
    # ABC < D* if all(A < D)
    elif isinstance(a, RegexConcat) and isinstance(b, RegexStar) and all(regex_implies(r, b) for r in a.regexes):
        return True
    # incompatible length
    elif a.min_length() < b.min_length() or a.max_length() > b.max_length():
        return False
    # incompatible first characters
    elif not regex_implies(a.first_character(), b.first_character()):
        return False
    # incompatible last characters
    elif not regex_implies(a.first_character(from_end=True), b.first_character(from_end=True)):
        return False
    # the slow way using FMSs
    if SLOW_SIMPLIFICATION:
        try:
            ans = Pattern(f"¬(¬({a})|{b})").nfa.min_length() is None
            logger.debug("%s =%s=> %s", a, "=" if ans else "/", b)
            return ans
        except ParseException:
            # currently doesn't work with e.g. emoji injected via \f or \w 🙁
            warnings.warn("Cannot fully simplify regular expression due to non-Latin characters", UnicodeWarning)
            return False
    return False


def regex(pattern: str) -> Regex:
    """Generate a Regex object directly from basic regular expression syntax. Useful for testing."""

    from pyparsing import Forward, Literal, OneOrMore, ParserElement, Word, infixNotation, nums, opAssoc

    ParserElement.setDefaultWhitespaceChars("")
    ParserElement.enablePackrat()

    _0_to_99 = Word(nums, min=1, max=2).setParseAction(lambda t: int("".join(t[0])))
    printables = ppu.Latin1.printables + " " + EXTRA_PRINTABLES
    literal_exclude = r"()+*.?{}^|$\[]"
    set_exclude = r"\]"

    literal = Word(printables, excludeChars=literal_exclude, exact=1).setParseAction(lambda t: RegexChars(t[0]))
    dot = Literal(".").setParseAction(lambda t: RegexNegatedChars(""))
    nset = ("[^" + Word(printables, excludeChars=set_exclude, min=1) + "]").setParseAction(lambda t: RegexNegatedChars(srange(f"[{t[1]}]")))
    set = ("[" + Word(printables, excludeChars=set_exclude, min=1) + "]").setParseAction(lambda t: RegexChars(srange(f"[{t[1]}]")))

    expr = Forward()
    group = ("(" + expr + ")").setParseAction(lambda t: t[1])
    atom = literal | dot | nset | set | group
    item = (
        (atom + "*").setParseAction(lambda t: RegexStar(t[0]))
        | (atom + "+").setParseAction(lambda t: t[0] + RegexStar(t[0]))
        | (atom + "?").setParseAction(lambda t: RegexConcat() | t[0])
        | (atom + "{" + _0_to_99 + "}").setParseAction(lambda t: RegexConcat([t[0]] * t[2]))
        | (atom + "{" + _0_to_99 + ",}").setParseAction(lambda t: RegexConcat([t[0]] * t[2]) + RegexStar(t[0]))
        | atom
    )
    items = OneOrMore(item).setParseAction(lambda t: RegexConcat(t))
    expr <<= infixNotation(items, [("|", 2, opAssoc.LEFT, lambda t: RegexUnion(t[0][::2]))])

    return expr.parseString(pattern, parseAll=True)[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=r"""NFA-based pattern matcher supporting novel spatial conjunction and modifiers.
Supported syntax:

CHARACTERS
- a        character literal
- .        wildcard character
- [abc]    character class
- [a-z]    character range
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
- (?<ID>P) define submatch capture group 
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
    parser.add_argument("-s", dest="svg", metavar="NAME", default=None, help="save FSM image and description")
    parser.add_argument("-c", dest="console", action="store_true", help="save FSM image for console")
    parser.add_argument("-x", dest="example", action="store_true", help="generate an example matching string")
    parser.add_argument("-r", dest="regex", action="store_true", help="generate a standard equivalent regex")
    parser.add_argument("-b", dest="bounds", action="store_true", help="generate lexicographic match bounds")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-X", dest="examples_only", metavar="N", type=int, help="output N example matches and quit")
    group.add_argument("-R", dest="regex_only", action="store_true", help="output a standard equivalent regex and quit")

    args = parser.parse_args()
    global DICTIONARY_FSM, EXPLICIT_FSM, SLOW_SIMPLIFICATION

    if args.examples_only is not None or args.regex_only:
        logger.setLevel(logging.ERROR)
        warnings.simplefilter("ignore")
        SLOW_SIMPLIFICATION = False

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

    if args.examples_only is not None:
        for _ in range(args.examples_only):
            print(pattern.example())
        return

    if args.regex_only:
        regex = pattern.nfa.regex()
        regex_repr = "$." if regex == RegexUnion() else "^$" if regex == RegexConcat() else f"^{regex}$"
        print(regex_repr)
        return

    if args.svg:
        logger.info(f"Rendering NFA diagram to '{args.svg}.dot.svg'")
        pattern.nfa.render(args.svg)
        pattern.nfa.save(args.svg, renumber_states=not DEBUG)

    if args.console:
        logger.info(f"Rendering NFA console diagram to 'console.dot.svg'")
        pattern.nfa.render("fsm_console", console=True)

    if args.example:
        logger.info(f"Example match: {pattern.example()!r}")

    if args.bounds:
        logger.info(f"Match bounds: {pattern.nfa.bound(True, 10)!r} to {pattern.nfa.bound(False, 10)!r}")

    if args.regex:
        regex = pattern.nfa.regex()
        regex_repr = "$." if regex == RegexUnion() else "^$" if regex == RegexConcat() else f"^{regex}$"
        logger.info(f"Equivalent regex: {regex_repr}")
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
                match = pattern.match(word)
                if match is not None:
                    if match:
                        print(f"{word} ({', '.join(f'{k}={v}' for k,v in sorted(match.items()))})", flush=True)
                    else:
                        print(word, flush=True)


if __name__ == "__main__":
    main()
