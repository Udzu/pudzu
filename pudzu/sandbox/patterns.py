from pudzu.utils import *
from typing import *

State = Union[int, Collection['State']]
Move = Enum('Move', 'EMPTY ALL')
Input = Union[str, Move]
Transitions = Dict[Tuple[State, Input], Collection[State]]

class NFA:
    """Nondeterministic Finite Automaton with
    - single start and end state
    - epsilon-moves
    - *-moves (only used if there is no other matching input)
    """

    def __init__(self, start: State, end: State, transitions: Transitions):
        self.start = start
        self.end = end
        self.transitions = transitions
        
    def __repr__(self) -> str:
        return f"NFA(start={self.start}, end={self.end}, transitions={self.transitions})"
        
    def match(string: str) -> bool:
        ...
        
    def remove_unreachable_states(self) -> 'NFA':
        ...

def MatchIn(characters: str) -> NFA:
    """Examples: a, [abc]"""
    return NFA(0, 1, {(0, c): [1] for c in characters})

def MatchNotIn(characters: str) -> NFA:
    """Examples: [^abc], ."""
    return NFA(0, 1, merge({(0, Move.ALL): [1]}, {(0, c): [] for c in characters}))

def MatchAfter(nfa1: NFA, nfa2: NFA) -> NFA:
    """Examples: ab"""
    t1 = {((s,1),i): [(t,1) for t in ts] for (s,i),ts in nfa1.transitions.items()}
    t2 = {((nfa1.end, 1) if s == nfa2.start else (s,2),i): [(t,2) for t in ts] for (s,i),ts in nfa2.transitions.items()}
    return NFA((nfa1.start, 1), (nfa2.end, 2), merge(t1, t2))
    
def MatchEither(nfa1: NFA, nfa2: NFA) -> NFA:
    """Examples: a|b"""
    t1 = {((s,1),i): [(t,1) for t in ts] for (s,i),ts in nfa1.transitions.items()}
    t2 = {((s,2),i): [(t,2) for t in ts] for (s,i),ts in nfa2.transitions.items()}
    t12 = {(0, Move.EMPTY): [(nfa1.start, 1), (nfa2.start, 2)], ((nfa1.end, 1), Move.EMPTY): 1, ((nfa2.end, 2), Move.EMPTY): 1}
    return NFA(0, 1, merge(t1, t2, t12))

# TODO: MatchBoth, MatchRepeated, etc

# TODO: parser