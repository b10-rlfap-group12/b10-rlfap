#!/usr/bin/env python3
"""Generate reproducible weighted RLFAP .dzn instances.

Difficulty is controlled by three parameters:
  --density     interfering link pairs per radio link (higher = more constraints)
  --freq-ratio  available channels as a fraction of the number of links
  --duplex-frac fraction of links that are paired into duplex relations

The defaults were chosen so that instances have non-zero weighted interference
and solve times that grow with size. Every instance records its seed.
"""
from __future__ import annotations
import argparse, random
from pathlib import Path

DEFAULT_DENSITY = 3.0
DEFAULT_FREQ_RATIO = 0.3
DEFAULT_DUPLEX_FRAC = 0.1
MIN_FREQUENCIES = 8


def make_instance(n_vars: int, seed: int, density: float = DEFAULT_DENSITY,
                  freq_ratio: float = DEFAULT_FREQ_RATIO,
                  duplex_frac: float = DEFAULT_DUPLEX_FRAC) -> str:
    rng = random.Random(seed)
    max_frequency = max(MIN_FREQUENCIES, int(n_vars * freq_ratio))
    target = int(n_vars * density)
    pairs: set[tuple[int, int]] = set()
    while len(pairs) < target:
        a, b = sorted(rng.sample(range(1, n_vars + 1), 2))
        pairs.add((a, b))
    pairs_sorted = sorted(pairs)
    v1 = [a for a, _ in pairs_sorted]
    v2 = [b for _, b in pairs_sorted]
    dist = [rng.choice([1, 2, 2, 3, 3, 4]) for _ in pairs_sorted]
    weight = [rng.randint(1, 10) for _ in pairs_sorted]

    # Duplex pairs use disjoint links and a same-channel relation (gap 0).
    n_duplex = max(1, int(n_vars * duplex_frac))
    used: set[int] = set()
    duplex_a, duplex_b = [], []
    while len(duplex_a) < n_duplex:
        a, b = sorted(rng.sample(range(1, n_vars + 1), 2))
        if a in used or b in used:
            continue
        used.update((a, b))
        duplex_a.append(a)
        duplex_b.append(b)

    def arr(xs):
        return "[" + ", ".join(map(str, xs)) + "]"

    return "\n".join([
        f"seed = {seed};",
        f"n_vars = {n_vars};",
        f"n_constraints = {len(v1)};",
        f"max_frequency = {max_frequency};",
        f"v1 = {arr(v1)};",
        f"v2 = {arr(v2)};",
        f"min_distance = {arr(dist)};",
        f"weight = {arr(weight)};",
        f"n_duplex = {n_duplex};",
        f"duplex_a = {arr(duplex_a)};",
        f"duplex_b = {arr(duplex_b)};",
        f"duplex_gap = {arr([0] * n_duplex)};",
        "",
    ])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--start-vars", type=int, default=20)
    ap.add_argument("--step", type=int, default=10)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--density", type=float, default=DEFAULT_DENSITY)
    ap.add_argument("--freq-ratio", type=float, default=DEFAULT_FREQ_RATIO)
    ap.add_argument("--duplex-frac", type=float, default=DEFAULT_DUPLEX_FRAC)
    ap.add_argument("--out", type=Path, default=Path("data/dzn"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for idx in range(args.count):
        n = args.start_vars + idx * args.step
        path = args.out / f"instance_{idx+1:02d}_{n}vars.dzn"
        text = make_instance(n, args.seed + idx, args.density, args.freq_ratio, args.duplex_frac)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path} (vars={n}, seed={args.seed + idx})")


if __name__ == "__main__":
    main()
