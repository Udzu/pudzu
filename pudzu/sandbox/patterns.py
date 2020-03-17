import argparse
import copy
import json
import logging
import string
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import *
from pudzu.utils import *

# Types
State = Union[str, Collection['State']]
Move = Enum('Move', 'EMPTY ALL')
Input = Union[str, Move]
Transitions = Dict[Tuple[State, Input], AbstractSet[State]]

class CaptureOptions(NamedTuple):
    reverse: bool = False
    case_insensitive: bool = False
    shift: int = 0

CaptureGroup = str
CaptureId = int
CaptureType = Enum('CaptureType', 'START END CAPTURE')
CaptureStarts = CaptureEnds = Dict[State, AbstractSet[Tuple[CaptureGroup, CaptureId]]]
Captures = Dict[State, Dict[Tuple[CaptureGroup, CaptureId], CaptureOptions]]

# TODO: sort out capture state types and destupidify!
@dataclass(frozen=True)
class CaptureState:
    prefix: List[str] = field(default_factory=list)
    prefix_case_insensitive: List[bool] = field(default_factory=list)
    suffix: List[str] = field(default_factory=list)
    suffix_case_insensitive: List[bool] = field(default_factory=list)
    length: List[int] = field(default_factory=list)
    offsets: Dict[CaptureId, int] = field(default_factory=dict)
    
CapturesStateDict = Dict[CaptureGroup, CaptureState]
CapturesState = FrozenSet[Tuple[CaptureGroup, CaptureState]]

def freeze(cstate: CapturesStateDict) -> CapturesState:
    return frozenset((g, CaptureState(tuple(s.prefix), tuple(s.prefix_case_insensitive), tuple(s.suffix), tuple(s.suffix_case_insensitive), tuple(s.length), frozenset(s.offsets.items()))) for g,s in cstate.items())

def unfreeze(cstate: CapturesState) -> CapturesStateDict:
    return dict((g, CaptureState(list(s.prefix), list(s.prefix_case_insensitive), list(s.suffix), list(s.suffix_case_insensitive), list(s.length), dict(s.offsets))) for g,s in cstate)

# NFAs
renderer = optional_import("PySimpleAutomata.automata_IO")
logger = logging.getLogger('patterns')

class NFA:
    """Nondeterministic Finite Automata with
    - single start state (with no inbounds) and end state (with no outbounds)
    - ε-moves (including potential ε loops)
    - *-moves (only used if there is no other matching move)
    - optional capture annotations on states
    """

    def __init__(self, start: State, end: State, transitions: Transitions,
                 capture_starts: Optional[CaptureStarts] = None,
                 capture_ends: Optional[CaptureEnds] = None,
                 captures: Optional[Captures] = None):
        self.start = start
        self.end = end
        self.transitions = transitions
        self.states = {self.start, self.end} | {s for s,_ in self.transitions.keys()} | {t for ts in self.transitions.values() for t in ts}
        self.capture_starts = {s:v for s,v in (capture_starts or {}).items() if s in self.states}
        self.capture_ends = {s:v for s,v in (capture_ends or {}).items() if s in self.states}
        self.captures = {s:v for s,v in (captures or {}).items() if s in self.states}

    def __repr__(self) -> str:
        return f"NFA(start={self.start}, end={self.end}, transitions={self.transitions})"

    def render(self, name: str, path: str = './') -> None:
        """Render NFA to SVG using PySimpleAutomata"""
        def label_state(s):
            if isinstance(s, str): return s
            else: return "\u200B"+ "".join(label_state(t) for t in s) + "\u200D"
        def label_copt(o):
            return "r" * o.reverse + "i" * o.case_insensitive + f"s{o.shift}" * (o.shift != 0)
        def label(s):
            l = label_state(s)
            if self.capture_starts.get(s): l += "\n{" + ", ".join(f"{g}.{i}" for (g,i) in self.capture_starts[s])
            if self.capture_ends.get(s): l += "\n}" + ", ".join(f"{g}.{i}" for (g,i) in self.capture_ends[s])
            if self.captures.get(s): l += "\n→" + ", ".join(f"{g}.{i}{label_copt(v)}" for (g,i),v in self.captures[s].items())
            return l
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

    def capture_epsilon(self, state: State, captures_state: CapturesState) -> AbstractSet[CapturesState]:
        cstates = unfreeze(captures_state)
        
        # first handle capture closures
        for group, id in self.capture_ends.get(state, set()):
            # check we're actually capturing (though we may call this repeatedly in succession)
            assert group in cstates, f"Unexpected capture close for {group}\n{cstates}"
            cstate = cstates[group]
            if id not in cstate.offsets:
                # we've already closed this capture
                continue
            elif cstate.length:
                # if we've already captured this group, just check the length is ok
                if cstate.offsets[id] != cstate.length[0]: return set()
            else:
                # otherwise, check we've captured enough
                if cstate.offsets[id] < max(len(cstate.prefix), len(cstate.suffix)): return set()
                # set the length
                cstate.length.append(cstate.offsets[id])
                # check that the prefix and suffix are compatible (updating them to be more precise if necessary)
                if len(cstate.suffix) <= len(cstate.prefix):
                    shorter, shorter_ci = cstate.suffix, cstate.suffix_case_insensitive
                    longer, longer_ci = cstate.prefix, cstate.prefix_case_insensitive
                else:
                    shorter, shorter_ci = cstate.prefix, cstate.prefix_case_insensitive
                    longer, longer_ci = cstate.suffix, cstate.suffix_case_insensitive
                # (loop over the shorter *fix...)
                for i in range(cstate.length[0]):
                    if i >= len(shorter):
                        shorter.append(longer[-i])
                        shorter_ci.append(longer_ci[-i])
                    else:
                        if shorter_ci[i]:
                            if shorter[i].lower() != longer[-i].lower(): return set()
                            shorter_ci[i] = longer_ci[-i]
                            shorter[i] = longer[-i]
                        elif longer_ci[-i]:
                            if shorter[i].lower() != longer[-i].lower(): return set()
                            longer_ci[-i] = shorter_ci[i]
                            longer[-i] = shorter[i]
                        else:
                            if shorter[i] != longer[-i]: return set()
                    
            # and we're done with this capture (though it may be repeated later)
            del cstate.offsets[id]
                
        # now handle capture openings
        for group, id in self.capture_starts.get(state, set()):
            # check we're not already capturing (though we may call this repeatedly before any input)
            if group in cstates:
                assert cstates[group].offsets.get(id, 0) == 0, f"Unexpected capture open for ({group}, {id})\n{cstates}"
                
            # set the offset and that's it for now
            cstates.setdefault(group, CaptureState()).offsets[id] = 0
        
        return { freeze(cstates) }
        
    def capture_input(self, state: State, captures_state: CapturesState, i: str) -> AbstractSet[CapturesState]:
    
        cstates = unfreeze(captures_state)
        
        for (group, id), options in self.captures.get(state, {}).items():
            # check we're actually capturing
            assert group in cstates, f"Unexpected capture input for {group}\n{cstates}"
            cstate = cstates[group]
            assert id in cstate.offsets, f"Unexpected capture input for ({group}, {id})\n{cstates}"
            # check if we've already captured enough
            if cstate.length and cstate.offsets[id] >= cstate.length[0]: return set()
            # shift the input if necessary
            j = i
            if options.shift != 0:
                for alphabet in (string.ascii_lowercase, string.ascii_uppercase):
                    if j in alphabet:
                        j = alphabet[(alphabet.index(j) - options.shift) % 26]
            # check the input against what we've got so far
            affix = cstate.suffix if options.reverse else cstate.prefix
            affix_ci = cstate.suffix_case_insensitive if options.reverse else cstate.prefix_case_insensitive
            if cstate.offsets[id] < len(affix):
                # compare to existing value
                if options.case_insensitive:
                    if j.lower() != affix[cstate.offsets[id]].lower(): return set()
                elif affix_ci[cstate.offsets[id]]:
                    # replace case-insensitive match by a case sensitive one
                    if j.lower() != affix[cstate.offsets[id]].lower(): return set()
                    affix[cstate.offsets[id]] = j
                    affix_ci[cstate.offsets[id]] = False
                else:
                    if j != affix[cstate.offsets[id]]: return set()
            else:
                # first input, so just append it
                affix.append(j)
                affix_ci.append(options.case_insensitive)
            cstate.offsets[id] += 1
    
        return { freeze(cstates) }
    
    # TODO: return capture information
    def match(self, string: str) -> bool:
        """Match NFA against a string"""
        states = self.expand_epsilons({(self.start, frozenset())})
        for c in string:
            states = {(t,tc) for (s,sc) in states for t in self.transitions.get((s, c), self.transitions.get((s, Move.ALL), set())) for tc in self.capture_input(s, sc, c)}
            states = self.expand_epsilons(states)
        return any(s == self.end for s,_ in states)

    def expand_epsilons(self, states: Iterable[Tuple[State, CapturesState]]) -> AbstractSet[Tuple[State, CapturesState]]:
        old, new = set(), states
        while new:
            old.update(new)
            new = {(t,tc) for (s,sc) in new for t in self.transitions.get((s, Move.EMPTY), set()) for tc in self.capture_epsilon(s,sc) if (t,tc) not in old}
        return old
        
    def expand_epsilons_no_captures(self, states: Iterable[State]) -> AbstractSet[State]:  # (capture-unaware expansion used by DFA generation)
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
        self.transitions = {(s,i): ts for (s,i),ts in self.transitions.items() if s in reachable}
        
        # remove states that can't reach the end (and any transitions to those states)
        acceptable, new = set(), {self.end}
        while new:
            acceptable.update(new)
            new = {s for (s,i),ts in self.transitions.items() if any(t in new for t in ts) and s not in acceptable}
        self.transitions = {(s,i): {t for t in ts if t in acceptable} for (s,i),ts in self.transitions.items()
                            if s in acceptable and (any(t in acceptable for t in ts) or (s,Move.ALL) in self.transitions)}

        # update states and capture info
        self.states = acceptable | { self.start, self.end }
        self.capture_starts = {s:v for s,v in self.capture_starts.items() if s in self.states}
        self.capture_ends = {s:v for s,v in self.capture_ends.items() if s in self.states}
        self.captures = {s:v for s,v in self.captures.items() if s in self.states}
                            
        # TODO: remove redundant ε states?

# Helper functions
def merge_trans(*args):
    """Merge multiple transitions, unioning target states."""
    return merge_with(lambda x: set.union(*x), *args)

def merge_captures(*args):
    """Merge multiple captures mappings, merging the target mappings"""
    return merge_with(lambda x: merge(*x), *args)

def make_captures(capture_fn):
    """Hacky helper for generating capture mappings."""
    capture_fn = ignoring_extra_args(capture_fn)
    start = capture_fn(lambda nfa: nfa.capture_starts, merge_trans, CaptureType.START)
    end = capture_fn(lambda nfa: nfa.capture_ends, merge_trans, CaptureType.END)
    capture = capture_fn(lambda nfa: nfa.captures, merge_captures, CaptureType.CAPTURE)
    return start, end, capture
    
# NFA constructors
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
    start, end = ("0",), ("1",)
    transitions = {}
    for word in words:
        for i in range(len(word)):
            transitions.setdefault((word[:i] or start, word[i]), set()).add(word[:i+1])
        transitions[(word, Move.EMPTY)] = {end}
    return NFA(start, end, transitions)
    
def MatchDictionary(path: Path) -> NFA:
    with open(str(path), "r", encoding="utf-8") as f:
        return MatchWords(w.rstrip("\n") for w in f)
    
def MatchAfter(nfa1: NFA, nfa2: NFA) -> NFA:
    """Handles: AB"""
    t1 = {(("1",s),i): {("1",t) for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2 = {(("1",nfa1.end) if s == nfa2.start else ("2",s),i): {("1",nfa1.end) if t == nfa2.start else ("2",t) for t in ts} for (s,i),ts in nfa2.transitions.items()}
    def capture_fn(getter, merger):
        c1 = {("1",s):v for s,v in getter(nfa1).items()}
        c2 = {("1",nfa1.end) if s == nfa2.start else ("2",s):v for s,v in getter(nfa2).items()}
        return merger(c1, c2)
    return NFA(("1",nfa1.start), ("2",nfa2.end), merge_trans(t1, t2), *make_captures(capture_fn))

def MatchEither(*nfas: NFA) -> NFA:
    """Handles: A|B (and arbitrary alternation too)"""
    tis = []
    for n,nfa in enumerate(nfas, 1):
        tis.append({((str(n),s),i): {(str(n),t) for t in ts} for (s,i),ts in nfa.transitions.items()})
    tstart = {("1", Move.EMPTY): {(str(n), nfa.start) for n,nfa in enumerate(nfas, 1)}}
    tend = {((str(n), nfa.end), Move.EMPTY): {"2"} for n,nfa in enumerate(nfas, 1)}
    def capture_fn(getter, merger):
        return {(str(n),s):v for n,nfa in enumerate(nfas, 1) for s,v in getter(nfa).items()}
    return NFA("1", "2", merge_trans(tstart, tend, *tis), *make_captures(capture_fn))

def MatchRepeated(nfa: NFA, repeat: bool = False, optional: bool = False) -> NFA:
    """Handles: A*, A+, A?"""
    transitions = {(("0",s),i): {("0",t) for t in ts} for (s,i),ts in nfa.transitions.items()}
    transitions[("1", Move.EMPTY)] = {("0",nfa.start)}
    if optional: transitions[("1", Move.EMPTY)].add("2")
    transitions[(("0",nfa.end), Move.EMPTY)] = {"2"}
    if repeat: transitions[(("0",nfa.end), Move.EMPTY)].add(("0",nfa.start))
    def capture_fn(getter): return {("0",s):v for s,v in getter(nfa).items()}
    return NFA("1", "2", transitions, *make_captures(capture_fn))

def MatchRepeatedN(nfa: NFA, minimum: int, maximum: int) -> NFA:
    """Handles: A{2,5}"""
    if minimum == maximum == 0:
        return MatchEmpty()
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
    
def MatchDFA(nfa: NFA, negate: bool) -> NFA:
    """Handles: !A"""
    # no support for DFAs and captures
    if nfa.capture_starts or nfa.capture_ends or nfa.captures:
        raise NotImplementedError(f"Combination of {'negation' if negate else 'DFAs'} and capture groups is unsupported")
    
    # convert to DFA (and optionally invert accepted/rejected states)
    start_state = tuple(sorted(nfa.expand_epsilons_no_captures({nfa.start}), key=str))
    to_process = [start_state]
    processed_states = set()
    accepting_states = set()
    transitions = {}
    while to_process:
        current_state = to_process.pop()
        processed_states.add(current_state)
        if any(s == nfa.end for s in current_state): accepting_states.add(current_state)
        moves = {i for (s,i) in nfa.transitions if s in current_state and i != Move.EMPTY}
        for i in moves:
            next_state = {t for s in current_state for t in nfa.transitions.get((s,i), nfa.transitions.get((s,Move.ALL), set()))}
            next_state = tuple(sorted(nfa.expand_epsilons_no_captures(next_state), key=str))
            transitions[(current_state, i)] = {next_state}
            if next_state not in processed_states: to_process.append(next_state)
    
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
    nfa.remove_redundant_states()
    return nfa

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
    def capture_fn(getter, merge): 
        c1 = {(s1,s2):v for s1,v in getter(nfa1).items() for s2 in nfa2.states}
        c2 = {(s1,s2):v for s2,v in getter(nfa2).items() for s1 in nfa1.states}
        return merge(c1, c2)
    nfa = NFA((nfa1.start, nfa2.start), (nfa1.end, nfa2.end), transitions, *make_captures(capture_fn))
    nfa.remove_redundant_states()
    return nfa

def MatchContains(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A<B, A<<B, A>B, A>>B"""
    # transition between (2) A, (3) AxB, and (5) A states
    # for proper, also use (1) A and (4) A states
    t1, t1e, t4, t4e = {}, {}, {}, {}
    if proper:
        t1 = {(("1",s),i): {("1",t) for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(("1",s),i): {("2",t) for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}
    t2 = {(("2",s),i): {("2",t) for t in ts} for (s,i),ts in nfa1.transitions.items()}
    t2e = {(("2",s), Move.EMPTY): {("3",s,nfa2.start)} for s in nfa1.states}
    t3 = {(("3",s,q), i): {("3",s,t) for t in ts} for (q,i),ts in nfa2.transitions.items() for s in nfa1.states}
    t3e = {(("3",s,nfa2.end), Move.EMPTY): {(("4",s) if proper else ("5",s))} for s in nfa1.states}
    if proper:
        t4 = {(("4",s),i): {("4",t) for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
        t4e = {(("4",s),i): {("5",t) for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}
    t5 = {(("5",s),i): {("5",t) for t in ts} for (s,i),ts in nfa1.transitions.items()}
    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e, t5)
    def capture_fn(getter, merge): 
        c1 = {(i,s):v for i in "25" + "12"*proper for s,v in getter(nfa1).items()}
        c2 = {("3",s,q):v for s in nfa1.states for q,v in getter(nfa2).items()}
        return merge(c1, c2)
    nfa = NFA(("1",nfa1.start) if proper else ("2",nfa1.start), ("5",nfa1.end), transitions, *make_captures(capture_fn))
    nfa.remove_redundant_states()
    return nfa

def MatchInterleaved(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A^B, A^^B"""
    # transition between (2) AxB and (3) AxB states
    # for proper, also use (1) A and (4) A states
    t1, t1e, t4, t4e = {}, {}, {}, {}
    if proper:
        t1 = {(("1",s),i): {("1",t) for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
        t1e = {(("1",s),i): {("2",t,nfa2.start) for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}
    t2 = {(("2",s,q), i): {("2",t,q) for t in ts} for (s,i),ts in nfa1.transitions.items() for q in nfa2.states}
    t2e = {(("2",q,s), Move.EMPTY): {("3",q,s)} for q in nfa1.states for s in nfa2.states}
    t3 = {(("3",q,s), i): {("3",q,t) for t in ts} for (s,i),ts in nfa2.transitions.items() for q in nfa1.states}
    t3e = {(("3",q,s), Move.EMPTY): {("2",q,s)} for q in nfa1.states for s in nfa2.states}
    if proper:
        t4 = {(("2",s,nfa2.end),i): {("4",t) for t in ts} for (s,i),ts in nfa1.transitions.items() if i != Move.EMPTY}
        t4e = {(("4",s),i): {("4",t) for t in ts} for (s,i),ts in nfa1.transitions.items() if i == Move.EMPTY}
    transitions = merge_trans(t1, t1e, t2, t2e, t3, t3e, t4, t4e)
    def capture_fn(getter, merge): 
        c1 = {(i,s):v for i in "2"+"14"*proper for s,v in getter(nfa1).items()}
        c2 = {("3",s,q):v for s in nfa1.states for q,v in getter(nfa2).items()}
        return merge(c1, c2)
    nfa = NFA(("1",nfa1.start) if proper else ("2",nfa1.start, nfa2.start), 
              ("4",nfa1.end) if proper else ("3",nfa1.end, nfa2.end), transitions, *make_captures(capture_fn))
    nfa.remove_redundant_states()
    return nfa

def MatchAlternating(nfa1: NFA, nfa2: NFA, proper: bool) -> NFA:
    """Handles: A#B, A##B"""
    # transition between (1) AxB and (2) AxB states
    # for improper, also use (0) start state
    t0 = {("0",Move.EMPTY): {("1",nfa1.start,nfa2.start), ("2",nfa1.start,nfa2.start)}} if not proper else {}
    t1 = {(("1",s,q),i): {("1" if i == Move.EMPTY else "2",t,q) for t in ts} for (s,i),ts in nfa1.transitions.items() for q in nfa2.states}
    t2 = {(("2",q,s),i): {("2" if i == Move.EMPTY else "1",q,t) for t in ts} for (s,i),ts in nfa2.transitions.items() for q in nfa1.states}
    # handle final transitions
    t1e = {(("1",nfa1.end,s),i): {("1",nfa1.end,t) for t in ts} for (s,i),ts in nfa2.transitions.items() if i==Move.EMPTY}
    t2e = {(("2",s,nfa2.end),i): {("2",t,nfa2.end) for t in ts} for (s,i),ts in nfa1.transitions.items() if i==Move.EMPTY}
    t21 = {(("2",nfa1.end,nfa2.end),Move.EMPTY): {("1",nfa1.end,nfa2.end)}}
    transitions = merge_trans(t0, t1, t1e, t2, t2e, t21)
    def capture_fn(getter, merge): 
        c1 = {("1",s,q):v for s,v in getter(nfa1).items() for q in nfa2.states}
        c2 = {("2",q,s):v for s,v in getter(nfa2).items() for q in nfa1.states}
        return merge(c1, c2)
    nfa = NFA("0" if not proper else ("1",nfa1.start,nfa2.start), ("1",nfa1.end,nfa2.end), transitions, *make_captures(capture_fn))
    nfa.remove_redundant_states()
    return nfa

def MatchReversed(nfa: NFA) -> NFA:
    """Handles: (?r:A)"""
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
    captures = {s:{c:o._replace(reverse=not o.reverse) for c,o in v.items()} for s,v in nfa.captures.items()}
    nfa = NFA(nfa.end, nfa.start, transitions, nfa.capture_ends, nfa.capture_starts, captures)
    nfa.remove_redundant_states()
    return nfa
    
def MatchInsensitively(nfa: NFA) -> NFA:
    """Handles: (?i:A)"""
    transitions = {}
    for (s,i),ts in nfa.transitions.items():
        if isinstance(i, str):
            transitions.setdefault((s,i.lower()),set()).update(ts)
            transitions.setdefault((s,i.upper()),set()).update(ts)
        else:
            transitions[(s,i)] = ts
    captures = {s:{c:o._replace(case_insensitive=True) for c,o in v.items()} for s,v in nfa.captures.items()}
    return NFA(nfa.start, nfa.end, transitions, nfa.capture_ends, nfa.capture_starts, captures)

def MatchShifted(nfa: NFA, shift: int) -> NFA:
    """Handles: (?s1:A)"""
    transitions = {}
    for (s,i),ts in nfa.transitions.items():
        for alphabet in (string.ascii_lowercase, string.ascii_uppercase):
            if isinstance(i, str) and i in alphabet:
                i = alphabet[(alphabet.index(i) + shift) % 26]
                break
        transitions[(s,i)] = ts
    captures = {s:{c:o._replace(shift=(o.shift + shift) % 26) for c,o in v.items()} for s,v in nfa.captures.items()}
    return NFA(nfa.start, nfa.end, transitions, nfa.capture_starts, nfa.capture_ends, captures)

def MatchCapture(group: CaptureGroup, id: CaptureId, nfa: Optional[NFA] = None) -> NFA:
    """Handles: (?1), (?1:P), (?<ID), (?<ID:P)"""
    if nfa is None: nfa = MatchRepeated(MatchNotIn(""), repeat=True, optional=True)
    transitions = {(("0",s),i): {("0",t) for t in ts} for (s,i),ts in nfa.transitions.items()}
    transitions[("1", Move.EMPTY)] = {("0",nfa.start)}
    transitions[(("0",nfa.end), Move.EMPTY)] = {"2"}
    capture_starts = merge({"1": {(group, id)}}, {("0",s):v for s,v in nfa.capture_starts.items()})
    capture_ends = merge({("0",nfa.end): {(group, id)}}, {("0",s):v for s,v in nfa.capture_ends.items()})
    captures = {("0",s): {(group, id): CaptureOptions(), **nfa.captures.get(s, {})} for s in nfa.states if s != nfa.end}
    return NFA("1", "2", transitions, capture_starts, capture_ends, captures)

# Parser
def op_reduce(l):
    if len(l) == 1: return l[0]
    else: return op_reduce([l[1](l[0], l[2]), *l[3:]])

class Pattern:
    from pyparsing import (
        Word, Optional, oneOf, Forward, OneOrMore, alphas, Group, Literal, infixNotation, opAssoc,
        ParserElement, nums, alphanums
    )
    ParserElement.setDefaultWhitespaceChars('')
    ParserElement.enablePackrat()

    # TODO: character escaping, supported scripts?
    _0_to_99 = Word(nums, min=1, max=2).setParseAction(lambda t: int(''.join(t[0])))
    _m99_to_99 = (Optional("-") + _0_to_99).setParseAction(lambda t: t[-1] * (-1 if len(t) == 2 else 1))
    _id = Word(alphanums+"_")

    characters = alphanums + " '-"
    literal = Word(characters, exact=1).setParseAction(lambda t: MatchIn(t[0]))
    dot = Literal(".").setParseAction(lambda t: MatchNotIn(""))
    set = ("[" + Word(characters, min=1) + "]").setParseAction(lambda t: MatchIn(t[1]))
    nset = ("[^" + Word(characters, min=1) + "]").setParseAction(lambda t: MatchNotIn(t[1]))
    words = Literal(r"\w").setParseAction(lambda t: DICTIONARY_FILE)

    expr = Forward()
    group = (
        ("(" + expr + ")").setParseAction(lambda t: t[1]) |
        ("(?D:" + expr + ")").setParseAction(lambda t: MatchDFA(t[1], negate=False)) |
        ("(?i:" + expr + ")").setParseAction(lambda t: MatchInsensitively(t[1])) |
        ("(?r:" + expr + ")").setParseAction(lambda t: MatchReversed(t[1])) |
        ("(?s" + _m99_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchShifted(t[3], t[1])) |
        ("(?s:" + expr + ")").setParseAction(lambda t: MatchEither(*[MatchShifted(t[1], i) for i in range(1, 26)])) |
        ("(?&" + _id + "=" + expr + ")").setParseAction(lambda t: SUBPATTERNS.update({t[1]: t[3]}) or MatchEmpty()) |
        ("(?&" + _id + ")").setParseAction(lambda t: SUBPATTERNS[t[1]]) |
        ("(?" + _0_to_99 + ":" + expr + ")").setParseAction(lambda t: MatchCapture(str(t[1]), Pattern.get_capture_id(), t[3])) |
        ("(?" + _0_to_99 + ")").setParseAction(lambda t: MatchCapture(str(t[1]), Pattern.get_capture_id())) |
        ("(?<" + _id + ":" + expr + ")").setParseAction(lambda t: MatchCapture(t[1], Pattern.get_capture_id(), t[3])) |
        ("(?<" + _id + ")").setParseAction(lambda t: MatchCapture(t[1], Pattern.get_capture_id()))
    )
    atom = literal | dot | set | nset | words | group
    item = (
        (atom + "+").setParseAction(lambda t: MatchRepeated(t[0], repeat=True,)) |
        (atom + "*").setParseAction(lambda t: MatchRepeated(t[0], repeat=True, optional=True)) |
        (atom + "?").setParseAction(lambda t: MatchRepeated(t[0], optional=True)) |
        (atom + "{" + _0_to_99 + "}").setParseAction(lambda t: MatchRepeatedN(t[0], t[2], int(t[2]))) |
        (atom + "{" + _0_to_99 + ",}").setParseAction(lambda t: MatchRepeatedNplus(t[0], t[2])) |
        (atom + "{" + _0_to_99 + "," + _0_to_99 + "}").setParseAction(lambda t: MatchRepeatedN(t[0], t[2], t[4])) |
        ("!" + atom).setParseAction(lambda t: MatchDFA(t[1], negate=True)) |
        atom
    )
    items = OneOrMore(item).setParseAction(lambda t: reduce(MatchAfter, t))

    spatial_ops = (
        Literal(">>").setParseAction(lambda _: lambda x, y: MatchContains(x, y, proper=True)) |
        Literal(">").setParseAction(lambda _: lambda x, y: MatchContains(x, y, proper=False)) |
        Literal("<<").setParseAction(lambda _: lambda x, y: MatchContains(y, x, proper=True)) |
        Literal("<").setParseAction(lambda _: lambda x, y: MatchContains(y, x, proper=False)) |
        Literal("^^").setParseAction(lambda _: lambda x, y: MatchInterleaved(x, y, proper=True)) |
        Literal("^").setParseAction(lambda _: lambda x, y: MatchInterleaved(x, y, proper=False)) |
        Literal("##").setParseAction(lambda _: lambda x, y: MatchAlternating(x, y, proper=True)) |
        Literal("#").setParseAction(lambda _: lambda x, y: MatchAlternating(x, y, proper=False))
    )
    expr <<= infixNotation(items, [
        ('&', 2, opAssoc.LEFT, lambda t: reduce(MatchBoth, t[0][::2])),
        (spatial_ops, 2, opAssoc.LEFT, lambda t: op_reduce(t[0])),
        ('|', 2, opAssoc.LEFT, lambda t: MatchEither(*t[0][::2])),
    ])

    def __init__(self, pattern: str):
        self.reset_capture_id()
        self.pattern = pattern
        self.nfa = self.expr.parseString(pattern, parseAll=True)[0]

    def __repr__(self):
        return f"Pattern({self.pattern!r})"
        
    def match(self, string: str) -> bool:
        return self.nfa.match(string)

    capture_id = 0

    @classmethod
    def get_capture_id(cls) -> int:
        cls.capture_id += 1
        return cls.capture_id

    @classmethod
    def reset_capture_id(cls) -> None:
        cls.capture_id = 0


def main():
    parser = argparse.ArgumentParser(description = """NFA-based pattern matcher supporting novel spatial conjunction and modifiers.
Supported syntax:

- a        character literal
- .        wildcard character
- [abc]    character class
- [^abc]   negated character class
- \w       word from dictionary file
- PQ       concatenation
- P?       0 or 1 occurences
- P*       0 or more occurences
- P+       1 or more occurences
- P{n}     n occurences
- P{n,}    n or more occurences
- P{m,n}   m to n occurences
- P|Q      P or Q
- !P       not P
- P&Q      P and Q
- P<Q      P inside Q
- P<<Q     P strictly inside Q
- P>Q      P outside Q
- P>>Q     P strictly outside Q
- P^Q      P interleaved with Q
- P^^Q     P interleaved inside Q
- P#Q      P alternating with Q
- P##Q     P alternating before Q
- (P)      parentheses
- (?i:P)   case-insensitive match
- (?r:P)   reversed match
- (?sn:P)  shifted by n characters
- (?s:P)   shifted by 1 to 25 characters
- (?D:P)   convert NFA to DFA
- (?&ID=P) define subpattern for subsequent use
- (?&ID)   use subpattern
- (?n)     capture group #n
- (?n:P)   capture group #n satisfying P
- (?<ID)   capture group ID
- (?<ID:P) capture group ID satisfying P
""", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("pattern", type=str, help="pattern to compile")
    parser.add_argument("file", nargs='?', help="filename to search", default=None)
    parser.add_argument("-d", dest="dict", metavar="PATH", type=str, help="dictionary file to use for \\w", default=None)
    parser.add_argument("-D", dest="DFA", action="store_true", help="convert NFA to DFA", default=None)
    parser.add_argument("-i", dest="case_insensitive", action="store_true", help="case insensitive match")
    parser.add_argument("-s", dest="svg", action="store_true", help="save FSM diagram")
    args = parser.parse_args()

    global DICTIONARY_FILE, SUBPATTERNS
    
    if args.dict:
        logger.info(f"Compiling dictionary from '{args.dict}'")
        DICTIONARY_FILE = MatchDictionary(Path(args.dict))

    SUBPATTERNS = {}

    pattern = args.pattern
    if args.case_insensitive: pattern = f"(?i:{pattern})"
    if args.DFA: pattern = f"(?D:{pattern})"

    logger.info(f"Compiling pattern '{pattern}'")
    pattern = Pattern(pattern)
    
    if args.svg:
        logger.info(f"Saving NFA diagram to 'fsm.dot.svg'")
        pattern.nfa.render("fsm")
      
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            for w in f:
                word = w.rstrip("\n")
                if pattern.match(word):
                    print(word, flush=True)

if __name__ == '__main__':
    main()
