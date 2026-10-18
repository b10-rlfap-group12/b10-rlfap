"""Shared helpers for reading MiniZinc output.

MiniZinc prints one block per improving solution, separated by '----------',
and prints '==========' only when optimality is proven. The best solution is
therefore the LAST block, not the first.
"""
from __future__ import annotations
import re
import subprocess

OBJ_RE = re.compile(r"^objective\s*=\s*(-?\d+);", re.M)
TIMEOUT_MARKERS = ("Time limit exceeded", "% Time limit")


def all_objectives(output: str) -> list[int]:
    return [int(x) for x in OBJ_RE.findall(output)]


def best_objective(output: str) -> int | None:
    vals = all_objectives(output)
    return vals[-1] if vals else None


def status_from_output(stdout: str, stderr: str, returncode: int) -> str:
    """OPTIMAL if optimality was proven, FEASIBLE if a solution was found but
    not proven optimal, UNKNOWN if no solution was found, FAILED on error."""
    combined = stdout + "\n" + stderr
    if returncode != 0 and not all_objectives(combined):
        return "FAILED"
    if "==========" in stdout:
        return "OPTIMAL"
    if all_objectives(stdout):
        return "FEASIBLE"
    return "UNKNOWN"


def last_block_values(output: str) -> dict[str, str]:
    """Return the variables of the last SOLUTION block as raw strings.

    A solution block is one that has a line starting with 'frequency='. The
    statistics lines ('%%%mzn-stat: ...') that some solvers print after the
    solution are ignored because they start with '%'.
    """
    blocks = [b for b in output.split("----------") if re.search(r"^frequency\s*=", b, flags=re.M)]
    if not blocks:
        return {}
    values = {}
    for line in blocks[-1].splitlines():
        m = re.match(r"^(\w+)\s*=\s*(.+);\s*$", line.strip())
        if m:
            values[m.group(1)] = m.group(2).strip()
    return values


def minizinc_version() -> str:
    try:
        out = subprocess.check_output(["minizinc", "--version"], text=True, stderr=subprocess.STDOUT)
        m = re.search(r"version\s+([\d.]+)", out)
        return m.group(1) if m else out.strip().splitlines()[0]
    except Exception:
        return "unknown"


def solver_version(solver_id: str) -> str:
    try:
        out = subprocess.check_output(["minizinc", "--solvers"], text=True, stderr=subprocess.STDOUT)
        for line in out.splitlines():
            if line.strip().startswith(solver_id):
                return line.strip()
    except Exception:
        pass
    return "unknown"
