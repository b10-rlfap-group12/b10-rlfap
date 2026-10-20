<p align="center">
  <img src="assets/B10_banner_animated.svg" alt="B10 · RLFAP · MiniZinc banner" width="100%">
</p>

<h1 align="center">B10 · Radio Link Frequency Assignment (RLFAP)</h1>

<p align="center">
  <b>Constraint programming with MiniZinc, a comparison of search heuristics and solver backends, and validation on the official CELAR benchmark.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/MiniZinc-2.9.3-0B6E99" alt="MiniZinc">
  <img src="https://img.shields.io/badge/Gecode-6.3.0-2E7D32" alt="Gecode">
  <img src="https://img.shields.io/badge/HiGHS-1.15.1-7B1FA2" alt="HiGHS">
  <img src="https://img.shields.io/badge/Verified-30%2F30-brightgreen" alt="Verified runs">
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License">
</p>

---

## 📑 Table of Contents

1. [🎯 Overview](#-overview)
2. [❓ The Problem in Simple Words](#-the-problem-in-simple-words)
3. [✨ Key Features](#-key-features)
4. [🗂️ Repository Structure](#️-repository-structure)
5. [⚙️ Setup](#️-setup)
6. [▶️ How to Run](#️-how-to-run)
7. [📊 Results](#-results)
8. [🖼️ Figures](#️-figures)
9. [🔍 Verification](#-verification)
10. [🧪 Official CELAR Validation](#-official-celar-validation)
11. [🧭 Reproducibility Rules](#-reproducibility-rules)
12. [👥 Team](#-team)
13. [📚 References](#-references)

---

## 🎯 Overview

This project solves the **Radio Link Frequency Assignment Problem (RLFAP)**. Mobile towers need channels, and nearby towers must not use channels that are too close together. The project:

- 🧩 writes a **weighted MiniZinc model** of the problem,
- ⚔️ compares **two Gecode search heuristics** and **the HiGHS backend** on the same instances,
- ✅ **checks every reported solution** with an independent Python program,
- 🏛️ validates the model on the **official CELAR benchmark**,
- 📝 reports results honestly, including the cases where the expected improvement did not happen.

---

## ❓ The Problem in Simple Words

| Question | Answer |
|---|---|
| 📡 What is a radio link? | A connection between two towers that uses one channel (frequency). |
| 💥 What goes wrong? | Two nearby links on the same or very close channels interfere, and calls break. |
| 🎯 What do we want? | Give each link a channel so that the total interference is as small as possible. |
| 🤔 Why a computer? | With many links, the number of possible assignments is too large to check by hand. |

---

## ✨ Key Features

| Icon | Feature | Where to find it |
|:---:|---|---|
| 🧠 | Compact weighted MiniZinc model | `models/rlfap_core.mzn` |
| 🔀 | Two search heuristics (`first_fail`, `input_order`) | `models/model_first_fail.mzn`, `models/model_input_order.mzn` |
| 🧮 | Second backend, HiGHS (MIP) | `models/model_default.mzn` |
| 🎲 | Reproducible synthetic instances (fixed seeds) | `src/gen_instances.py` |
| 🛡️ | Independent solution checker | `src/check_solutions.py` |
| 🏛️ | Official CELAR validation | `src/validate_celar.py` |
| 📈 | Summaries, plots and figures | `src/analyze_results.py`, `src/plot.py`, `src/make_figures.py` |
| 🚦 | Backend preflight check (stops early if a solver is missing) | `src/run.py` |

---

## 🗂️ Repository Structure

```text
b10-rlfap/
├── 📁 assets/              Banner used in this README
├── 📁 models/              MiniZinc models (shared core + search variants + HiGHS)
├── 📁 data/
│   ├── 📁 dzn/             10 synthetic instances (generated, seeded)
│   └── 📁 raw/celar/       Official CELAR model and 10 public instances
├── 📁 src/                 Python scripts (generate, run, check, analyse, plot)
├── 📁 results/
│   ├── 📄 results.csv              All 30 synthetic runs
│   ├── 📄 verification.csv         Independent check of every solution
│   ├── 📄 summary.txt              Status counts, timing, comparisons
│   ├── 📄 celar_validation.csv     Official CELAR results
│   ├── 📁 raw/                     Full solver output (synthetic)
│   ├── 📁 raw_celar/               Full solver output (CELAR)
│   ├── 📁 plots/                   Charts
│   └── 📁 figures/                 Figures for the report
├── 📁 report/              Paper draft and validation report
├── 📄 Makefile             One-line commands
├── 📄 setup_linux.sh       Installs MiniZinc and Python environment
├── 📄 requirements.txt     Python packages
└── 📄 BACKEND_SETUP.md     How to enable the HiGHS backend
```

---

## ⚙️ Setup

> 💡 Tested on Ubuntu Linux with MiniZinc 2.9.3.

**1. Install MiniZinc and Python environment**

```bash
bash setup_linux.sh
source .venv/bin/activate
```

**2. Enable the HiGHS backend** (one-time step)

Follow [`BACKEND_SETUP.md`](BACKEND_SETUP.md). Check it with:

```bash
minizinc --solvers    # HiGHS and Gecode should both appear
```

---

## ▶️ How to Run

| Step | Command | Time | What it does |
|:---:|---|:---:|---|
| 1️⃣ | `make generate` | seconds | Creates the 10 synthetic instances |
| 2️⃣ | `make run` | ~15–20 min | Runs 30 experiments (3 configurations × 10 instances) |
| 3️⃣ | `make analyze` | seconds | Writes `results/summary.txt` |
| 4️⃣ | `make plot` | seconds | Writes the plots |
| 5️⃣ | `make check` | seconds | Verifies every solution, expects `verified=30/30` |
| 6️⃣ | `make validate-celar` | ~5 min | Runs the official CELAR instances |

Quick check on an existing result set (under a minute):

```bash
make check && head -20 results/summary.txt
```

---

## 📊 Results

### 🏁 Status and time (30 synthetic runs, 30 s limit)

| ⚙️ Configuration | ✅ Optimal | ⏱️ Limit reached | 📉 Median (s) | 📈 Max (s) |
|---|:---:|:---:|:---:|:---:|
| Gecode, `first_fail` | 8 | 2 | 0.570 | 30.073 |
| Gecode, `input_order` | 9 | 1 | 0.513 | 30.067 |
| HiGHS, default | **10** | 0 | 1.737 | 14.811 |

### 🔑 Key findings

- 🟢 **HiGHS proved an optimum on all 10 synthetic instances.**
- 🟢 **Wherever two or more configurations proved optimality, they agree.**
- 🟡 **`input_order` is clearly faster on the 30- and 40-link instances.**
- 🔴 **`first_fail` did not improve on `input_order` in general.** It was faster on one instance only (110 links), and that gap is within run-to-run noise.
- 🟠 **The official CELAR instances return feasible solutions within 30 s, but none is proven optimal.**

---

## 🖼️ Figures

| Figure | What it shows |
|---|---|
| 🔄 **Fig. 1** Workflow | The pipeline from model to figures |
| 🟩 **Fig. 2** Status heatmap | Status and time for each instance and configuration |
| ⚖️ **Fig. 3** Paired comparison | `first_fail` vs `input_order` time per instance |
| ⏳ **Fig. 4** Solve time vs size | Runtime is not monotonic in size |
| 🎯 **Fig. 5** Objective vs size | Solution quality; time-limited values are upper bounds |
| ✔️ **Fig. 6** Agreement | Proven optima agree across configurations |

All figures are in `results/figures/` and `results/plots/`.

---

## 🔍 Verification

Every reported solution is checked **outside** the solver:

- ✅ each frequency is inside the allowed band,
- ✅ every interference indicator is recomputed from the instance data,
- ✅ every duplex equality holds,
- ✅ the weighted objective is recomputed and compared.

A failed solver run is reported as an **error**, never as a pass.

Current result: **`verified=30/30`, `failures=0`.**

---

## 🧪 Official CELAR Validation

| 🧩 Check | Result |
|---|:---:|
| Schema valid | 10 / 10 |
| Feasible solution returned | 10 / 10 |
| Proven optimal | 0 / 10 |

> ⚠️ All CELAR values are **best values found within 30 s**, so they are upper bounds, not optimal values. Repeated runs can give slightly different values.

---

## 🧭 Reproducibility Rules

- 🔢 Every synthetic instance has a **recorded seed**.
- 🧾 Every run records **solver version, MiniZinc version, time limit and status**.
- 🧷 Raw solver output is **kept** in `results/raw/` and `results/raw_celar/`.
- 🚫 `OPTIMAL` is only written when the solver **proves** it.
- 🖥️ Timings depend on the machine. Compare runs on the same hardware.

---

## 👥 Team

| 👤 Member | 🏷️ Role |
|---|---|
| **Mohammed Saif Al Sabah** | Model, experiments, paper |
| **Fokrul Islam** | Instances, validation, repository |

📘 **Course:** CSE-3214, Artificial Intelligence Laboratory
🏫 **Department:** Computer Science and Engineering, BAUET, Natore
👨‍🏫 **Instructor:** Pollob Chandra Ray

---

## 📚 References

1. C. Cabon, S. de Givry, L. Lobjois, T. Schiex, and J. P. Warners, "Radio link frequency assignment," *Constraints*, vol. 4, no. 1, pp. 79–89, 1999.
2. N. Nethercote, P. J. Stuckey, R. Becket, S. Brand, G. J. Duck, and G. Tack, "MiniZinc: Towards a standard CP modelling language," *CP 2007*, LNCS vol. 4741, pp. 529–543.
3. MiniZinc benchmarks repository: https://github.com/MiniZinc/minizinc-benchmarks
4. C. Schulte, G. Tack, and M. Z. Lagerkvist, "Gecode: Generic constraint development environment," https://www.gecode.org
5. HiGHS: High performance software for linear optimization, https://highs.dev

---

<p align="center">
  ⭐ If this project helped you, consider starring the repository. ⭐<br>
  <sub>Made with MiniZinc, Gecode, HiGHS and a lot of coffee ☕</sub>
</p>
