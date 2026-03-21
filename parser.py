import csv
import json
import re

def parse_declare_decl(path):
    pattern = re.compile(r'(?P<template>[A-Za-z ]+)\[(?P<acts>[^\]]+)\]')

    constraints = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if "[" not in line or "]" not in line:
                continue

            match = pattern.search(line)
            if not match:
                continue

            template = match.group("template").strip().lower().replace(" ", "")

            acts = [
                normalize_name(a.strip())
                for a in match.group("acts").split(",")
            ]

            if len(acts) > 2:
                constraints.append({
                    "type": template,
                    "activities": acts
                })
            else:
                constraints.append({
                    "type": template,
                    "act1": acts[0] if len(acts) > 0 else None,
                    "act2": acts[1] if len(acts) > 1 else None
                })

    return constraints

def parse_declare_json(path):
    constraints = []

    preferences_templates = {"patterngap", "pattern", "prefix", "suffix"}  

    with open(path) as f:
        data = json.load(f)

    for c in data.get("constraints", []):
        constraint_type = c["template"].strip().lower()
        parameters = c.get("parameters", [])

        acts = [normalize_name(p.strip()) for group in parameters for p in group]

        if constraint_type in preferences_templates:
            constraints.append({
                "type": constraint_type,
                "activities": acts
            })
        else:
            act1 = acts[0] if len(acts) > 0 else None
            act2 = acts[1] if len(acts) > 1 else None
            act3 = acts[2] if len(acts) > 2 else None 

            constraints.append({
                "type": constraint_type,
                "act1": act1,
                "act2": act2,
                "act3":act3
            })

    return constraints

def normalize_name(name):
    if name is None:
        return None
    name = name.strip().lower()
    name = name.replace(" ", "_")          
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def extract_alphabet(constraints):
    alphabet = set()

    for c in constraints:
        if c.get("type") == "minlen":
            continue
        if "activities" in c:
            alphabet.update(c["activities"])
        else:
            if c.get("act1"):
                alphabet.add(c["act1"])
            if c.get("act2"):
                alphabet.add(c["act2"])
            if c.get("act3"):
                alphabet.add(c["act3"])

    return list(alphabet)

def filter_absence_constraints(constraints):
    activity_constraints = {}

    for c in constraints:
        if "activities" in c:
            acts = c["activities"]
        else:
            acts = [c.get("act1"), c.get("act2"), c.get("act3")]
        for act in acts:
            if act:
                activity_constraints.setdefault(act, set()).add(c["type"])

    filtered = []
    for c in constraints:
        if c["type"] == "absence":
            if "activities" in c:
                acts = c["activities"]
            else:
                acts = [c.get("act1"), c.get("act2"), c.get("act3")]

            skip = False
            for act in acts:
                if act and len(activity_constraints[act] - {"absence"}) > 0:
                    skip = True
                    break
            if skip:
                continue
        filtered.append(c)

    return filtered