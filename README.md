# Scenario Generation for Declarative Process Models

This repository provides an **integrated tool** for:

- Generating **PDDL domains and problems** from Declare models  
- Solving them using **diverse planning techniques** (Top-K, Top-Quality, Diverse)  
- Converting resulting plans into **Event Logs (XES)**  

---

## Main Features

### Model Parsing
Supports declarative process models in:
- `.json`
- `.decl`

### PDDL Generation
Automatically converts Declare constraints into:
- PDDL actions  
- Automata-based state transitions  

### Diverse Planning
Integration with the **ForbidIterative** framework to compute multiple execution paths:

- **Top-K** → Finds the *k* best plans  
- **Top-Quality (Top-Q)** → Finds plans within a given quality bound  
- **Diverse** → Finds plans that are significantly different from each other  

### Post-Processing
- Extracts SAS plans  
- Converts them into standard **XES event logs** for Process Mining analysis  

---

## Requirements and Installation

The project is fully containerized using **Docker**, which handles all dependencies (e.g., Fast Downward and ForbidIterative).

### 1. Clone the Repository

```bash
git clone <repo-url>
cd <repository-folder>
```

### 2. Build the Docker Image

```bash
docker build -t scenario-gen .
```

---

## Execution Guide

The tool is executed via CLI using Docker.  
You should mount a local volume to:
- provide input models  
- retrieve generated outputs  

### Usage

```bash
docker run --rm -v "${PWD}/outputs:/app/outputs" scenario-gen <model_path> <planner_type> [options]
```

### Arguments

- `<model_path>` → Path to the Declare model (`.json` or `.decl`)  
- `<planner_type>` → Planner type:
  - `topk`
  - `topq`
  - `diverse`

### Options

- `-n, --num-plans` → Number of plans to generate (default: 10)  
- `-b, --bound` → Quality bound (**required for topq**, must be > 1.0)  

  The quality bound is defined as a multiplicative factor over the optimal plan cost.  
  Given an optimal cost `C*`, the planner will accept solutions with cost:

  ```
  C ≤ bound × C*
  ```

  For example:
  - `bound = 1.0` → Only optimal plans  
  - `bound = 1.2` → Plans up to 20% worse than the optimal cost  

---

## Examples

### 1. Generate 10 Top-K Plans

```bash
docker run -v $(pwd)/outputs:/app/outputs scenario-gen my_model.json topk -n 10
```

### 2. Generate Plans with a Quality Bound

```bash
docker run -v $(pwd)/outputs:/app/outputs scenario-gen my_model.json topq -n 5 --bound 1.2
```

### 3. Generate Diverse Plans

```bash
docker run -v $(pwd)/outputs:/app/outputs scenario-gen my_model.json diverse -n 20
```
### Using Models from `experiments`

If you want to use input models located in the `experiments` folder (e.g., `experiments/UniversityAdmission/University.json`), you must mount **both the `experiments` folder and the `outputs` folder**. 

```bash
docker run --rm -v "${PWD}/outputs:/app/outputs" -v "${PWD}/experiments:/app/experiments" scenario-gen experiments/UniversityAdmission/University.json topk
```
---

## Credits and Dependencies

- **ForbidIterative** → Used for Top-K, Top-Quality and Diverse planning  
- **Fast Downward** → Planning engine  
