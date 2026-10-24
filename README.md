

<h1 align="center">B10 · RLFAP · MiniZinc</h1>

<p align="center">
  <strong>Radio Link Frequency Assignment with Constraint Programming, Solver Comparison & CELAR Validation</strong>
</p>

<p align="center">
  <a href="#-overview"><img src="https://img.shields.io/badge/Project-RLFAP-0EA5A8?style=flat-square" alt="Project"></a>
  <a href="#-setup"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="#-setup"><img src="https://img.shields.io/badge/MiniZinc-2.9.3-0B6E99?style=flat-square" alt="MiniZinc"></a>
  <img src="https://img.shields.io/badge/Gecode-6.3.0-2E7D32?style=flat-square" alt="Gecode">
  <img src="https://img.shields.io/badge/HiGHS-1.15.1-7B1FA2?style=flat-square" alt="HiGHS">
  <img src="https://img.shields.io/badge/Verified-30%2F30-brightgreen?style=flat-square" alt="Verified runs">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License">
</p>

<p align="center">
  <a href="#-overview">Overview</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-setup">Setup</a> ·
  <a href="#-experiments">Experiments</a> ·
  <a href="#-results">Results</a> ·
  <a href="#-team">Team</a>
</p>

---

## ◈ Project Identity

| Field | Details |
|:--|:--|
| **Course** | CSE-3214 — Artificial Intelligence Laboratory |
| **Project code** | B10 |
| **Group** | 12 |
| **Department** | Computer Science and Engineering (CSE) |
| **Academic level** | 3rd Year, 2nd Semester · Even Section |
| **Institution** | Bangladesh Army University of Engineering & Technology (BAUET) |
| **Instructor** | Pollob Chandra Ray |
| **Member 01** | Mohammed Saif Al Sabah — `0812320205101026` |
| **Member 02** | Fokrul Islam — `0812320205101044` |

> **Project goal:** assign frequency channels to radio links so that weighted interference violations are minimised while respecting frequency-band and duplex constraints.

---

## ▣ Table of Contents

- [Overview](#-overview)
- [The Problem in Simple Words](#-the-problem-in-simple-words)
- [Research Question](#-research-question)
- [Features](#-features)
- [Repository Structure](#-repository-structure)
- [Setup](#-setup)
- [Experiments](#-experiments)
- [Official CELAR Validation](#-official-celar-validation)
- [Verification](#-verification)
- [Results](#-results)
- [Figures and Reports](#-figures-and-reports)
- [Interpretation Rules](#-interpretation-rules)
- [Reproducibility Rules](#-reproducibility-rules)
- [Team](#-team)
- [References](#-references)

---

## ◎ Overview

The **Radio Link Frequency Assignment Problem (RLFAP)** is a constraint-optimization problem from telecommunications. Each radio link needs a frequency, but nearby or interfering links cannot use channels that are too close together.

This repository provides a complete, reproducible study that:

- models a weighted RLFAP in **MiniZinc**;
- compares two Gecode search heuristics: `first_fail` and `input_order`;
- compares the constraint-programming model with the **HiGHS MIP backend**;
- generates ten seeded synthetic instances with increasing difficulty;
- independently verifies every reported synthetic solution;
- validates the workflow against ten official CELAR benchmark instances;
- stores raw solver output, CSV results, plots, reports and demo assets;
- reports limitations honestly, including time-limited `FEASIBLE` results.

---

## ◌ The Problem in Simple Words

| Question | Answer |
|:--|:--|
| **What is a radio link?** | A communication connection between two towers that uses one frequency channel. |
| **What goes wrong?** | Nearby links using equal or closely separated frequencies can interfere. |
| **What do we want?** | Assign frequencies so that total weighted interference is as small as possible. |
| **Why use optimization?** | With many links, the possible assignments become too large to check manually. |
| **Why is this a complex engineering problem?** | It combines a finite resource, many coupled constraints, competing objectives and solver-dependent scalability. |

### Core engineering idea

```text
Radio links + interference distances + finite frequency band
                         ↓
              Constraint optimization model
                         ↓
             Low-violation frequency assignment
```

---

## ⁙ Research Question

> How do the `first_fail` and `input_order` search heuristics, and the choice of Gecode (CP) versus HiGHS (MIP), affect solve time and solution quality for weighted RLFAP instances?

The study separates three issues clearly:

1. **Model quality** — whether the constraints represent the intended RLFAP logic.
2. **Search behaviour** — whether variable-ordering heuristics improve convergence.
3. **Backend behaviour** — whether CP and MIP solvers scale differently on the same experimental family.

---

## ✦ Features

| Icon | Capability | Project location |
|:---:|:--|:--|
| ◈ | Weighted MiniZinc RLFAP model with interference and duplex equality | `models/rlfap_core.mzn` |
| ⇄ | `first_fail` and `input_order` search variants | `models/model_first_fail.mzn` · `models/model_input_order.mzn` |
| ◇ | HiGHS MIP-compatible backend model | `models/model_default.mzn` |
| ⌁ | Seeded synthetic instance generator | `src/gen_instances.py` |
| ⛨ | Independent solution checker | `src/check_solutions.py` |
| ⌘ | Official CELAR model and public instances | `data/raw/celar/` |
| ⊙ | Backend preflight and experiment runner | `src/run.py` |
| ▦ | Result analysis, summaries and plots | `src/analyze_results.py` · `src/plot.py` |
| ▤ | Instance statistics report | `src/summarize_instances.py` |
| ▣ | IEEE-style paper and editable Word report | `report/` |
| ▶ | Silent live-demo walkthrough | `demo/B10_RLFAP_Live_Demo.mp4` |

---

## ⌘ Repository Structure

```text
b10_rlfap_backend_project/
├── assets/
│   └── rlfap-banner.svg             # Self-contained animated README banner
├── models/
│   ├── rlfap_core.mzn               # Shared weighted MiniZinc model
│   ├── model_first_fail.mzn         # Gecode first_fail search
│   ├── model_input_order.mzn        # Gecode input_order search
│   └── model_default.mzn            # HiGHS/MIP-compatible model
├── data/
│   ├── dzn/                         # 10 seeded synthetic instances
│   └── raw/celar/                   # Official CELAR model and instances
├── src/
│   ├── gen_instances.py             # Synthetic data generator
│   ├── run.py                       # Multi-backend experiment runner
│   ├── check_solutions.py           # Independent solution verification
│   ├── validate_celar.py            # Official CELAR validation
│   ├── mzn_parse.py                 # Solver output and status parser
│   ├── analyze_results.py           # Summaries and paired comparisons
│   ├── plot.py                      # Result plots
│   ├── summarize_instances.py       # Dataset statistics table
│   └── make_figures.py              # Report figures
├── results/
│   ├── results.csv                  # Synthetic experiment results
│   ├── verification.csv             # Independent verification results
│   ├── celar_validation.csv         # Official CELAR results
│   ├── instance_statistics.csv      # Dataset statistics
│   ├── summary.txt                  # Human-readable result summary
│   ├── raw/                         # Full synthetic solver output
│   ├── raw_celar/                   # Full CELAR solver output
│   ├── plots/                       # Charts
│   └── figures/                     # Paper figures
├── report/
│   ├── IEEE_RLFAP_Paper.pdf         # Six-page two-column paper
│   ├── IEEE_RLFAP_Paper.docx        # Editable Word paper
│   ├── IEEE_RLFAP_Paper_WordPreview.pdf
│   ├── paper_draft.md
│   └── dataset_validation.md
├── demo/
│   └── B10_RLFAP_Live_Demo.mp4
├── Makefile
├── setup_linux.sh
├── requirements.txt
├── BACKEND_SETUP.md
└── README.md
```

---

## ⚙ Setup

### Quick Start — Linux / Ubuntu

> Tested on Ubuntu Linux with MiniZinc 2.9.3.

```bash
# 1. Enter the extracted project directory
cd b10_rlfap_backend_project

# 2. Install system dependencies
sudo apt update
sudo apt install -y minizinc python3 python3-venv python3-pip

# 3. Create and activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install Python dependencies
python -m pip install -r requirements.txt

# 5. Confirm the installation
python3 --version
minizinc --version
minizinc --solvers
```

### Enable HiGHS

HiGHS is an optional second backend. Follow [`BACKEND_SETUP.md`](BACKEND_SETUP.md), then confirm that both Gecode and HiGHS are visible:

```bash
minizinc --solvers
```

If a required backend is missing, `src/run.py` performs a preflight check and stops early instead of producing misleading results.

---

## ▶ Experiments

### Standard reproducible sequence

| Order | Command | Expected time | Purpose |
|:---:|:--|:--:|:--|
| 01 | `make generate` | seconds | Create 10 seeded synthetic instances |
| 02 | `make run` | about 15–20 minutes | Run 30 configurations with a 30 s limit |
| 03 | `make analyze` | seconds | Write `results/summary.txt` |
| 04 | `make plot` | seconds | Generate plots and figures |
| 05 | `make check` | seconds | Independently verify every solution |
| 06 | `make validate-celar` | about 5 minutes | Run official CELAR validation |

```bash
make generate
make run
make analyze
make plot
make check
make validate-celar
```

### Quick check on existing results

```bash
make check
head -20 results/summary.txt
```

### Individual Python commands

```bash
python3 src/gen_instances.py
python3 src/run.py
python3 src/analyze_results.py
python3 src/plot.py
python3 src/check_solutions.py
python3 src/validate_celar.py --solver Gecode --time-limit 30
```

---

## ⛨ Official CELAR Validation

The project includes the original CELAR model and ten public benchmark instances. CELAR validation is reported separately from the compact synthetic model because the official model uses its own domain and category semantics.

```bash
make validate-celar
cat results/celar_validation.csv
```

### Included validation summary

| Check | Result |
|:--|:--:|
| Schema valid | 10 / 10 |
| Feasible solution returned | 10 / 10 |
| Proven optimal | 0 / 10 |

> **Important:** Every included CELAR run reached the 30-second limit with a `FEASIBLE` result. These objective values are best values found within the time limit and must be treated as upper bounds, not proven optima. Repeated runs can vary slightly by machine and solver build.

Details are documented in [`report/dataset_validation.md`](report/dataset_validation.md).

---

## ✓ Verification

Every reported synthetic solution is checked outside the solver by `src/check_solutions.py`.

The checker recomputes:

- whether each frequency lies inside the permitted band;
- every interference indicator from the instance data;
- every duplex equality constraint;
- the weighted objective value;
- the consistency between the solver output and the recorded CSV row.

A failed solver run is reported as an error, never as a pass.

```text
Current verified result: 30 / 30
Failures: 0
```

---

## 📈 Results

### Status and time — 30 synthetic runs, 30-second limit

| Configuration | Proven optimal | Limit reached | Median time (s) | Maximum time (s) |
|:--|:--:|:--:|--:|--:|
| Gecode · `first_fail` | 8 | 2 | 0.570 | 30.073 |
| Gecode · `input_order` | 9 | 1 | 0.513 | 30.067 |
| HiGHS · default | **10** | 0 | 1.737 | 14.811 |

### Key findings

- **HiGHS proved an optimum on all 10 synthetic instances.**
- Wherever two or more configurations proved optimality, their objective values agree.
- `input_order` is faster on the 30- and 40-link instances in this experiment.
- `first_fail` did not improve on `input_order` in general; it was faster on only one instance, and that gap is within run-to-run noise.
- Official CELAR instances returned feasible solutions within 30 seconds, but none was proven optimal.

### Status meanings

| Status | Meaning |
|:--|:--|
| `OPTIMAL` | The solver proved optimality within the time limit. |
| `FEASIBLE` | A valid solution was found, but optimality was not proven. The objective is an upper bound. |
| `UNKNOWN` | No solution was found within the time limit. |
| `FAILED` | The solver returned an error or could not complete the run. |

Never describe a time-limited `FEASIBLE` result as optimal.

---

## ◫ Figures and Reports

| Asset | Description |
|:--|:--|
| `results/figures/` | Figures prepared for the report |
| `results/plots/` | Runtime, objective and scalability charts |
| `report/IEEE_RLFAP_Paper.pdf` | Six-page two-column IEEE-style paper |
| `report/IEEE_RLFAP_Paper.docx` | Editable Word version of the paper |
| `report/IEEE_RLFAP_Paper_WordPreview.pdf` | Rendered Word-document preview |
| `report/paper_draft.md` | Full paper draft and discussion |
| `report/dataset_validation.md` | CELAR dataset validation evidence |
| `demo/B10_RLFAP_Live_Demo.mp4` | 29-second silent project walkthrough |

The six main report figures cover:

1. reproducible workflow;
2. status heatmap;
3. paired `first_fail` versus `input_order` comparison;
4. solve time versus instance size;
5. objective versus instance size;
6. agreement between proven optima.

---

## ⌁ Interpretation Rules

- Synthetic results test the compact project model on generated instances; they are not field measurements from a live network.
- Official CELAR results use the original CELAR model and are reported separately.
- Every comparison should report solver version, MiniZinc version, machine, time limit, dataset source and seed.
- Gecode heuristic comparisons are not identical searches across both backends; HiGHS uses no Gecode search annotation.
- Runtime is machine-dependent. Compare configurations on the same machine whenever possible.

---

## ⛓ Reproducibility Rules

- Every synthetic instance has a recorded seed.
- Every run records solver version, MiniZinc version, time limit and status.
- Raw solver output is retained in `results/raw/` and `results/raw_celar/`.
- `OPTIMAL` is recorded only when the solver proves optimality.
- The independent checker is run outside the solver.
- Synthetic and official CELAR experiments remain separate.
- Model assumptions and conversion decisions are documented in the paper and validation report.

---

## 👥 Team

| Member | Responsibility |
|:--|:--|
| **Mohammed Saif Al Sabah** | Model, experiments and paper |
| **Fokrul Islam** | Instances, validation and repository |

**Course:** CSE-3214, Artificial Intelligence Laboratory  
**Department:** Computer Science and Engineering, BAUET, Natore  
**Instructor:** Pollob Chandra Ray  
**Group:** 12 · 3rd Year · 2nd Semester · Even Section

---

## 📚 References

1. C. Cabon, S. de Givry, L. Lobjois, T. Schiex, and J. P. Warners, “Radio link frequency assignment,” *Constraints*, vol. 4, no. 1, pp. 79–89, 1999.
2. N. Nethercote, P. J. Stuckey, R. Becket, S. Brand, G. J. Duck, and G. Tack, “MiniZinc: Towards a standard CP modelling language,” *CP 2007*, LNCS vol. 4741, pp. 529–543.
3. MiniZinc Benchmarks Repository: <https://github.com/MiniZinc/minizinc-benchmarks>
4. C. Schulte, G. Tack, and M. Z. Lagerkvist, “Gecode: Generic constraint development environment,” <https://www.gecode.org>
5. HiGHS — High-performance software for linear optimization: <https://highs.dev>

---

<p align="center">
  <img src="https://img.shields.io/badge/Built%20with-MiniZinc%20%7C%20Gecode%20%7C%20HiGHS-0EA5A8?style=flat-square" alt="Built with MiniZinc, Gecode and HiGHS">
  <br>
  <sub>Reproducible constraint programming study · Group 12 · BAUET CSE</sub>
</p>
```
