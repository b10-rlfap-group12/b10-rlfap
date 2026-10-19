#!/usr/bin/env python3
"""Independently verify every synthetic solution reported by the solver.

For each successful run in results/results.csv, this script reads the best
solution from results/raw/, recomputes every rule from the .dzn data in Python,
and checks:
  - each frequency is an integer in 1..max_frequency,
  - violated[c] == 1 exactly when |f[v1]-f[v2]| < min_distance[c],
  - every duplex pair satisfies f[a] - f[b] == gap,
  - objective == sum(weight[c] * violated[c]).

Results go to results/verification.csv. The script exits non-zero on any failure.
"""
from __future__ import annotations
import csv, re, sys
from pathlib import Path
from mzn_parse import last_block_values

root = Path(__file__).resolve().parents[1]


def dzn_arrays(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    out = {}
    for name, body in re.findall(r"(\w+)\s*=\s*(\[[^\]]*\]|-?\d+)\s*;", text):
        if body.startswith("["):
            inner = body[1:-1].strip()
            out[name] = [int(x) for x in inner.split(",") if x.strip()] if inner else []
        else:
            out[name] = int(body)
    return out


def parse_list(s: str) -> list[int]:
    s = s.strip().strip("[]").strip()
    return [int(x) for x in s.split(",") if x.strip()] if s else []


def check(row: dict) -> tuple[bool, str]:
    data = dzn_arrays(root / "data/dzn" / f"{row['instance']}.dzn")
    raw = root / "results/raw" / f"{row['instance']}__{row['model']}__{row['solver']}.txt"
    vals = last_block_values(raw.read_text(encoding="utf-8", errors="replace"))
    if "frequency" not in vals:
        return False, "no solution in raw output"
    f = parse_list(vals["frequency"])
    viol = parse_list(vals["violated"])
    obj = int(vals["objective"])
    n, mf = data["n_vars"], data["max_frequency"]
    problems = []
    if len(f) != n: problems.append(f"frequency length {len(f)}!={n}")
    if any(not (1 <= x <= mf) for x in f): problems.append("frequency out of domain")
    v1, v2, d, w = data["v1"], data["v2"], data["min_distance"], data["weight"]
    if len(viol) != len(v1): problems.append("violated length mismatch")
    else:
        for c in range(len(v1)):
            expected = int(abs(f[v1[c] - 1] - f[v2[c] - 1]) < d[c])
            if viol[c] != expected:
                problems.append(f"violated[{c+1}]={viol[c]} expected {expected}")
                break
    for a, b, g in zip(data.get("duplex_a", []), data.get("duplex_b", []), data.get("duplex_gap", [])):
        if f[a - 1] - f[b - 1] != g:
            problems.append(f"duplex {a}-{b} violated"); break
    expected_obj = sum(wc * vc for wc, vc in zip(w, viol)) if len(viol) == len(w) else None
    if expected_obj != obj:
        problems.append(f"objective {obj} != recomputed {expected_obj}")
    return (not problems), ("OK" if not problems else "; ".join(problems))


def main() -> None:
    rows = list(csv.DictReader((root / "results/results.csv").open(encoding="utf-8")))
    out_rows, failures = [], 0
    for r in rows:
        if r["status"] not in ("OPTIMAL", "FEASIBLE"):
            out_rows.append({**{k: r[k] for k in ("instance", "model", "solver", "status")},
                             "verified": "skipped", "detail": "no solution"})
            continue
        ok, detail = check(r)
        failures += (not ok)
        out_rows.append({**{k: r[k] for k in ("instance", "model", "solver", "status")},
                         "verified": ok, "detail": detail})
    out = root / "results/verification.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)
    verified = sum(r["verified"] is True for r in out_rows)
    checked = sum(r["verified"] in (True, False) for r in out_rows)
    print(f"verified={verified}/{checked} checked runs; failures={failures}; saved={out}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
