#!/usr/bin/env python3
"""Run the official CELAR model and instances, preserving benchmark semantics."""
from __future__ import annotations
import argparse, subprocess
from pathlib import Path

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--solver', default='Gecode')
    ap.add_argument('--time-limit', type=int, default=30)
    ap.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(); root = args.project
    model = root / 'data/raw/celar/celar.mzn'
    for data in sorted((root / 'data/raw/celar').glob('*.dzn')):
        print(f'=== {data.name} / {args.solver} ===', flush=True)
        subprocess.run(['minizinc', '--solver', args.solver, '--time-limit', str(args.time_limit*1000), str(model), str(data)], check=False)

if __name__ == '__main__': main()
