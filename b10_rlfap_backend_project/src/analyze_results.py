#!/usr/bin/env python3
"""Summarise results/results.csv: status counts, timing, paired comparisons,
and cross-backend agreement on proven optima. Writes results/summary.txt."""
from __future__ import annotations
import csv, statistics
from collections import Counter, defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((root / "results/results.csv").open(encoding="utf-8")))
lines: list[str] = []
def out(s: str = "") -> None:
    print(s); lines.append(s)

out(f"Total runs: {len(rows)}")
out("Status counts by configuration:")
by_cfg = defaultdict(list)
for r in rows:
    by_cfg[(r["solver"], r["model"])].append(r)
for (solver, model), rs in sorted(by_cfg.items()):
    c = Counter(r["status"] for r in rs)
    out(f"  {solver:7} {model:18} OPTIMAL={c['OPTIMAL']} FEASIBLE={c['FEASIBLE']} UNKNOWN={c['UNKNOWN']} FAILED={c['FAILED']}")

out("\nSolve time (seconds, wall clock incl. MiniZinc start-up):")
for (solver, model), rs in sorted(by_cfg.items()):
    t = [float(r["solve_time_sec"]) for r in rs]
    out(f"  {solver:7} {model:18} median={statistics.median(t):.3f}  mean={statistics.mean(t):.3f}  max={max(t):.3f}")

out("\nObjective (best solution found; time-limited runs are upper bounds):")
for (solver, model), rs in sorted(by_cfg.items()):
    obj = [int(r["objective"]) for r in rs if r["objective"] != ""]
    nz = sum(1 for v in obj if v != 0)
    out(f"  {solver:7} {model:18} min={min(obj)} max={max(obj)} mean={statistics.mean(obj):.2f} non-zero={nz}/{len(obj)}")

# Paired comparison of the two Gecode heuristics on identical instances.
# Two complete runs of this pipeline differed by up to ~0.07 s on sub-second
# instances (wall-clock noise, including MiniZinc start-up). Differences within
# TIE_TOLERANCE_SEC are therefore treated as ties, not as a winner.
TIE_TOLERANCE_SEC = 0.1
by_inst = defaultdict(dict)
for r in rows:
    by_inst[r["instance"]][r["model"]] = r
ff_faster = io_faster = tie = 0
out("\nPaired Gecode comparison (first_fail vs input_order), same instance and time limit:")
for inst in sorted(by_inst):
    a, b = by_inst[inst]["model_first_fail"], by_inst[inst]["model_input_order"]
    ta, tb = float(a["solve_time_sec"]), float(b["solve_time_sec"])
    both_timeout = a["status"] == "FEASIBLE" and b["status"] == "FEASIBLE"
    if both_timeout:
        tie += 1; verdict = "both time-limited"
    elif abs(ta - tb) <= TIE_TOLERANCE_SEC:
        tie += 1; verdict = f"tie (within {TIE_TOLERANCE_SEC} s)"
    elif ta < tb:
        ff_faster += 1; verdict = "first_fail faster"
    else:
        io_faster += 1; verdict = "input_order faster"
    out(f"  {inst:22} FF={ta:7.2f}s ({a['status']:8}) IO={tb:7.2f}s ({b['status']:8}) -> {verdict}")
out(f"  Summary: first_fail faster on {ff_faster}, input_order faster on {io_faster}, tie or both time-limited on {tie}.")

out("\nCross-backend agreement on proven optima:")
mismatch = 0
for inst in sorted(by_inst):
    opt = {m: int(r["objective"]) for m, r in by_inst[inst].items() if r["status"] == "OPTIMAL"}
    vals = set(opt.values())
    if len(vals) > 1:
        mismatch += 1
    out(f"  {inst:22} proven optima: {opt if opt else 'none'} {'-> AGREE' if len(vals) <= 1 else '-> DISAGREE'}")
out(f"  Instances with disagreeing proven optima: {mismatch}")

out("\nNote: interpret these numbers only with the documented dataset, hardware, "
    "solver versions and time limit (see results/results.csv columns and README).")
(root / "results/summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
