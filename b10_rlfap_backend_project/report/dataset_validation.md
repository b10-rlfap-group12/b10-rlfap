# Dataset Validation Evidence

## Source

The official MiniZinc benchmark suite contains a `celar/` directory with the CELAR RLFAP model and public `.dzn` instances. CELAR is a benchmark family derived from simplified real-network radio-link frequency assignment data. The repository copy is stored in `data/raw/celar/` with the original `celar.mzn` model.

## Reproduction

```bash
python src/validate_celar.py --solver Gecode --time-limit 30
cat results/celar_validation.csv
```

The script:

1. checks that the data keys `num_variables`, `num_hardconstraints`, `num_softconstraints` and `categories` are defined (regular-expression match on each line),
2. runs the original `celar.mzn` model with the chosen solver and time limit,
3. records the status, solve time, and the **best** objective (the last printed solution), together with the solver and MiniZinc versions.

Raw solver output for each instance is saved in `results/raw_celar/`.

## What "validated" means here

An instance counts as validated when the schema check passes **and** the solver returns at least one solution. It does **not** mean that the solution was shown to be optimal. Optimality is recorded separately as `OPTIMAL`.

## Result of the included run

Solver: Gecode 6.2.0, MiniZinc 2.8.2, time limit 30 s.

| Measure | Result |
|---|---|
| Schema valid | 10 / 10 |
| Solution returned | 10 / 10 |
| Proven optimal (`OPTIMAL`) | 0 / 10 |
| Non-zero objective | 10 / 10 |

Every instance reached the time limit with status `FEASIBLE`, so each objective below is the best value found in 30 s and is an upper bound on the optimum.

| Instance | Status | Best objective (30 s) |
|---|---|---:|
| CELAR6-SUB0 | FEASIBLE | 18,688 |
| CELAR6-SUB2 | FEASIBLE | 12,785 |
| CELAR6-SUB3 | FEASIBLE | 17,684 |
| CELAR6-SUB4 | FEASIBLE | 23,871 |
| CELAR7-SUB3 | FEASIBLE | 12,513,054 |
| CELAR7-SUB4 | FEASIBLE | 17,633,055 |
| graph05 | FEASIBLE | 114,150 |
| graph11 | FEASIBLE | 496,868 |
| scen06 | FEASIBLE | 157,266 |
| scen07 | FEASIBLE | 356,017,406 |

Values come from `results/celar_validation.csv`. Earlier development runs of the same command reported slightly different values for some instances (for example CELAR7-SUB4 and scen06), because a run stopped by a wall-clock limit returns whichever solution was found last. Time-limited objectives are therefore not exactly reproducible. When you report them, state the single run and its time limit, or repeat the runs and report the spread.

## Interpretation

The official instances give non-trivial weighted objectives, so the benchmark is not degenerate in the way that some synthetic instances are. They show that the official model runs, the solution is accepted, and the objective is measured. They do not show that Gecode solves these instances well: in 30 s none of them was solved to optimality.

## Limitations

The official model uses the benchmark's original domain and category representation and its objective semantics. The compact project model (`models/rlfap_core.mzn`) uses a simplified bounded-frequency representation. The paper must state whether a result comes from (a) the official model, (b) the compact project model on synthetic instances, or (c) a fully ported CELAR experiment. The three are not the same experiment unless a conversion is documented.

## References

- MiniZinc benchmark repository: https://github.com/MiniZinc/minizinc-benchmarks
- Cabon et al., "Radio Link Frequency Assignment," *Constraints*, 1999: https://hal.inrae.fr/hal-02695373v1
- MiniZinc output and checking documentation: https://docs.minizinc.dev/en/stable/checkers.html
