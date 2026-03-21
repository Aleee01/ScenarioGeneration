import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta

import re

import re

def parse_sas_to_list(content):
    
    if "---BEGIN_PLANS---" not in content:
        return []
    
    plans_section = content.split("---BEGIN_PLANS---")[1].strip()
    
    raw_plan_blocks = re.split(r';\s*cost\s*=\s*\d+.*', plans_section)
    
    plans = []
    
    for block in raw_plan_blocks:
        actions = re.findall(r'\((.*?)\)', block)
        
        clean_actions = []
        
        for a in actions:
            a = re.sub(r'__###__.*', '', a).strip()
            
            match = re.search(r'\b(sync_([a-z]+(?:_[a-z]+)*)_\d+)\b', a)
            
            if match:
                central_name = match.group(2)  
                clean_actions.append(central_name)
        
        if clean_actions:
            plans.append(clean_actions)
    
    return plans

def get_unique_plans(plans):
    unique = []
    seen = set()
    
    for plan in plans:
        key = tuple(plan)
        if key not in seen:
            seen.add(key)
            unique.append(plan)
    
    return unique

def write_xes(plans, output_path):
    log = ET.Element("log", xes_version="2.0", xmlns="http://www.xes-standard.org/")
    
    ET.SubElement(log, "extension", name="Concept", prefix="concept", uri="http://www.xes-standard.org/concept.xesext")
    ET.SubElement(log, "extension", name="Time", prefix="time", uri="http://www.xes-standard.org/time.xesext")

    base_time = datetime.now()
    for i, plan_steps in enumerate(plans):
        trace = ET.SubElement(log, "trace")
        ET.SubElement(trace, "string", key="concept:name", value=f"Plan_{i+1}")
        
        for j, action in enumerate(plan_steps):
            event = ET.SubElement(trace, "event")
            ET.SubElement(event, "string", key="concept:name", value=action)
            timestamp = (base_time + timedelta(minutes=j)).strftime("%Y-%m-%dT%H:%M:%S.000+01:00")
            ET.SubElement(event, "date", key="time:timestamp", value=timestamp)

    tree = ET.ElementTree(log)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

