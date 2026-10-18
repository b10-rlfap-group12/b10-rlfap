#!/usr/bin/env python3
"""Run the synthetic RLFAP experiment on two MiniZinc backends.

Backend 1: Gecode (CP, complete search)
  - models/model_first_fail.mzn  (first_fail variable heuristic)
  - models/model_input_order.mzn (input_order variable heuristic)
Backend 2: HiGHS (MIP, via MiniZinc linearisation)
  - models/model_default.mzn (no search annotation; solver chooses)

The two heuristics are compared on the same backend. Backend results are
compared only on the same instance and time limit, not as identical searches.
"""
from __future__ import annotations
import argparse, csv, subprocess, time
from pathlib import Path
from mzn_parse import best_objective, status_from_output, minizinc_version, solver_version

CONFIGS = [
    ("Gecode", "model_first_fail"),
    ("Gecode", "model_input_order"),
    ("HiGHS", "model_default"),
]
DZN_VALUES = ["seed", "n_vars", "n_constraints", "max_frequency", "n_duplex"]


def read_dzn_values(path: Path) -> dict[str, str]:
    import re
    text = path.read_text(encoding="utf-8")
    out = {}
    for k in DZN_VALUES:
        m = re.search(rf"(?:^|\n){k}\s*=\s*([^;]+);", text)
        out[k] = m.group(1).strip() if m else "0"
    return out


def run_one(model: Path, data: Path, solver: str, limit: int, raw_dir: Path, mzn_ver: str) -> dict:
    cmd = ["minizinc", "--solver", solver, "--time-limit", str(limit * 1000),
           "--statistics", str(model), str(data)]
    started = time.perf_counter()
    stdout = stderr = ""
    returncode = 0
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=limit + 15)
        stdout, stderr, returncode = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = "TIMEOUT (wrapper)"
        returncode = -1
    elapsed = time.perf_counter() - started
    status = status_from_output(stdout, stderr, returncode)
    obj = best_objective(stdout)

    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{data.stem}__{model.stem}__{solver}.txt").write_text(
        stdout + "\n--- stderr ---\n" + stderr, encoding="utf-8", errors="replace")

    vals = read_dzn_values(data)
    return {
        "instance": data.stem,
        "n_vars": int(vals["n_vars"]), "n_constraints": int(vals["n_constraints"]),
        "max_frequency": int(vals["max_frequency"]), "n_duplex": int(vals["n_duplex"]),
        "seed": int(vals["seed"]), "model": model.stem, "solver": solver,
        "status": status, "solve_time_sec": round(elapsed, 4),
        "objective": "" if obj is None else obj,
        "time_limit_sec": limit, "minizinc_version": mzn_ver,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--time-limit", type=int, default=30)
    ap.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    root = args.project
    data_files = sorted((root / "data/dzn").glob("*.dzn"))
    if not data_files:
        raise SystemExit("No .dzn files. Run: python src/gen_instances.py")
    mzn_ver = minizinc_version()
    rows = []
    for solver, model_name in CONFIGS:
        model = root / "models" / f"{model_name}.mzn"
        print(f"solver config: {solver} | {solver_version(solver)}", flush=True)
        for data in data_files:
            print(f"{model.stem} / {solver} / {data.name}", flush=True)
            rows.append(run_one(model, data, solver, args.time_limit, root / "results/raw", mzn_ver))
    out = root / "results/results.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"saved {out} ({len(rows)} runs)")


if __name__ == "__main__":
    main()
