"""Plimsoll Gate 0.5 — null-baseline permutation test on a held-out source.

Parametrized port of `gate-0/null-baseline.py`. Reads a triples CSV from
`prep-*.py` plus the pairwise-results CSV from `analyze.py`, then runs
N_PERM per-pair label-swap permutations under H0 (agents A and B exchangeable
on each task) to produce a null distribution for median |Δ|.

Frozen per the OSF pre-registration (DOI 10.17605/OSF.IO/G9WFY):
  - Margin band:           [0.30, 0.70]
  - Inclusion thresholds:  ≥20 shared full, ≥8 shared margin (must match
                           analyze.py — pairs reconstructed exactly)
  - N_PERM:                1000
  - SEED:                  42 (per Gate 0 convention; per-source independence
                           is provided by the disjoint data, not the seed)
  - Decision (per source): observed median |Δ| ≥ 0.05 AND z ≥ 3

Outputs the null distribution CSV, prints z-score and tail probability,
returns final per-source verdict.

Usage:
  python null-baseline.py --input <prep-output.csv> \\
                          --pairs <pairwise-results.csv> \\
                          --out <null-results.csv> \\
                          --source-name <swebench-verified|livecodebench|mmlu-pro>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MARGIN_LO = 0.30
MARGIN_HI = 0.70
MIN_SHARED_FULL = 20
MIN_SHARED_MARGIN = 8
N_PERM = 1000
SEED = 42

DECISION_THRESHOLD_MEDIAN_ABS_DELTA = 0.05
DECISION_THRESHOLD_Z = 3.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True,
                        help="pairwise-results.csv from analyze.py (defines the qualifying pair set).")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-name", type=str, required=True,
                        choices=["swebench-verified", "livecodebench", "mmlu-pro"])
    parser.add_argument("--n-perm", type=int, default=N_PERM)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--margin-lo", type=float, default=MARGIN_LO)
    parser.add_argument("--margin-hi", type=float, default=MARGIN_HI)
    parser.add_argument("--min-shared-full", type=int, default=MIN_SHARED_FULL)
    parser.add_argument("--min-shared-margin", type=int, default=MIN_SHARED_MARGIN)
    parser.add_argument("--filter-benchmark", type=str, default=None,
                        help="Optional: filter input to benchmark_name == this value (variant B).")
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: input not found: {args.input}")
    if not args.pairs.exists():
        sys.exit(f"ERROR: pairs not found: {args.pairs}")

    rng = np.random.default_rng(args.seed)
    df = pd.read_csv(args.input)
    df["success"] = df["success"].astype(int)
    if args.filter_benchmark is not None:
        before = len(df)
        df = df[df["benchmark_name"] == args.filter_benchmark]
        print(f"  filter-benchmark={args.filter_benchmark!r}: {before:,} -> {len(df):,} rows")
        if df.empty:
            sys.exit(f"ERROR: no rows after filter-benchmark={args.filter_benchmark!r}")
    obs = pd.read_csv(args.pairs)
    obs_median = float(obs["abs_delta"].median())
    print(f"[{args.source_name}] Observed median |Δ|: {obs_median:.4f}")
    print(f"  band=[{args.margin_lo:.2f},{args.margin_hi:.2f}]  "
          f"thresholds=({args.min_shared_full},{args.min_shared_margin})")
    print(f"  pairs in observed set: {len(obs):,}")

    # Pool across benchmark_name (matches analyze.py POOLED primary).
    task_difficulty = df.groupby("task_id")["success"].mean()
    margin_tasks = set(
        task_difficulty[
            (task_difficulty >= args.margin_lo) & (task_difficulty <= args.margin_hi)
        ].index
    )
    wide = df.pivot_table(
        index="agent", columns="task_id", values="success", aggfunc="mean"
    )

    pair_data: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for _, row in obs.iterrows():
        a, b = row["a"], row["b"]
        if a not in wide.index or b not in wide.index:
            continue
        sa, sb = wide.loc[a], wide.loc[b]
        both = sa.notna() & sb.notna()
        if int(both.sum()) < args.min_shared_full:
            continue
        task_ids = sa[both].index
        margin_mask = np.fromiter(
            (t in margin_tasks for t in task_ids), dtype=bool
        )
        if int(margin_mask.sum()) < args.min_shared_margin:
            continue
        pair_data.append(
            (sa[both].to_numpy(dtype=float),
             sb[both].to_numpy(dtype=float),
             margin_mask)
        )

    n_pairs = len(pair_data)
    print(f"  pairs reconstructed: {n_pairs:,}")
    if n_pairs == 0:
        sys.exit("ERROR: no pairs reconstructed; check that --input matches what analyze.py used.")
    if n_pairs != len(obs):
        print(
            f"  WARNING: reconstructed {n_pairs} but observed CSV has {len(obs)}; "
            "check input alignment."
        )

    null_medians = np.zeros(args.n_perm)
    null_p95s = np.zeros(args.n_perm)
    print(f"\nRunning {args.n_perm:,} permutations × {n_pairs:,} pairs ...")
    for k in range(args.n_perm):
        deltas = np.empty(n_pairs)
        for i, (a, b, mask) in enumerate(pair_data):
            swap = rng.random(len(a)) < 0.5
            a_p = np.where(swap, b, a)
            b_p = np.where(swap, a, b)
            ef = (a_p - b_p).mean()
            em = (a_p[mask] - b_p[mask]).mean()
            deltas[i] = abs(em - ef)
        null_medians[k] = np.median(deltas)
        null_p95s[k] = np.quantile(deltas, 0.95)
        if (k + 1) % 100 == 0:
            print(f"  {k + 1:,}/{args.n_perm:,} done — running null mean: "
                  f"{null_medians[:k+1].mean():.4f}")

    bar = "=" * 60
    print(f"\n{bar}\n[{args.source_name}] NULL DISTRIBUTION OF MEDIAN |Δ|\n{bar}")
    print(f"  mean:    {null_medians.mean():.4f}")
    print(f"  std:     {null_medians.std():.4f}")
    print(f"  p2.5:    {np.quantile(null_medians, 0.025):.4f}")
    print(f"  p25:     {np.quantile(null_medians, 0.25):.4f}")
    print(f"  median:  {np.median(null_medians):.4f}")
    print(f"  p75:     {np.quantile(null_medians, 0.75):.4f}")
    print(f"  p97.5:   {np.quantile(null_medians, 0.975):.4f}")

    z = (obs_median - null_medians.mean()) / null_medians.std()
    p_extreme = float((null_medians >= obs_median).mean())
    print(f"\n{bar}\n[{args.source_name}] COMPARISON\n{bar}")
    print(f"  observed median |Δ|: {obs_median:.4f}")
    print(f"  null mean:           {null_medians.mean():.4f}")
    print(f"  z-score:             {z:+.2f}")
    print(f"  P(null ≥ obs):       {p_extreme:.4f}")

    print(f"\n{bar}\n[{args.source_name}] FINAL Gate 0.5 VERDICT\n{bar}")
    cleared_effect = obs_median >= DECISION_THRESHOLD_MEDIAN_ABS_DELTA
    cleared_z = z >= DECISION_THRESHOLD_Z
    if cleared_effect and cleared_z:
        verdict = (
            f"CLEARS — median |Δ| = {obs_median:.4f} ≥ "
            f"{DECISION_THRESHOLD_MEDIAN_ABS_DELTA} AND z = {z:+.2f} ≥ "
            f"{DECISION_THRESHOLD_Z}. Pre-registered Gate 0.5 verdict for "
            f"{args.source_name}: replication confirmed."
        )
    elif not cleared_effect:
        verdict = (
            f"FAILS (effect floor) — median |Δ| = {obs_median:.4f} < "
            f"{DECISION_THRESHOLD_MEDIAN_ABS_DELTA}. Capability-margin filtering "
            "does not produce paired-effect-size instability on this source at "
            "the registered effect threshold."
        )
    else:
        verdict = (
            f"FAILS (null floor) — median |Δ| = {obs_median:.4f} ≥ threshold "
            f"but z = {z:+.2f} < {DECISION_THRESHOLD_Z}. Effect is real-sized "
            "but not statistically distinguishable from chance label assignment "
            "on this source's pair structure."
        )
    print(verdict)

    pd.DataFrame({
        "perm": range(args.n_perm),
        "null_median": null_medians,
        "null_p95": null_p95s,
    }).to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
