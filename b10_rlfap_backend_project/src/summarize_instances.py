#!/usr/bin/env python3
"""Summarize every synthetic DZN instance for the report."""
from __future__ import annotations
import csv, re
from pathlib import Path

def get(text: str, name: str) -> int:
    m = re.search(rf"(?:^|\n){name}\s*=\s*([^;]+);", text)
    return int(m.group(1).strip()) if m else 0

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    rows = []
    for p in sorted((root / "data/dzn").glob("*.dzn")):
        t = p.read_text(encoding="utf-8")
        rows.append({k: get(t, k) for k in ["seed", "n_vars", "n_constraints", "max_frequency", "n_duplex"]} | {"instance": p.stem})
    out = root / "results/instance_statistics.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["instance", "seed", "n_vars", "n_constraints", "max_frequency", "n_duplex"]); w.writeheader(); w.writerows(rows)
    print(f"saved {out} ({len(rows)} instances)")

if __name__ == "__main__": main()
