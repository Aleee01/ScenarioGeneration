from dataclasses import dataclass
from itertools import product, combinations
from typing import List
from collections import defaultdict

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
    states: List[str]
    init: str
    final_states: List[str]
    abstract: str = None

def group_transitions_by_label(transitions):
    grouped = defaultdict(list)
    for t in transitions:
        if t.label:
            grouped[t.label].append(t.id)
    return dict(grouped)

def generate_combinations_gen(transitions, sink_map):

    distinct_automata = set(t.automaton for t in transitions)
    m = len(distinct_automata)
    labels = set(t.label for t in transitions)

    for label in labels:
        label_transitions = [t for t in transitions if t.label == label]

        for k in range(1, min(m, len(label_transitions)) + 1):
            for combo in combinations(label_transitions, k):
                
                automata_in_combo = {t.automaton for t in combo}
                if len(automata_in_combo) != len(combo):
                    continue

                discard = False
                for t in combo:
                    if t.dest in sink_map[t.automaton]:
                        discard = True
                        break
                if discard:
                    continue

                combo_ids = {t.id for t in combo}
                extended_combo = list(combo_ids)

                for t in label_transitions:
                    if t.id not in combo_ids and t.automaton not in automata_in_combo:
                        extended_combo.append(f"not {t.id}")

                yield label, tuple(sorted(extended_combo))

def build_transition_map(transitions):
    return {t.id: t for t in transitions}

def find_sink_states(automaton, transitions):
    src_states = {t.src for t in transitions if t.automaton == automaton.name}

    sink_states = set()

    for state in automaton.states:
        if (
            state not in automaton.final_states
            and state not in src_states
        ):
            sink_states.add(state)

    return sink_states


def generate_finish_actions_gen(all_automata):
    final_lists = [list(a.final_states) for a in all_automata]
    finish_combos = product(*final_lists)
    counter = 0
    for combo in finish_combos:
        preconditions = []
        effects = ["(finished)"]
        for automaton, final_state in zip(all_automata, combo):

            preconditions.append(f"(cur_state {final_state})")
            if automaton.abstract:

                effects.append(f"(not (cur_state {final_state}))")
                effects.append(f"(cur_state {automaton.abstract})")
        action_name = f"finish_{counter}"
        counter += 1
        action_str = f"""
(:action {action_name}
 :precondition (and
    {' '.join(preconditions)}
 )
 :effect (and
    {' '.join(effects)}
 )
)
"""
        yield action_str

def generate_pddl_actions_gen(transition_map, combinations_gen):
    action_counter = 0
    for label, combo in combinations_gen:
        action_name = f"sync_{label}_{action_counter}"
        action_counter += 1

        preconditions = ["(not (finished))"]
        effects = []

        for elem in combo:
            is_negated = elem.startswith("not ")
            tid = elem.replace("not ", "")
            t = transition_map[tid]

            if is_negated:
                preconditions.append(f"(not (cur_state {t.src}))")
            else:
                preconditions.append(f"(cur_state {t.src})")
                effects.append(f"(not (cur_state {t.src}))")
                effects.append(f"(cur_state {t.dest})")

        action_str = f"""
(:action {action_name}
 :precondition (and
    {' '.join(preconditions)}
 )
 :effect (and
    {' '.join(effects)}
 )
)
"""
        yield action_str

def generate_pddl_domain_file(actions_gen, path="domain.pddl"):
    with open(path, "w") as f:
        f.write("""
(define (domain multi_automata_sync)
 (:requirements :strips)
 (:predicates
    (cur_state ?s)
    (finished)
 )
""")
        for action_str in actions_gen:
            f.write(action_str)
        f.write("\n)")
    print(f"PDDL Domain written in {path}")

def generate_pddl_problem(all_automata, path="problem.pddl"):
    objects = []
    init = []
    goals = []

    for automaton in all_automata:
        if automaton.abstract:
            goals.append(f"(cur_state {automaton.abstract})")
        else:
            goals.append(f"(cur_state {next(iter(automaton.final_states))})")
        for s in automaton.states:
            objects.append(s)
        init.append(f"(cur_state {automaton.init})")

    problem_str = f"""
(define (problem sync_problem)
(:domain multi_automata_sync)

(:objects
    {' '.join(objects)}
)

(:init
    {' '.join(init)}
)

(:goal
    (and
        {' '.join(goals)}
    )
)
)
"""
    with open(path, "w") as f:
        f.write(problem_str)
    print(f"PDDL Problem written in {path}")