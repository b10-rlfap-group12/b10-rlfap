# B10 Paper Outline — Radio Link Frequency Assignment

## Abstract
State the problem, MiniZinc approach, compared solvers/heuristics, and the main numeric finding after experiments are rerun.

## 1. Introduction
- Frequency reuse and interference in cellular/radio networks.
- Why constraint programming is suitable.
- Research question and contributions.

## 2. Related Work
- RLFAP/CELAR benchmark.
- Constraint propagation and variable-ordering heuristics.
- Cite the official benchmark and MiniZinc documentation.

## 3. Problem Formulation
- Link variables and bounded frequency domain.
- Pairwise separation constraint.
- Weighted violation objective.
- Explain all assumptions and the difference between hard and soft constraints.

## 4. Implementation
- MiniZinc version and solver versions.
- `first_fail` and `input_order` search variants.
- Instance generator and reproducibility seed.

## 5. Experimental Design
- At least 10 increasing-size instances.
- Time limit, hardware, solver settings.
- Metrics: status, objective, solve time, scale, and timeout rate.

## 6. Results and Discussion
Insert the plots from `results/plots/`. Explain trends rather than only listing numbers. Discuss why a heuristic or solver wins, and where it stops scaling.

## 7. Threats to Validity
Synthetic instances are not a substitute for field measurements. Solver results depend on hardware, version, timeout, and model encoding.

## 8. Conclusion and Future Work
Summarize the answer to the research question and propose weighted real-world data, geographic reuse constraints, or multi-objective optimization.
