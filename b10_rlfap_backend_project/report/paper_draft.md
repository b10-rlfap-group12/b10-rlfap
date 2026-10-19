# Radio Link Frequency Assignment Using MiniZinc Constraint Programming

**Group:** 12
**Department:** Computer Science and Engineering (CSE)
**Academic level:** 3rd Year, 2nd Semester, Even section
**Instructor:** Pollob Chandra Ray
**Member 1:** Mohammed Saif Al Sabah — `0812320205101026`  
**Member 2:** Fokrul Islam — `0812320205101044`
**Course:** AI Sessional Lab Final

## Abstract

Radio link frequency assignment (RLFAP) gives integer frequency channels to radio links while limiting interference. We formulate a weighted soft-constraint model in MiniZinc, in which every interfering pair must be separated by a minimum distance and duplex pairs share a fixed offset. We compare two Gecode search annotations (`first_fail` and `input_order`) and a HiGHS MIP backend on ten deterministic synthetic instances of 20 to 110 links, with a 30 s limit. Wherever at least two configurations prove optimality, they agree on the optimum, and an independent checker verifies all 30 reported solutions. The `first_fail` heuristic is faster on one instance, while `input_order` is clearly faster on the 30- and 40-link instances; the remaining differences are within timing noise or time-limited. The two hardest instances are the two smallest: neither Gecode configuration proves optimality on the 20-link instance within 30 s, whereas HiGHS proves an optimum in its recorded run. We also validate the pipeline on ten public CELAR/RLFAP instances: all return a feasible objective within 30 s, but none is solved to optimality, so their objectives are upper bounds.

## 1. Problem formulation and assumptions

### 1.1 Why the problem matters

Radio links need spectrum channels. When two links that interfere with each other use the same or insufficiently separated frequencies, communication quality degrades. Frequency planning is therefore a resource allocation problem with competing requirements: a limited band, pairwise separation constraints, duplex relationships, and an objective that penalises harmful assignments.

### 1.2 Assumptions and simplifications

1. Each link receives one integer frequency channel.
2. The compact model uses a normalised band `1..max_frequency`. It does not represent a particular commercial band or propagation environment.
3. Interference is represented by pairwise minimum-separation constraints. Multipath fading, terrain, antenna patterns, power control, mobility and stochastic traffic are outside scope.
4. A weighted violation is a proxy for interference cost. A higher weight means the pair is more important to protect.
5. A duplex pair is represented by an exact frequency-offset equality. The synthetic generator uses a same-channel relation (offset zero) for about 10% of links.
6. Official CELAR instances keep their original category domains, hard equalities, soft inequalities and weighted objective. Official-model results are reported separately from the compact model.

### 1.3 Why this is a Complex Engineering Problem

- **WP1 (depth of knowledge):** The solution combines frequency-planning context, integer domains, reified constraints, weighted optimisation, MiniZinc modelling and solver behaviour. See `models/rlfap_core.mzn` and `data/raw/celar/celar.mzn`.
- **WP3 (depth of analysis):** The problem has conflicting separation requirements, duplex equalities, limited frequency domains and weighted priorities. No obvious optimal assignment is available, so the modelling and search choices must be compared experimentally.
- **WP4 (infrequently encountered issues):** The instances go beyond textbook examples: a dense interference graph, a bounded band whose size is comparable to the separation requirement, and the official CELAR benchmark with its own domain structure.
- **WP5 (beyond standards):** Spectrum regulation and the official benchmark's conventions constrain the design. The project records seeds, versions and raw solver output, distinguishes proven optima from time-limited solutions, and separates synthetic data from real measurements.

## 2. Mathematical model

Let `F = {1,...,M}` be the available frequency band, and let `f_i ∈ F` be the channel of link `i`. For each interference pair `c` with endpoints `(u_c, v_c)`, required separation `d_c` and weight `w_c`, define the violation indicator

  `z_c = 1` if `|f_u_c − f_v_c| < d_c`, and `z_c = 0` otherwise.

For each duplex relation `k` with links `(a_k, b_k)` and offset `g_k`, the hard equality is

  `f_a_k − f_b_k = g_k`.

The complete model is:

  `f_i ∈ F` for every link `i`,
  `z_c = I(|f_u_c − f_v_c| < d_c)` for every interference pair `c`,
  `f_a_k − f_b_k = g_k` for every duplex relation `k`,
  minimise `Σ_c w_c z_c`.

The duplex equality is a hard constraint. The interference terms are soft: they are counted rather than forbidden, so every instance has a feasible assignment (for example, all links on one channel, which then pays the full weight of its interference pairs).

## 3. MiniZinc implementation

`models/rlfap_core.mzn` contains the shared variables, the reified interference indicators, the duplex equalities and the weighted objective. Two search variants include it:

- `model_first_fail.mzn`: `int_search(frequency, first_fail, indomain_min, complete)`, which picks the variable with the smallest remaining domain.
- `model_input_order.mzn`: `int_search(frequency, input_order, indomain_min, complete)`, which follows declaration order.

`model_default.mzn` includes the same core with no search annotation. It is used for the HiGHS backend, which does not use CP search annotations.

Pairwise separation is written explicitly rather than with a global constraint. Each pair has its own distance and weight, so a global `all_different` would be incorrect, and the explicit form keeps every pair auditable.

## 4. Instances and data

`src/gen_instances.py` produces ten deterministic synthetic instances with 20, 30, ..., 110 links. Each instance is generated from its own seed (2026 onward) and has:

- `n_links × 3` interference pairs (density 3.0),
- a band of `max(8, 0.3 × n)` channels,
- separation distances drawn from {1, 2, 3, 4} with more weight on 2 and 3,
- integer weights in 1..10,
- `max(1, 0.1 × n)` disjoint duplex pairs with offset zero.

`results/instance_statistics.csv` records the size, pair count, band and duplex count of every instance.

The repository also contains the public CELAR/RLFAP MiniZinc model and ten `.dzn` instances in `data/raw/celar/`. `src/validate_celar.py` runs the original model on them. The official benchmark is not converted into the compact schema.

## 5. Experimental protocol

```bash
python src/gen_instances.py --count 10 --start-vars 20 --step 10 --seed 2026
python src/run.py --time-limit 30          # 30 runs
python src/check_solutions.py              # independent verification of every solution
python src/analyze_results.py              # results/summary.txt
python src/plot.py                         # results/plots/
python src/validate_celar.py --solver Gecode --time-limit 30
```

Configurations:

| Backend | Type | Model | Search |
|---|---|---|---|
| Gecode 6.3.0 | CP | `model_first_fail` | `first_fail` |
| Gecode 6.3.0 | CP | `model_input_order` | `input_order` |
| HiGHS 1.15.1 | MIP | `model_default` | solver default |

Every run uses a 30 s limit, MiniZinc 2.9.3, and the same generated `.dzn` file. Wall-clock time includes MiniZinc start-up and FlatZinc conversion. The machine is a single-core Linux VM; the runs were executed one at a time.

Each row of `results/results.csv` records instance, sizes, seed, model, solver, status, solve time, objective, time limit and MiniZinc version. Status is `OPTIMAL` when the solver proves optimality, `FEASIBLE` when a solution is returned without a proof, and `UNKNOWN` when no solution is returned.

## 6. Results

### 6.1 Verification

`src/check_solutions.py` recomputes each reported solution from the `.dzn` data: frequencies lie in the band, every `violated[c]` equals `|f_u − f_v| < d`, duplex equalities hold, and the objective equals the weighted sum. All 30 runs pass. As a negative test, we changed one reported objective in a copy of the results; the checker rejected that run.

### 6.2 Status and timing

| Configuration | OPTIMAL | FEASIBLE (30 s limit) | Median time (s) | Mean time (s) | Max time (s) |
|---|---:|---:|---:|---:|---:|
| Gecode, `first_fail` | 8 | 2 | 0.570 | 7.134 | 30.073 |
| Gecode, `input_order` | 9 | 1 | 0.513 | 3.635 | 30.067 |
| HiGHS, default | 10 | 0 | 1.737 | 3.476 | 14.811 |

The means for Gecode are dominated by the time-limited runs. Once Gecode finishes, it is usually faster than HiGHS, but HiGHS solves all ten instances, and Gecode does not finish the 20- and 30-link instances in the time limit.

### 6.3 Heuristic comparison (`first_fail` versus `input_order`)

Same instance, same backend, same time limit (values from the final clean run; `results/summary.txt`):

| Instance | `first_fail` | `input_order` | Verdict |
|---|---|---|---|
| 20 links | 30.06 s, FEASIBLE | 30.07 s, FEASIBLE | both time-limited |
| 30 links | 30.07 s, FEASIBLE | 2.19 s, OPTIMAL | `input_order` faster |
| 40 links | 7.81 s, OPTIMAL | 0.38 s, OPTIMAL | `input_order` faster |
| 50 links | 0.33 s | 0.38 s | tie (within 0.1 s) |
| 60 links | 0.38 s | 0.37 s | tie |
| 70 links | 0.42 s | 0.46 s | tie |
| 80 links | 0.46 s | 0.49 s | tie |
| 90 links | 0.51 s | 0.53 s | tie |
| 100 links | 0.63 s | 0.68 s | tie |
| 110 links | 0.67 s | 0.80 s | tie |

A tie means the difference is at most 0.1 s. We chose this tolerance after observing that two complete runs of the same pipeline differed by up to about 0.07 s on sub-second instances, so smaller differences are not interpreted. Under this rule `first_fail` is faster on one instance, `input_order` is faster on two, and seven are ties or time-limited. The two `input_order` wins are the 30- and 40-link instances, where the difference is large (seconds versus a fraction of a second) and was the same in two independent runs. An earlier run with a stricter 5% rule had labelled several sub-second differences as wins for `input_order`; those differences fall within the noise and are not reported as wins.

The data do not support a universal improvement of `first_fail` over `input_order` on these instances. This is evidence for ten instances with one seed each, not a general result.

### 6.4 Backend comparison and agreement

Where at least two configurations prove optimality, their objectives agree on all ten instances, so there is no evidence of an encoding error across the Gecode and HiGHS formulations. The clearest difference is on the 20-link instance: HiGHS proves the optimum of 6 in about 5 s, while both Gecode configurations stop at the 30 s limit with a best objective of 26. The same instance is the hardest for both Gecode configurations. Above 50 links, all configurations finish in under 2 s in the recorded run.

### 6.5 Objective values

Of the ten instances, six have a non-zero optimum. Four have an optimum of zero, which is a valid assignment with no interference violations. The objective plot (`results/plots/objective_by_scale.png`) shows the best value found, and it is an upper bound wherever the run was time-limited.

### 6.6 Scalability

Solve time does not increase monotonically with size. The hardest instances are the smallest (20 and 30 links), and runtime falls and then rises slowly from 40 to 110 links (Figure `results/plots/solve_time_by_scale.png`). A plausible explanation is that the band grows with size as `0.3 n`, so the separation requirement, which is a fixed 1 to 4 channels, is a larger fraction of the band for small instances. We did not test this explanation directly.

### 6.7 Official CELAR validation

All ten public CELAR instances run to completion under the original model. Each returns a feasible objective within the 30 s limit, and none is proven optimal. The best objectives found are listed in `report/dataset_validation.md`. Because runs stopped by the time limit return whichever solution was found last, these values are not exactly reproducible across runs.

## 7. Discussion

What worked: the model reproduces the optimum across two backends on all ten synthetic instances, the independent checker confirms every reported solution, and the logs record enough information to repeat each run.

What did not: the proposed model improvement (`first_fail`) does not help on these instances. On the 30- and 40-link instances it is clearly slower in both runs. Gecode does not prove optimality within 30 s on the 20-link instance, where HiGHS does.

Scale limits: the official CELAR instances are beyond what either configuration can prove in 30 s, so the official results are an upper-bound validation, not a solution-quality comparison.

Threats to validity: the synthetic instances are generated, not measured; each instance has one seed; the time limit is short and the machine is a single core; time-limited objectives vary between runs; the HiGHS backend is a MIP linearisation of the same model and may not behave like a CP solver on other problems.

## 8. Limitations and honest interpretation

The synthetic model is a controlled engineering test, not a field measurement. Its normalised band and pairwise interference abstraction omit propagation details. The official CELAR model is semantically richer but uses its own domain representation, so its results must not be presented as an identical run of the compact model. Runtime depends on hardware, MiniZinc and solver versions, seed, encoding and time limit. A timeout is an experimental result and is reported, not hidden.

## 9. Conclusion

The project gives a reproducible MiniZinc formulation of weighted RLFAP, a two-backend experiment with an independent solution checker, and validation on ten official CELAR instances. On the synthetic instances the two backends agree on every proven optimum. `first_fail` is faster on one larger instance, while `input_order` is clearly faster on the 30- and 40-link instances; most remaining differences are small or time-limited. The official instances are feasible within 30 s but not solved to optimality. Longer runs, more seeds, and an official-model experiment with more time would be the next steps.

## References

1. MiniZinc documentation and standard library documentation: https://docs.minizinc.dev
2. MiniZinc benchmark suite, including the CELAR directory: https://github.com/MiniZinc/minizinc-benchmarks
3. B. Cabon et al., "Radio Link Frequency Assignment," *Constraints*, 1999: https://hal.inrae.fr/hal-02695373v1
4. MiniZinc output and checking documentation: https://docs.minizinc.dev/en/stable/checkers.html
