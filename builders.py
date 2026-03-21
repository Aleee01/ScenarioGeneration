from dataclasses import dataclass, field
from collections import defaultdict
from typing import Set

@dataclass
class Transition:
    id: str
    src: str
    dest: str
    label: str
    automaton: str

@dataclass
class Automaton:
    name: str
    states: Set[str] = field(default_factory=set)
    init: str = None
    final_states: Set[str] = field(default_factory=set)
    abstract: str = None

def build_automaton_from_dict(definition):
    automaton = Automaton(
        name=definition["name"],
        states=set(definition["states"]),
        init=definition["init"],
        final_states={definition["final"]} if isinstance(definition["final"], str)
                     else set(definition["final"]),
        abstract=definition.get("abstract", None)
    )

    transitions = []
    counter = 0
    

    for src, label, dest in definition["transitions"]:
        tid = f"TR_{automaton.name}_{counter}"
        counter += 1

        if src==dest:
            continue

        transitions.append(
            Transition(
                id=tid,
                src=src,
                dest=dest,
                label=label,
                automaton=automaton.name
            )
        )

    return automaton, transitions

def automaton_existence(a, idx, all_acts):
    s0 = f"ex_{a}_s0_{idx}"
    s1 = f"ex_{a}_s1_{idx}"

    transitions = [(s0, a, s1)]

    for act in all_acts:
        transitions.append((s1, act, s1))
        if act != a:
            transitions.append((s0, act, s0))

    return {
        "name": f"existence_{a}_{idx}",
        "states": [s0, s1],
        "init": s0,
        "final": s1,
        "transitions": transitions,
    }

def automaton_init(a, idx, all_acts):
    s0 = f"init_{a}_s0_{idx}"
    s1 = f"init_{a}_s1_{idx}"
    s2 = f"init_{a}_s2_{idx}"

    transitions = [(s0, a, s1)]

    for act in all_acts:
        transitions.append((s1, act, s1))
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s0, act, s2))

    return {
        "name": f"init_{a}_{idx}",
        "states": [s0, s1, s2],
        "init": s0,
        "final": s1,
        "transitions": transitions,
    }

def automaton_end(a, idx, all_acts):
    s0 = f"end_{a}_s0_{idx}"
    s1 = f"end_{a}_s1_{idx}"
    s2 = f"end_{a}_s2_{idx}"
    transitions = [(s0, a, s1), (s2, a, s1)]
    for act in all_acts:
        if act != a:
            transitions.append((s0, act, s0))
            transitions.append((s1, act, s2))
    return {
        "name": f"init_{a}_{idx}",
        "states": [s0, s1, s2],
        "init": s0,
        "final": s1,
        "transitions": transitions,
    }

def automaton_absence(a, idx, all_acts):
    s0 = f"ab_{a}_s0_{idx}"
    s1 = f"ab_{a}_s1_{idx}"
    transitions = [(s0, a, s1)]
    for act in all_acts:
        transitions.append((s1, act, s1))
        if act != a:
            transitions.append((s0, act, s0))
    return {
        "name": f"absence_{a}_{idx}",
        "states": [s0, s1],
        "init": s0,
        "final": s0,
        "transitions": transitions,
    }

def automaton_choice(a, b, idx, all_acts):
    s0 = f"choice_{a}_{b}_s0_{idx}"
    s1 = f"choice_{a}_{b}_s1_{idx}"
    transitions = [(s0, b, s1), (s0, a, s1)]
    for act in all_acts:
        transitions.append((s1, act, s1))
        if act not in (a, b):
            transitions.append((s0, act, s0))
    return {
        "name": f"choice_{a}_{b}_{idx}",
        "states": [s0, s1],
        "init": s0,
        "final": s1,
        "transitions": transitions,
    }

def automaton_exclusivechoice(a, b, idx, all_acts):
    s0 = f"exchoice_{a}_{b}_s0_{idx}"
    s1 = f"exchoice_{a}_{b}_s1_{idx}"
    s2 = f"exchoice_{a}_{b}_s2_{idx}"
    abs = f"exchoice_{a}_{b}_sabs_{idx}"
    s3 = f"exchoice_{a}_{b}_s3_{idx}"
    transitions = [(s0, b, s1), (s0, a, s2), (s2, b, s3), (s1, a, s3)]
    for act in all_acts:
        transitions.append((s3, act, s3))
        if act not in (a, b):
            transitions.append((s0, act, s0))
        if act != a:
            transitions.append((s1, act, s1))
        if act != b:
            transitions.append((s2, act, s2))
    return {
        "name": f"exclusivechoice_{a}_{b}_{idx}",
        "states": [s0, s1, s2, s3, abs],
        "init": s0,
        "final": [s1, s2],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_respondedexistence(a, b, idx, all_acts):
    s0 = f"respex_{a}_{b}_s0_{idx}"
    s1 = f"respex_{a}_{b}_s1_{idx}"
    s2 = f"respex_{a}_{b}_s2_{idx}"
    abs = f"respex_{a}_{b}_sabs_{idx}"
    transitions = [(s0, b, s1), (s0, a, s2), (s2, b, s1)]
    for act in all_acts:
        transitions.append((s1, act, s1))
        if act != a:
            transitions.append((s0, act, s0))
        if act != b:
            transitions.append((s2, act, s2))
    return {
        "name": f"respondedexistence_{a}_{b}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_branchrespondedexistence(a, b, c, idx, all_acts):
    s0 = f"br_respex_{a}_{b}_{c}_s0_{idx}"
    s1 = f"br_respex_{a}_{b}_{c}_s1_{idx}"
    s2 = f"br_respex_{a}_{b}_{c}_s2_{idx}"
    abs = f"br_respex_{a}_{b}_{c}_sabs_{idx}"
    transitions = [(s0, b, s1), (s0, a, s2), (s0, c, s1), (s2, b, s1), (s2, c, s1)]
    for act in all_acts:
        transitions.append((s1, act, s1))
        if act not in (a,b,c):
            transitions.append((s0, act, s0))
        if act not in (b,c):
            transitions.append((s2, act, s2))
    return {
        "name": f"br_respondedexistence_{a}_{b}_{c}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_coexistence(a, b, idx, all_acts):
    s0 = f"coex_{a}_{b}_s0_{idx}"
    s1 = f"coex_{a}_{b}_s1_{idx}"
    s2 = f"coex_{a}_{b}_s2_{idx}"
    s3 = f"coex_{a}_{b}_s3_{idx}"
    abs = f"coex_{a}_{b}_sabs_{idx}"
    transitions = [(s0, b, s1), (s1, a, s3), (s0, a, s2), (s2, b, s3)]
    for act in all_acts:
        transitions.append((s3, act, s3))
        if act != a:
            transitions.append((s1, act, s1))
        if act != b:
            transitions.append((s2, act, s2))
        if act not in (a, b):
            transitions.append((s0, act, s0))
    return {
        "name": f"coexistence_{a}_{b}_{idx}",
        "states": [s0, s1, s2, s3, abs],
        "init": s0,
        "final": [s0, s3],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_response(a, b, idx, all_acts):
    s0 = f"resp_{a}_{b}_s0_{idx}"
    s1 = f"resp_{a}_{b}_s1_{idx}"
    transitions = [(s0, a, s1), (s1, b, s0)]
    for act in all_acts:
        if act != a:
            transitions.append((s0, act, s0))
        if act != b:
            transitions.append((s1, act, s1))
    return {
        "name": f"response_{a}_{b}_{idx}",
        "states": [s0, s1],
        "init": s0,
        "final": s0,
        "transitions": transitions,
    }

def automaton_precedence(a, b, idx, all_acts):
    s0 = f"prec_{a}_{b}_s0_{idx}"
    s1 = f"prec_{a}_{b}_s1_{idx}"
    s2 = f"prec_{a}_{b}_s2_{idx}"
    abs = f"prec_{a}_{b}_sabs_{idx}"
    transitions = [(s0, b, s2), (s0, a, s1)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        transitions.append((s1, act, s1))
        if act not in (a,b):
            transitions.append((s0, act, s0))
    return {
        "name": f"precedence_{a}_{b}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_succession(a, b, idx, all_acts):
    s0 = f"succ_{a}_{b}_s0_{idx}"
    s1 = f"succ_{a}_{b}_s1_{idx}"
    s2 = f"succ_{a}_{b}_s2_{idx}"
    s3 = f"succ_{a}_{b}_s3_{idx}"
    abs = f"succ_{a}_{b}_sabs_{idx}"
    transitions = [(s0, b, s3), (s0, a, s1), (s1, b, s2), (s2, a, s1)]
    for act in all_acts:
        transitions.append((s3, act, s3))
        if act != a:
            transitions.append((s2, act, s2))
        if act != b:
            transitions.append((s1, act, s1))
        if act not in (a, b):
            transitions.append((s0, act, s0))
    return {
        "name": f"succession_{a}_{b}_{idx}",
        "states": [s0, s1, s2, s3, abs],
        "init": s0,
        "final": [s0, s2],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_chain_response(a, b, idx, all_acts):
    s0 = f"chainresp_{a}_{b}_s0_{idx}"
    s1 = f"chainresp_{a}_{b}_s1_{idx}"
    s2 = f"chainresp_{a}_{b}_s2_{idx}"
    transitions = [(s0, a, s1), (s1, b, s0)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s0, act, s0))
        if act != b:
            transitions.append((s1, act, s2))
    return {
        "name": f"chain_response_{a}_{b}_{idx}",
        "states": [s0, s1, s2],
        "init": s0,
        "final": s0,
        "transitions": transitions,
    }

def automaton_chain_precedence(a, b, idx, all_acts):
    s0 = f"chainprec_{a}_{b}_s0_{idx}"
    s1 = f"chainprec_{a}_{b}_s1_{idx}"
    s2 = f"chainprec_{a}_{b}_s2_{idx}"
    abs = f"chainprec_{a}_{b}_sabs_{idx}"
    transitions = [(s0, a, s1), (s0, b, s2), (s1, a, s1)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s1, act, s0))
        if act not in (a, b):
            transitions.append((s0, act, s0))
    return {
        "name": f"chain_precedence_{a}_{b}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_chain_succession(a, b, idx, all_acts):
    s0 = f"chainsucc_{a}_{b}_s0_{idx}"
    s1 = f"chainsucc_{a}_{b}_s1_{idx}"
    s2 = f"chainsucc_{a}_{b}_s2_{idx}"
    transitions = [(s0, a, s1), (s1, b, s0), (s0, b, s2)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != b:
            transitions.append((s1, act, s2))
        if act not in (a, b):
            transitions.append((s0, act, s0))
    return {
        "name": f"chain_succession_{a}_{b}_{idx}",
        "states": [s0, s1, s2],
        "init": s0,
        "final": s0,
        "transitions": transitions,
    }

def automaton_altresponse(a, b, idx, all_acts):
    s0 = f"altresp_{a}_{b}_s0_{idx}"
    s1 = f"altresp_{a}_{b}_s1_{idx}"
    s2 = f"altresp_{a}_{b}_sink_{idx}"
    transitions = [(s0, a, s1), (s1, b, s0), (s1, a, s2)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s0, act, s0))
        if act not in (a, b):
            transitions.append((s1, act, s1))
    return {
        "name": f"altresponse_{a}_{b}_{idx}",
        "states": [s0, s1, s2],
        "init": s0,
        "final": s0,
        "transitions": transitions,
    }

def automaton_altprecedence(a, b, idx, all_acts):
    s0 = f"aprec_{a}_{b}_s0_{idx}"
    s1 = f"aprec_{a}_{b}_s1_{idx}"
    s2 = f"aprec_{a}_{b}_s2_{idx}"
    abs = f"aprec_{a}_{b}_sabs_{idx}"
    transitions = [(s0, b, s2), (s0, a, s1), (s1, b, s0)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != b:
            transitions.append((s1, act, s1))
        if act not in (a, b):
            transitions.append((s0, act, s0))
    return {
        "name": f"altprecedence_{a}_{b}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_altsuccession(a, b, idx, all_acts):
    s0 = f"altsucc_{a}_{b}_s0_{idx}"
    s1 = f"altsucc_{a}_{b}_s1_{idx}"
    s2 = f"altsucc_{a}_{b}_s2_{idx}"
    transitions = [(s0, b, s2), (s0, a, s1), (s1, b, s0), (s1, a, s2)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act not in (a, b):
            transitions.append((s0, act, s0))
            transitions.append((s1, act, s1))
    return {
        "name": f"alternatesuccession_{a}_{b}_{idx}",
        "states": [s0, s1, s2],
        "init": s0,
        "final": s0,
        "transitions": transitions,
    }

def automaton_notsuccession(a, b, idx, all_acts):
    s0 = f"notsucc_{a}_{b}_s0_{idx}"
    s1 = f"notsucc_{a}_{b}_s1_{idx}"
    s2 = f"notsucc_{a}_{b}_s2_{idx}"
    abs = f"notsucc_{a}_{b}_sabs_{idx}"
    transitions = [(s0, a, s1), (s1, b, s2)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s0, act, s0))
        if act != b:
            transitions.append((s1, act, s1))
    return {
        "name": f"notsuccession_{a}_{b}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_notchainsucc(a, b, idx, all_acts):
    s0 = f"notchainsucc_{a}_{b}_s0_{idx}"
    s1 = f"notchainsucc_{a}_{b}_s1_{idx}"
    s2 = f"notchainsucc_{a}_{b}_s2_{idx}"
    abs = f"notchainsucc_{a}_{b}_sabs_{idx}"
    transitions = [(s0, a, s1), (s1, b, s2), (s1, a, s1)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s0, act, s0))
        if act not in (a, b):
            transitions.append((s1, act, s0))
    return {
        "name": f"notchainsuccession_{a}_{b}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_notcoexistence(a, b, idx, all_acts):
    s0 = f"notcoex_{a}_{b}_s0_{idx}"
    s1 = f"notcoex_{a}_{b}_s1_{idx}"
    s2 = f"notcoex_{a}_{b}_s2_{idx}"
    s3 = f"notcoex_{a}_{b}_s3_{idx}"
    abs = f"notcoex_{a}_{b}_sabs_{idx}"
    transitions = [(s0, b, s1), (s0, a, s2), (s1, a, s3), (s2, b, s3)]
    for act in all_acts:
        transitions.append((s3, act, s3))
        if act != a:
            transitions.append((s1, act, s1))
        if act != b:
            transitions.append((s2, act, s2))
        if act not in (a, b):
            transitions.append((s0, act, s0))
    return {
        "name": f"notcoexistence_{a}_{b}_{idx}",
        "states": [s0, s1, s2, s3, abs],
        "init": s0,
        "final": [s0, s1, s2],
        "transitions": transitions,
        "abstract": abs,
    }


def automaton_exactlyone(a, idx, all_acts):
    s0 = f"ex1_{a}_s0_{idx}"
    s1 = f"ex1_{a}_s1_{idx}"
    s2 = f"ex1_{a}_s2_{idx}"
    transitions = [(s0, a, s1), (s1, a, s2)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s0, act, s0))
            transitions.append((s1, act, s1))
    return {
        "name": f"exactlyone_{a}_{idx}",
        "states": [s0, s1, s2],
        "init": s0,
        "final": s1,
        "transitions": transitions,
    }


def automaton_atmost1(a, idx, all_acts):
    s0 = f"atm1_{a}_s0_{idx}"
    s1 = f"atm1_{a}_s1_{idx}"
    s2 = f"atm1_{a}_s2_{idx}"
    abs = f"atm1_{a}_sabs_{idx}"
    transitions = [(s0, a, s1), (s1, a, s2)]
    for act in all_acts:
        transitions.append((s2, act, s2))
        if act != a:
            transitions.append((s0, act, s0))
            transitions.append((s1, act, s1))
    return {
        "name": f"atmost1_{a}_{idx}",
        "states": [s0, s1, s2, abs],
        "init": s0,
        "final": [s0, s1],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_atmost2(a, idx, all_acts):
    s0 = f"atm2_{a}_s0_{idx}"
    s1 = f"atm2_{a}_s1_{idx}"
    s2 = f"atm2_{a}_s2_{idx}"
    s3 = f"atm2_{a}_s3_{idx}"
    abs = f"atm2_{a}_sabs_{idx}"
    transitions = [(s0, a, s1), (s1, a, s2), (s2, a, s3)]
    for act in all_acts:
        transitions.append((s3, act, s3))
        if act != a:
            transitions.append((s0, act, s0))
            transitions.append((s1, act, s1))
            transitions.append((s2, act, s2))
    return {
        "name": f"atmost2_{a}_{idx}",
        "states": [s0, s1, s2, s3, abs],
        "init": s0,
        "final": [s0, s1, s2],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_atmost3(a, idx, all_acts):
    s0 = f"atm3_{a}_s0_{idx}"
    s1 = f"atm3_{a}_s1_{idx}"
    s2 = f"atm3_{a}_s2_{idx}"
    s3 = f"atm3_{a}_s3_{idx}"
    s4 = f"atm3_{a}_s4_{idx}"
    abs = f"atm3_{a}_sabs_{idx}"
    transitions = [(s0, a, s1), (s1, a, s2), (s2, a, s3), (s3, a, s4)]
    for act in all_acts:
        transitions.append((s4, act, s4))
        if act != a:
            transitions.append((s0, act, s0))
            transitions.append((s1, act, s1))
            transitions.append((s2, act, s2))
            transitions.append((s3, act, s3))
    return {
        "name": f"atmost2_{a}_{idx}",
        "states": [s0, s1, s2, s3, s4, abs],
        "init": s0,
        "final": [s0, s1, s2, s3],
        "transitions": transitions,
        "abstract": abs,
    }

def automaton_prefix(idx, activities, all_acts):

    n = len(activities)

    states = [f"pre_s{i}_{idx}" for i in range(n + 2)]

    sink = states[n+1]
    final = states[n]
    transitions = []
    for j in range(n):
        transitions.append((states[j], activities[j], states[j+1]))

    for i in range(n):   
        for act in all_acts:
            if act != activities[i]:
                transitions.append((states[i], act, sink))

    for act in all_acts:
        transitions.append((final, act, final))
        transitions.append((sink, act, sink))

    return {
        "name": f"prefix_{idx}",
        "states": states,
        "init": states[0],
        "final": final,
        "transitions": transitions,
}

def automaton_suffix(idx, activities, all_acts):

    n = len(activities)

    states = [f"suf_s{i}_{idx}" for i in range(n + 2)]

    sink = states[n+1]
    final = states[n]
    transitions = []
    for j in range(n):
        transitions.append((states[j], activities[j], states[j+1]))

    for i in range(1,n):   
        for act in all_acts:
            if act != activities[i]:
                transitions.append((states[i], act, sink))

    for act in all_acts:
        transitions.append((final, act, sink))
        transitions.append((sink, act, sink))
        if act!=activities[0]:
            transitions.append((states[0], act, states[0]))

    return {
        "name": f"suffix_{idx}",
        "states": states,
        "init": states[0],
        "final": final,
        "transitions": transitions,
}

def automaton_pattern(idx, activities, all_acts):

    n = len(activities)

    states = [f"pat_s{i}_{idx}" for i in range(n + 1)]

    init = states[0]
    final = states[n]
    transitions = []
    for j in range(n):
        transitions.append((states[j], activities[j], states[j+1]))

    for i in range(1,n):   
        for act in all_acts:
            if act != activities[i]:
                transitions.append((states[i], act, init))

    for act in all_acts:
        transitions.append((final, act, final))
        if act!=activities[0]:
            transitions.append((init, act, init))

    return {
        "name": f"pattern_{idx}",
        "states": states,
        "init": init,
        "final": final,
        "transitions": transitions,
}

def automaton_pattern_gap(idx, activities, all_acts):

    n = len(activities)

    states = [f"patg_s{i}_{idx}" for i in range(n + 1)]

    init = states[0]
    final = states[n]
    transitions = []
    for j in range(n):
        transitions.append((states[j], activities[j], states[j+1]))

    for i in range(n):   
        for act in all_acts:
            if act != activities[i]:
                transitions.append((states[i], act, states[i]))

    for act in all_acts:
        transitions.append((final, act, final))

    return {
        "name": f"pattern_gap_{idx}",
        "states": states,
        "init": init,
        "final": final,
        "transitions": transitions,
}

def automaton_minlen(idx, A, all_acts):
    len=int(A)

    states = [f"min_s{i}_{idx}" for i in range(len+1)]

    init = states[0]
    final = states[len]

    transitions = []

    for j in range(len):
        for act in all_acts:
            transitions.append((states[j], act, states[j+1]))
    
    for act in all_acts:
        transitions.append((final, act, final))

    return {
        "name": f"minlen_{idx}",
        "states": states,
        "init": init,
        "final": final,
        "transitions": transitions,
}

def declare_factory(constraint, idx, alphabet):
    ctype = constraint["type"]
    if "activities" in constraint:
        acts = constraint.get("activities", [])
    A = constraint.get("act1")
    B = constraint.get("act2")
    C = constraint.get("act3")

    mapping = {
        "existence": lambda: automaton_existence(A, idx, alphabet),
        "init": lambda: automaton_init(A, idx, alphabet),
        "end": lambda: automaton_end(A, idx, alphabet),
        "exactly_one": lambda: automaton_exactlyone(A, idx, alphabet),
        "atmost1": lambda: automaton_atmost1(A, idx, alphabet),
        "atmost2": lambda: automaton_atmost2(A, idx, alphabet),
        "atmost3": lambda: automaton_atmost3(A, idx, alphabet),
        "absence": lambda: automaton_absence(A, idx, alphabet),
        "response": lambda: automaton_response(A, B, idx, alphabet),
        "precedence": lambda: automaton_precedence(A, B, idx, alphabet),
        "succession": lambda: automaton_succession(A, B, idx, alphabet),
        "notresponse": lambda: automaton_notsuccession(A, B, idx, alphabet),
        "notprecedence": lambda: automaton_notsuccession(A, B, idx, alphabet),
        "notsuccession": lambda: automaton_notsuccession(A, B, idx, alphabet),
        "alternateresponse": lambda: automaton_altresponse(A, B, idx, alphabet),
        "alternateprecedence": lambda: automaton_altprecedence(A, B, idx, alphabet),
        "alternatesuccession": lambda: automaton_altsuccession(A, B, idx, alphabet),
        "chainresponse": lambda: automaton_chain_response(A, B, idx, alphabet),
        "chainprecedence": lambda: automaton_chain_precedence(A, B, idx, alphabet),
        "chainsuccession": lambda: automaton_chain_succession(A, B, idx, alphabet),
        "notchainresponse": lambda: automaton_notchainsucc(A, B, idx, alphabet),
        "notchainprecedence": lambda: automaton_notchainsucc(A, B, idx, alphabet),
        "notchainsuccession": lambda: automaton_notchainsucc(A, B, idx, alphabet),
        "choice": lambda: automaton_choice(A, B, idx, alphabet),
        "exclusivechoice": lambda: automaton_exclusivechoice(A, B, idx, alphabet),
        "respondedexistence": lambda: automaton_respondedexistence(A, B, idx, alphabet),
        "br_respondedexistence": lambda: automaton_branchrespondedexistence(A, B, C, idx, alphabet),
        "coexistence": lambda: automaton_coexistence(A, B, idx, alphabet),
        "notcoexistence": lambda: automaton_notcoexistence(A, B, idx, alphabet),
        "notresponded_existence": lambda: automaton_notcoexistence(A, B, idx, alphabet),
        "prefix": lambda: automaton_prefix(idx, acts, alphabet),
        "suffix": lambda: automaton_suffix(idx, acts, alphabet),
        "pattern": lambda: automaton_pattern(idx, acts, alphabet),
        "patterngap": lambda: automaton_pattern_gap(idx, acts, alphabet),
        "minlen": lambda: automaton_minlen(idx, A, alphabet),
    }

    if ctype not in mapping:
        raise ValueError(f"Unsupported Declare constraint: {ctype}")

    return mapping[ctype]()