#!/usr/bin/env python3
"""Plot solve time and solution quality against instance size.

Time uses a log scale because runtimes span about 0.1 s to the 30 s limit.
Timed-out (FEASIBLE) objectives are upper bounds, so they are drawn with
hollow markers to make that visible."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((root / "results/results.csv").open(encoding="utf-8")))
out = root / "results/plots"; out.mkdir(parents=True, exist_ok=True)


def series(value_key: str, need_solution: bool):
    groups = defaultdict(list)
    for r in rows:
        if need_solution and r["objective"] == "":
            continue
        val = float(r[value_key]) if value_key == "solve_time_sec" else float(r["objective"])
        groups[(r["model"], r["solver"])].append((int(r["n_vars"]), val, r["status"]))
    return groups


def draw(groups, ylabel, title, fname, log_y: bool):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for key, pts in sorted(groups.items()):
        pts.sort()
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        line, = ax.plot(xs, ys, marker="o", label=" / ".join(key))
        for x, y, st in pts:
            if st == "FEASIBLE":  # time-limited: hollow marker
                ax.plot([x], [y], marker="o", markerfacecolor="white", color=line.get_color())
    if log_y:
        ax.set_yscale("log")
    ax.set_xlabel("Number of radio links")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Hollow markers = time limit reached (FEASIBLE; objective is an upper bound).",
             fontsize=7, color="dimgray")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out / fname, dpi=180)
    plt.close(fig)


draw(series("solve_time_sec", need_solution=False),
     "Solve time (s, log scale)", "RLFAP solve time versus instance size",
     "solve_time_by_scale.png", log_y=True)
draw(series("objective", need_solution=True),
     "Weighted interference violations", "RLFAP solution quality versus instance size",
     "objective_by_scale.png", log_y=False)
print(f"saved plots in {out}")
