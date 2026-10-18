# Solver backends

The experiment uses two MiniZinc backends:

| Backend | Type | Models | Notes |
|---|---|---|---|
| Gecode 6.2.0 | CP (complete search) | `model_first_fail.mzn`, `model_input_order.mzn` | Ships with the Ubuntu `minizinc` package. |
| HiGHS 1.15.1 | MIP (via MiniZinc linearisation) | `model_default.mzn` | Needs the HiGHS shared library (see below). |

Check what MiniZinc sees:

```bash
minizinc --solvers
```

## Gecode

Included with `sudo apt install minizinc` on Ubuntu 24.04. Nothing else is needed.

## HiGHS

On the development machine the Ubuntu MiniZinc package lists HiGHS but cannot load it
(`plugin loading error: Failed to load plugin ... libhighs.so`). The workaround used:

```bash
python -m pip install highspy
# locate the bundled shared library, then link it where MiniZinc looks
python -c "import highspy, os; print(os.path.dirname(highspy.__file__))"
sudo ln -sf <that_dir>/libhighs.so.1.15.1 /usr/lib/libhighs.so
```

Verify:

```bash
minizinc --solver HiGHS models/model_default.mzn data/dzn/instance_01_20vars.dzn
```

A successful run ends with `==========`. If HiGHS still reports a plugin error, do not count
its results as completed; either fix the library path or report the backend as unavailable.

## Rules for the report

- Record `minizinc --solvers` output and versions in the paper.
- Do not describe a listed-but-unloadable solver as a completed experiment.
- `model_default.mzn` has no search annotation, so the Gecode heuristic comparison and the
  HiGHS comparison are backend comparisons, not identical search strategies.
