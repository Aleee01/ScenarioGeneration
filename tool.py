import argparse
import os
import sys
import subprocess
from pathlib import Path

from parser import (
    extract_alphabet,
    filter_absence_constraints,
    parse_declare_json,
    parse_declare_decl
)

from builders import declare_factory, build_automaton_from_dict

from pddl_generator import (
    group_transitions_by_label,
    build_transition_map,
    generate_combinations_gen,
    generate_pddl_actions_gen,
    generate_finish_actions_gen,
    generate_pddl_domain_file,
    generate_pddl_problem,
    find_sink_states
)
from extract_plans import parse_sas_to_list, get_unique_plans, write_xes


def validate_file(file_path):
    if not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"File not found: {file_path}")

    if not (file_path.endswith(".json") or file_path.endswith(".decl")):
        raise argparse.ArgumentTypeError(
            "The file must be .json or .decl"
        )

    return file_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scenario Generation for declarative process models"
    )

    parser.add_argument(
        "model",
        type=validate_file,
        help="Declare model (.json or .decl)"
    )

    parser.add_argument(
        "planner",
        type=str,
        help="Planner type (topk, topq, diverse)"
    )

    parser.add_argument(
        "-n", "--num-plans",
        type=int,
        default=10,
        help="Number of plans to generate (default: 10)"
    )

    parser.add_argument(
        "-b", "--bound",
        type=float,
        help="Bound (mandatory for topq planner, must be greater than 1)"
    )

    return parser.parse_args()


def validate_args(args):
    planner = args.planner.lower()

    valid_planners = ["topk", "topq", "diverse"]

    if planner not in valid_planners:
        print(f"Invalid planner: {planner}")
        print(f"Valid planners: {valid_planners}")
        sys.exit(1)

    if planner == "topq":
        if args.bound is None:
            print("Planner 'topq' requires parameter --bound")
            sys.exit(1)

        if args.bound <= 1:
            print("Bound must be greater than 1")
            sys.exit(1)


def generate_pddl(model_path, output_dir="pddl_output"):

    if model_path.endswith(".json"):
        constraints = parse_declare_json(model_path)
    elif model_path.endswith(".decl"):
        constraints = parse_declare_decl(model_path)
    else:
        raise ValueError("Invalid format (.json or .decl)")

    constraints = filter_absence_constraints(constraints)
    alphabet = extract_alphabet(constraints)

    all_automata = []
    all_transitions = []

    for idx, c in enumerate(constraints):
        definition = declare_factory(c, idx, alphabet)
        automaton, transitions = build_automaton_from_dict(definition)

        all_automata.append(automaton)
        all_transitions.extend(transitions)

    grouped = group_transitions_by_label(all_transitions)
    transition_map = build_transition_map(all_transitions)

    sink_map = {
        a.name: find_sink_states(a, all_transitions)
        for a in all_automata
    }

    comb_gen = generate_combinations_gen(all_transitions, sink_map)

    actions_gen = generate_pddl_actions_gen(transition_map, comb_gen)

    if any(len(a.final_states) > 1 for a in all_automata):
        from itertools import chain
        finish_gen = generate_finish_actions_gen(all_automata)
        actions_gen = chain(actions_gen, finish_gen)

    os.makedirs(output_dir, exist_ok=True)

    domain_path = os.path.join(output_dir, "domain.pddl")
    problem_path = os.path.join(output_dir, "problem.pddl")

    generate_pddl_domain_file(actions_gen, path=domain_path)
    generate_pddl_problem(all_automata, path=problem_path)
    print(f"\nPDDL files generated:")
    print(f" - Domain: {domain_path}")
    print(f" - Problem: {problem_path}")

    return domain_path, problem_path




def run_planner(args, domain_path, problem_path, output_dir):
    planner = args.planner.lower()
    n = args.num_plans
    b = args.bound

    scripts = {
        "topk": "/app/forbiditerative/plan_topk.sh",
        "topq": "/app/forbiditerative/plan_unordered_topq.sh",
        "diverse": "/app/forbiditerative/plan_diverse_agl.sh"
    }

    if planner not in scripts:
        raise ValueError(f"Invalid planner: {planner}")

    script = scripts[planner]

    domain_abs = os.path.abspath(domain_path)
    problem_abs = os.path.abspath(problem_path)

    if planner == "diverse":
        plans_folder = "found_plans"
    else:
        plans_folder = "found_plans/done"

    if planner == "topq":
        cmd = f"{script} {domain_abs} {problem_abs} {b} {n}"
    else:
        cmd = f"{script} {domain_abs} {problem_abs} {n}"

    full_cmd = f"""
{cmd}
echo '---BEGIN_PLANS---'
if [ -d "{plans_folder}" ]; then
    for f in {plans_folder}/sas_plan.*; do
        echo "FILE: $f"
        cat "$f"
        echo "----"
    done
fi
"""

    print(f"Running:\n{planner}")

    result = subprocess.run(
        ["bash", "-c", full_cmd], 
        capture_output=True,
        text=True,
        cwd="/app/forbiditerative"
    )

    save_outputs(result, planner, output_dir)


def save_outputs(result, planner, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"output_{planner}.txt"

    output_file = output_dir / filename

    with open(output_file, "w") as f:
        f.write(result.stdout)
        f.write("\n\n=== STDERR ===\n")
        f.write(result.stderr)

    print(f"Planner output saved in: {output_file}")

    content = result.stdout

    plans = parse_sas_to_list(content)
    plans = get_unique_plans(plans)

    if plans:
        xes_file = output_dir / (output_file.stem + ".xes")
        write_xes(plans, xes_file)
        print(f"XES generated: {xes_file}")
    else:
        print("No valid plan founded.")


def main():
    args = parse_args()
    validate_args(args)

    print("\n--- INPUT ---")
    print(f"Model: {args.model}")
    print(f"Planner: {args.planner}")
    print(f"Number of plans: {args.num_plans}")
    if args.bound:
        print(f"Qaulity bound: {args.bound}")
    print("-------------\n")

    domain_path, problem_path = generate_pddl(args.model)

    output_dir = "outputs"

    run_planner(args, domain_path, problem_path, output_dir)


if __name__ == "__main__":
    main()