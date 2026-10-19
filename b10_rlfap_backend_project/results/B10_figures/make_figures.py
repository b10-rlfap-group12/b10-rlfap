#!/usr/bin/env python3
"""Paper figures built from results/results.csv.

Writes to results/figures/:
  fig_paired_scatter.png   first_fail time vs input_order time per instance
  fig_status_heatmap.png   status and time for every instance and configuration
  fig_agreement.png        proven optimum per instance and configuration
  fig_workflow.png         project pipeline diagram
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

root = Path(__file__).resolve().parents[1]
out = root / "results/figures"
out.mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader((root / "results/results.csv").open(encoding="utf-8")))

CONFIGS = [("model_first_fail", "Gecode first_fail"),
           ("model_input_order", "Gecode input_order"),
           ("model_default", "HiGHS")]
by = defaultdict(dict)
for r in rows:
    by[r["instance"]][r["model"]] = r
instances = sorted(by, key=lambda i: int(by[i]["model_default"]["n_vars"]))
links = [int(by[i]["model_default"]["n_vars"]) for i in instances]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

# 1. Paired scatter
# x = first_fail time, y = input_order time.
# Below the diagonal: input_order is faster. Above the diagonal: first_fail is faster.
fig, ax = plt.subplots(figsize=(4.6, 4.2))
ff = [float(by[i]["model_first_fail"]["solve_time_sec"]) for i in instances]
io = [float(by[i]["model_input_order"]["solve_time_sec"]) for i in instances]
lo, hi = 0.08, 40
ax.fill([lo, hi, hi], [lo, lo, hi], color="#eef5ee", zorder=0)   # input_order faster
ax.fill([lo, lo, hi], [lo, hi, hi], color="#fbeeee", zorder=0)   # first_fail faster
ax.plot([lo, hi], [lo, hi], color="grey", lw=1, ls="--", zorder=1)
for n, x, y in zip(links, ff, io):
    ax.scatter(x, y, s=46, color="#1f77b4", zorder=3)
    ax.annotate(f"{n}", (x, y), textcoords="offset points", xytext=(5, -9), fontsize=7)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("Gecode first_fail solve time (s)")
ax.set_ylabel("Gecode input_order solve time (s)")
ax.set_title("Heuristic comparison per instance", fontsize=10)
ax.text(0.12, 15, "first_fail faster", fontsize=7.5, color="#8a4b4b")
ax.text(6, 0.12, "input_order faster", fontsize=7.5, color="#3d6b3d")
ax.text(0.085, 0.085, "dashed: equal time", fontsize=6.5, color="#666666")
ax.grid(True, which="both", alpha=0.25)
fig.tight_layout(); fig.savefig(out / "fig_paired_scatter.png", dpi=200); plt.close(fig)

# 2. Status heatmap
status_code = {"OPTIMAL": 2, "FEASIBLE": 1, "UNKNOWN": 0, "FAILED": -1}
colors = matplotlib.colors.ListedColormap(["#d62728", "#ffbf00", "#2ca02c"])
mat = np.zeros((len(instances), len(CONFIGS)))
for a, i in enumerate(instances):
    for b, (m, _) in enumerate(CONFIGS):
        mat[a, b] = max(status_code.get(by[i][m]["status"], 0), 0)
fig, ax = plt.subplots(figsize=(4.8, 4.6))
ax.imshow(mat, cmap=colors, vmin=0, vmax=2, aspect="auto")
for a, i in enumerate(instances):
    for b, (m, _) in enumerate(CONFIGS):
        r = by[i][m]
        t = float(r["solve_time_sec"])
        tag = "limit" if r["status"] == "FEASIBLE" else ("opt" if r["status"] == "OPTIMAL" else r["status"])
        ax.text(b, a, f"{t:.2f}s\n{tag}", ha="center", va="center", fontsize=6.5)
ax.set_xticks(range(len(CONFIGS)))
ax.set_xticklabels([c[1] for c in CONFIGS], rotation=15, ha="right", fontsize=7.5)
ax.set_yticks(range(len(instances)))
ax.set_yticklabels([f"{n} links" for n in links], fontsize=7.5)
ax.set_title("Status and time per instance (30 s limit)", fontsize=10)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#2ca02c", label="OPTIMAL"), Patch(color="#ffbf00", label="FEASIBLE (limit)"),
                   Patch(color="#d62728", label="no solution")],
          loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig(out / "fig_status_heatmap.png", dpi=200); plt.close(fig)

# 3. Agreement dot plot (proven optima)
fig, ax = plt.subplots(figsize=(5.2, 3.6))
mk = {"model_first_fail": ("o", "#1f77b4"), "model_input_order": ("s", "#ff7f0e"), "model_default": ("^", "#2ca02c")}
for a, i in enumerate(instances):
    vals = []
    for m, _ in CONFIGS:
        r = by[i][m]
        if r["status"] == "OPTIMAL":
            v = int(r["objective"])
            vals.append(v)
            mkr, c = mk[m]
            dy = {"model_first_fail": -0.2, "model_input_order": 0.0, "model_default": 0.2}[m]
            ax.scatter(v, a + dy, marker=mkr, color=c, s=40, zorder=3)
ax.set_yticks(range(len(instances)))
ax.set_yticklabels([f"{n} links" for n in links], fontsize=7.5)
ax.set_xlabel("Proven optimum (objective)")
ax.set_title("Proven optima agree across configurations\n(markers offset vertically for visibility)", fontsize=9)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], marker=mk[m][0], color=mk[m][1], ls="", label=c) for m, c in CONFIGS],
          loc="lower right", fontsize=7, frameon=True)
ax.grid(True, axis="x", alpha=0.25)
fig.tight_layout(); fig.savefig(out / "fig_agreement.png", dpi=200); plt.close(fig)

# 4. Workflow diagram
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
def box(x, y, w, h, title, lines, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.12",
                                fc=fc, ec="#444444", lw=0.9))
    ax.text(x + w/2, y + h - 0.28, title, ha="center", va="top", fontsize=8.5, weight="bold")
    ax.text(x + w/2, y + h - 0.66, "\n".join(lines), ha="center", va="top", fontsize=7, linespacing=1.35)
def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#444444", lw=0.9))
box(0.2, 4.6, 2.9, 1.5, "1. Model", ["rlfap_core.mzn", "model_first_fail.mzn", "model_input_order.mzn", "model_default.mzn (HiGHS)"], "#e8f0fb")
box(3.55, 4.6, 2.9, 1.5, "2. Instances", ["gen_instances.py", "10 synthetic .dzn", "(20 to 110 links, seeded)", "CELAR: 10 official .dzn"], "#eaf6ea")
box(6.9, 4.6, 2.9, 1.5, "3. Runner", ["run.py", "backend preflight", "30 runs, 30 s limit", "status + best objective"], "#fdf1e3")
box(0.2, 2.0, 2.9, 1.5, "4. Checker", ["check_solutions.py", "recomputes every rule", "from the .dzn data", "errors are never passed"], "#f6eafb")
box(3.55, 2.0, 2.9, 1.5, "5. Analysis", ["analyze_results.py", "paired comparison", "backend agreement", "summary.txt"], "#fdf1e3")
box(6.9, 2.0, 2.9, 1.5, "6. Figures", ["plot.py", "make_figures.py", "PNG plots", "for report and slides"], "#eaf6ea")
box(3.55, 0.05, 2.9, 1.3, "7. Official CELAR", ["validate_celar.py", "schema check, 10/10", "feasible within limit"], "#e8f0fb")
arrow(3.1, 5.35, 3.55, 5.35); arrow(6.45, 5.35, 6.9, 5.35)
arrow(8.35, 4.6, 8.35, 3.5); arrow(1.65, 4.6, 1.65, 3.5)
arrow(3.1, 2.75, 3.55, 2.75); arrow(6.45, 2.75, 6.9, 2.75)
arrow(5.0, 2.0, 5.0, 1.35)
ax.set_title("Project pipeline", fontsize=10)
fig.tight_layout(); fig.savefig(out / "fig_workflow.png", dpi=200); plt.close(fig)
print("figures saved to", out)
