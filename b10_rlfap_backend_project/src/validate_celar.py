#!/usr/bin/env python3
"""Validate the official MiniZinc CELAR/RLFAP benchmark files.

For each official .dzn instance this script:
  1. checks that the expected data keys are defined (regex, not substring),
  2. runs the ORIGINAL celar.mzn model with the chosen solver and time limit,
  3. records the status (OPTIMAL / FEASIBLE / UNKNOWN / FAILED) and the BEST
     objective (last printed solution), not the first.

'validated' means: schema ok AND the solver returned a solution. It does NOT
mean the instance was solved to optimality. See report/dataset_validation.md.
"""
from __future__ import annotations
import argparse, csv, re, subprocess, time
from pathlib import Path
from mzn_parse import best_objective, status_from_output, minizinc_version, solver_version

REQUIRED_KEYS = ["num_variables", "num_hardconstraints", "num_softconstraints", "categories"]


def schema_ok(text: str) -> tuple[bool, str]:
    missing = [k for k in REQUIRED_KEYS
               if not re.search(rf"^\s*{k}\s*=", text, flags=re.M)]
    return (not missing), ";".join(missing)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", default="Gecode")
    ap.add_argument("--time-limit", type=int, default=30)
    ap.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    root = args.project
    model = root / "data/raw/celar/celar.mzn"
    files = sorted((root / "data/raw/celar").glob("*.dzn"))
    if not model.exists() or not files:
        raise SystemExit("Official CELAR files not found in data/raw/celar")

    mzn_ver = minizinc_version()
    sol_ver = solver_version(args.solver)
    raw_dir = root / "results/raw_celar"
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for data in files:
        ok, missing = schema_ok(data.read_text(encoding="utf-8"))
        cmd = ["minizinc", "--solver", args.solver, "--time-limit", str(args.time_limit * 1000),
               str(model), str(data)]
        start = time.perf_counter()
        stdout = stderr = ""; returncode = -1
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=args.time_limit + 15)
            stdout, stderr, returncode = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr = "TIMEOUT (wrapper)"
        elapsed = time.perf_counter() - start
        status = status_from_output(stdout, stderr, returncode)
        obj = best_objective(stdout)
        (raw_dir / f"{data.stem}__{args.solver}.txt").write_text(
            stdout + "\n--- stderr ---\n" + stderr, encoding="utf-8", errors="replace")
        rows.append({
            "instance": data.name, "schema_valid": ok, "missing_keys": missing,
            "solver": args.solver, "solver_version": sol_ver, "minizinc_version": mzn_ver,
            "time_limit_sec": args.time_limit, "status": status,
            "solve_time_sec": round(elapsed, 4),
            "objective": "" if obj is None else obj,
        })
        print(f"{data.name}: {status} objective={obj}", flush=True)

    out = root / "results/celar_validation.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    with_solution = sum(r["status"] in ("OPTIMAL", "FEASIBLE") and r["objective"] != "" for r in rows)
    optimal = sum(r["status"] == "OPTIMAL" for r in rows)
    nonzero = sum(r["objective"] != "" and int(r["objective"]) != 0 for r in rows)
    schema = sum(r["schema_valid"] for r in rows)
    print(f"schema_valid={schema}/{len(rows)}; with_solution={with_solution}/{len(rows)}; "
          f"optimal={optimal}/{len(rows)}; nonzero_objective={nonzero}/{len(rows)}; saved={out}")
    if schema != len(rows) or with_solution != len(rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
