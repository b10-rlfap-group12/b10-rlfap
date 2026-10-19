<p align="center">
  <img src="assets/rlfap-banner.svg" alt="RLFAP project banner" width="100%">
</p>

<h1 align="center">B10 — Radio Link Frequency Assignment</h1>
<p align="center"><strong>MiniZinc constraint programming: reproducible synthetic experiments, independent solution checking, and official CELAR validation</strong></p>

> **Project goal:** assign frequency channels to radio links so that weighted interference violations are minimised. The repository contains the model, instance generator, two-backend experiment runner, an independent solution checker, analysis scripts, the official CELAR validation, and the paper draft.

## Project identity

| Field | Details |
|:--|:--|
| **Course** | AI Sessional Lab Final |
| **Group** | 12 |
| **Department** | Computer Science and Engineering (CSE) |
| **Academic level** | 3rd Year, 2nd Semester, Even section |
| **Instructor** | Pollob Chandra Ray |
| **Member 1** | Mohammed Saif Al Sabah — `0812320205101026` |
| **Member 2** | Fokrul Islam — `0812320205101044` |

## What is included

| Component | Status |
|:--|:--|
| Compact MiniZinc RLFAP model with reified interference and duplex equality | ✓ `models/rlfap_core.mzn` |
| `first_fail` and `input_order` search variants (Gecode) | ✓ |
| Second backend: HiGHS (MIP) | ✓ `models/model_default.mzn` |
| Synthetic generator with tunable difficulty and recorded seeds | ✓ `src/gen_instances.py` |
| Independent checker that recomputes every constraint from the data | ✓ `src/check_solutions.py` |
| Official CELAR model, 10 public instances, validation run | ✓ `data/raw/celar/`, `results/celar_validation.csv` |
| Analysis summary, paired comparisons, backend agreement | ✓ `results/summary.txt` |
| Plots (log-scale time, objective) | ✓ `results/plots/` |
| Paper draft and validation report | ✓ `report/` |

## Research question

> How do the `first_fail` and `input_order` search heuristics, and the choice of Gecode (CP) versus HiGHS (MIP), affect solve time and solution quality for weighted RLFAP instances?

## Quick start (Linux, Ubuntu 24.04)

> After extracting the submission ZIP, enter the project root first: `cd b10_rlfap_backend_project`.

```bash
sudo apt update
sudo apt install -y minizinc python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
minizinc --version
minizinc --solvers        # Gecode should be listed; HiGHS needs BACKEND_SETUP.md
```

For the HiGHS backend, follow [`BACKEND_SETUP.md`](BACKEND_SETUP.md).

## Live demo video

The submission includes `demo/B10_RLFAP_Live_Demo.mp4`, a 29-second silent walkthrough of instance generation, CELAR validation, solver runs and plots.

## Reproduce the synthetic experiment

```bash
make generate     # writes data/dzn/*.dzn and results/instance_statistics.csv
make run          # 30 runs: 2 Gecode heuristics + HiGHS, 10 instances, 30 s limit
make analyze      # writes results/summary.txt
make plot         # writes results/plots/*.png
make check        # independently verifies every reported solution
```

Or run the steps individually with `python src/<script>.py`. Full details are in [`report/paper_draft.md`](report/paper_draft.md).

## Validate the official CELAR benchmark

```bash
make validate-celar      # runs the original celar.mzn on the 10 public instances
cat results/celar_validation.csv
```

The validator checks the data keys with a regular expression, runs the official model, and records the status and the **best** objective (the last printed solution). A row counts as validated when the solver returns a solution. That does **not** mean the instance was solved to optimality. In the included run, every CELAR instance reached the 30 s limit with `FEASIBLE`, so these objectives are upper bounds. See [`report/dataset_validation.md`](report/dataset_validation.md).

## Status meanings

- `OPTIMAL`: the solver proved optimality within the time limit.
- `FEASIBLE`: a valid solution was found, but optimality was not proven within the time limit. The objective is an upper bound.
- `UNKNOWN`: no solution was found within the time limit.
- `FAILED`: the solver returned an error.

Never describe a time-limited `FEASIBLE` result as optimal.

## Repository map

```text
models/                 MiniZinc models: rlfap_core.mzn (shared), two heuristic variants, HiGHS model
data/dzn/               Synthetic instances (generated; reproducible from seeds)
data/raw/celar/         Official CELAR model, public instances, and metadata
src/gen_instances.py    Synthetic instance generator (tunable density, frequency ratio, duplex fraction)
src/run.py              Experiment runner: Gecode (2 heuristics) and HiGHS
src/check_solutions.py  Independent checker for every reported synthetic solution
src/validate_celar.py   Official CELAR schema and solver validation
src/mzn_parse.py        Shared parser: best solution, status, versions
src/analyze_results.py  Status counts, timing, paired comparisons, backend agreement
src/plot.py             Plots
src/summarize_instances.py  Instance statistics table
results/                CSVs, raw solver logs, verification, summary, plots
report/                 Paper draft, validation report, paper outline
```

## Interpretation rules

- Synthetic results test the compact project model on generated instances. They are not field measurements of any real network.
- Official CELAR results use the original CELAR model and its own domain and category semantics. They are reported separately from the compact model.
- Every final comparison must report the solver version, MiniZinc version, machine, time limit, dataset source, and seed. These are recorded in the CSV files.
- Do not describe the Gecode heuristic comparison as a comparison of identical searches on both backends. HiGHS uses no search annotation.

## Academic integrity

Synthetic experiments and official CELAR validation are kept separate. Citations and any conversion or modelling assumption are documented in `report/paper_draft.md`. Add the official references and your group's own checks before submission.
