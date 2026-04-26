"""Plimsoll Gate 0.5 — per-pair sign-flip rate (variant vs registered baseline).

Per OSF Addendum DOI 10.17605/OSF.IO/3PD2A and `robustness/DESIGN.md` v3,
sign-flip rate is the load-bearing diagnostic for the post-hoc sensitivity pass:

    flip_rate(variant) = #{pairs where sign(Δ_baseline) ≠ sign(Δ_variant)}
                         / N_qualifying_pairs

where Δ refers to `effect_margin` (the in-band paired effect size that the
median |Δ paired effect size| statistic is computed over).

Pre-committed thresholds:
  flip_rate < 5%      → stable
  5% ≤ flip_rate < 15% → mildly unstable (Limitations)
  flip_rate ≥ 15%     → destabilizing (headline)

Inner-joins baseline and variant pair tables on (a, b). Pairs that survived
inclusion under one set of (band, thresholds) but not the other are excluded
from the flip-rate denominator with a count reported separately for audit.

Usage:
  python compute-flip-rate.py \\
    --baseline component-c-runs/livecodebench/livecodebench-pairs.csv \\
    --variant  robustness/livecodebench/band-0.25-0.75/pairs.csv \\
    --out      robustness/livecodebench/band-0.25-0.75/flip-rate.csv \\
    --source   livecodebench --variant-name "band-[0.25,0.75]"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def load_pairs(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    needed = {"a", "b", "effect_full", "effect_margin"}
    missing = needed - set(df.columns)
    if missing:
        sys.exit(f"ERROR: {path} missing columns {missing}")
    return df[["a", "b", "effect_full", "effect_margin"]].copy()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, required=True,
                   help="Pairs CSV from the OSF-registered baseline run.")
    p.add_argument("--variant", type=Path, required=True,
                   help="Pairs CSV from the variant run.")
    p.add_argument("--out", type=Path, required=True,
                   help="Output CSV with one summary row + per-pair join detail in a sibling file.")
    p.add_argument("--source", type=str, required=True,
                   help="Source name (swebench-verified|livecodebench|mmlu-pro).")
    p.add_argument("--variant-name", type=str, required=True,
                   help="Human-readable variant label (e.g. 'band-[0.25,0.75]', 'logit', 'thresh-(30,15)').")
    p.add_argument("--n-pairs-floor", type=int, default=50,
                   help="Below this, the cell is descriptive-only (default: 50).")
    args = p.parse_args()

    base = load_pairs(args.baseline).rename(
        columns={"effect_full": "ef_base", "effect_margin": "em_base"}
    )
    var = load_pairs(args.variant).rename(
        columns={"effect_full": "ef_var", "effect_margin": "em_var"}
    )

    n_base = len(base)
    n_var = len(var)

    joined = pd.merge(base, var, on=["a", "b"], how="inner")
    n_qualifying = len(joined)

    n_baseline_only = n_base - n_qualifying
    n_variant_only = n_var - n_qualifying

    if n_qualifying == 0:
        sys.exit(f"ERROR: no shared pairs between baseline ({n_base}) and variant ({n_var})")

    sign_base = np.sign(joined["em_base"])
    sign_var = np.sign(joined["em_var"])
    flip_mask = (sign_base != sign_var) & ((sign_base != 0) | (sign_var != 0))
    n_flips = int(flip_mask.sum())
    flip_rate = n_flips / n_qualifying

    if flip_rate < 0.05:
        category = "stable"
    elif flip_rate < 0.15:
        category = "mildly-unstable"
    else:
        category = "destabilizing"

    descriptive_only = n_qualifying < args.n_pairs_floor

    summary = pd.DataFrame([dict(
        source=args.source,
        variant=args.variant_name,
        n_baseline_pairs=n_base,
        n_variant_pairs=n_var,
        n_qualifying=n_qualifying,
        n_baseline_only=n_baseline_only,
        n_variant_only=n_variant_only,
        n_sign_flips=n_flips,
        flip_rate=flip_rate,
        category=category,
        descriptive_only=descriptive_only,
        n_pairs_floor=args.n_pairs_floor,
    )])
    summary.to_csv(args.out, index=False)

    detail_path = args.out.with_suffix(".pairs.csv")
    joined["sign_flip"] = flip_mask
    joined.to_csv(detail_path, index=False)

    bar = "=" * 60
    print(bar)
    print(f"FLIP-RATE: {args.source} / {args.variant_name}")
    print(bar)
    print(f"  baseline pairs:  {n_base:,}")
    print(f"  variant pairs:   {n_var:,}")
    print(f"  qualifying (∩):  {n_qualifying:,}  (baseline-only: {n_baseline_only:,}, variant-only: {n_variant_only:,})")
    print(f"  sign flips:      {n_flips:,}")
    print(f"  flip_rate:       {flip_rate:.4f}  ({flip_rate:.1%})")
    print(f"  category:        {category}")
    if descriptive_only:
        print(f"  *** descriptive-only: n_qualifying < n_pairs_floor={args.n_pairs_floor}")
    print(f"\nWrote {args.out}")
    print(f"Wrote {detail_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
