"""Plimsoll Gate 0.5 — paired effect-size stability on a held-out source.

Parametrized port of `gate-0/analyze.py`. Reads the (agent, task, success)
triple format produced by `prep-{swebench,livecodebench,mmlu-pro}.py` and
runs the Gate 0 pipeline on it.

Frozen per the OSF pre-registration (DOI 10.17605/OSF.IO/G9WFY):
  - Margin band:           [0.30, 0.70] difficulty (mean per-task pass rate)
  - Inclusion thresholds:  ≥20 shared full tasks, ≥8 shared margin-band tasks
  - Headline statistic:    median |Δ paired effect size|
  - Decision (per source): median |Δ| ≥ 0.05 AND null-baseline z ≥ 3
                           (z computed by null-baseline.py)

Primary analysis pools across `benchmark_name` (per-discipline / per-platform
texture is reported supplementarily but not gated). For sources with a single
benchmark (SWE-bench Verified) this is a no-op; for sources with multiple
benchmarks (LiveCodeBench platforms, MMLU-Pro disciplines) the pooling is the
pre-registered primary.

Usage:
  python analyze.py --input <prep-output.csv> --out <pairwise-results.csv> \\
                    --source-name <swebench-verified|livecodebench|mmlu-pro>
"""
from __future__ import annotations

import argparse
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

MARGIN_LO = 0.30
MARGIN_HI = 0.70
MIN_SHARED_FULL = 20
MIN_SHARED_MARGIN = 8

DECISION_THRESHOLD_MEDIAN_ABS_DELTA = 0.05  # null-baseline z ≥ 3 also required


# Module-level overrides set by main(). Defaults are the OSF-locked baseline.
_MARGIN_LO = MARGIN_LO
_MARGIN_HI = MARGIN_HI
_MIN_SHARED_FULL = MIN_SHARED_FULL
_MIN_SHARED_MARGIN = MIN_SHARED_MARGIN


def load_triples(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected = {"benchmark_name", "agent", "task_id", "success"}
    missing = expected - set(df.columns)
    if missing:
        sys.exit(f"ERROR: input CSV missing columns: {missing}")
    df["success"] = df["success"].astype(int)
    print(f"Loaded {len(df):,} rows.")
    print(
        f"  benchmarks: {df['benchmark_name'].nunique():,}  "
        f"agents: {df['agent'].nunique():,}  "
        f"tasks: {df['task_id'].nunique():,}"
    )
    return df


def analyze_pooled(df: pd.DataFrame) -> pd.DataFrame:
    """Primary analysis: pool across benchmark_name; pairs are (agent_a, agent_b)."""
    task_difficulty = df.groupby("task_id")["success"].mean()
    margin_tasks = set(
        task_difficulty[
            (task_difficulty >= _MARGIN_LO) & (task_difficulty <= _MARGIN_HI)
        ].index
    )
    print(
        f"\n[POOLED] band=[{_MARGIN_LO:.2f},{_MARGIN_HI:.2f}]  "
        f"thresholds=({_MIN_SHARED_FULL},{_MIN_SHARED_MARGIN})  "
        f"tasks={len(task_difficulty):,}  "
        f"in-band={len(margin_tasks):,} ({len(margin_tasks) / max(len(task_difficulty), 1):.1%})"
    )

    wide = df.pivot_table(
        index="agent", columns="task_id", values="success", aggfunc="mean"
    )
    margin_cols = [t for t in wide.columns if t in margin_tasks]
    wide_margin = wide[margin_cols]

    rows: list[dict] = []
    agents = wide.index.tolist()
    n_pairs_total = len(agents) * (len(agents) - 1) // 2
    print(f"  candidate pairs: {n_pairs_total:,}")

    for a, b in combinations(agents, 2):
        sa, sb = wide.loc[a], wide.loc[b]
        both = sa.notna() & sb.notna()
        n_full = int(both.sum())
        if n_full < _MIN_SHARED_FULL:
            continue
        effect_full = float((sa[both] - sb[both]).mean())

        sam, sbm = wide_margin.loc[a], wide_margin.loc[b]
        both_m = sam.notna() & sbm.notna()
        n_margin = int(both_m.sum())
        if n_margin < _MIN_SHARED_MARGIN:
            continue
        effect_margin = float((sam[both_m] - sbm[both_m]).mean())

        rows.append(
            dict(
                a=a, b=b,
                n_full=n_full, n_margin=n_margin,
                effect_full=effect_full, effect_margin=effect_margin,
            )
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["delta"] = out["effect_margin"] - out["effect_full"]
    out["abs_delta"] = out["delta"].abs()
    out["sign_flip"] = np.sign(out["effect_full"]) != np.sign(out["effect_margin"])
    return out


def analyze_per_benchmark(df: pd.DataFrame) -> pd.DataFrame:
    """Supplementary: per-benchmark_name breakdown for texture reporting."""
    rows: list[dict] = []
    for benchmark in sorted(df["benchmark_name"].unique()):
        bdf = df[df["benchmark_name"] == benchmark]
        sub = analyze_pooled(bdf)
        if sub.empty:
            continue
        sub["benchmark"] = benchmark
        rows.append(sub)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def report(out: pd.DataFrame, source_name: str) -> dict:
    bar = "=" * 60
    print(f"\n{bar}\n{source_name} — POOLED PAIRWISE COMPARISONS: {len(out):,}\n{bar}")
    if out.empty:
        print("ERROR: no pairs survived inclusion thresholds.")
        return {"source": source_name, "n_pairs": 0}

    rho, pval = stats.spearmanr(out["effect_full"], out["effect_margin"])
    pearson_r, _ = stats.pearsonr(out["effect_full"], out["effect_margin"])
    print(f"\nSpearman ρ(effect_full, effect_margin): {rho:.3f}  (p={pval:.2e})")
    print(f"Pearson  r:                              {pearson_r:.3f}")

    ad = out["abs_delta"]
    print("\n|effect_margin − effect_full|:")
    print(f"  median: {ad.median():.4f}")
    print(f"  p75:    {ad.quantile(0.75):.4f}")
    print(f"  p95:    {ad.quantile(0.95):.4f}")
    print(f"  max:    {ad.max():.4f}")

    flips = int(out["sign_flip"].sum())
    print(
        f"\nSign flips (rank disagrees with margin): {flips:,} / {len(out):,} "
        f"({flips / len(out):.1%})"
    )

    print(f"\n{bar}\nGate 0.5 PRELIMINARY VERDICT (pending null-baseline)\n{bar}")
    median_d = float(ad.median())
    if median_d >= DECISION_THRESHOLD_MEDIAN_ABS_DELTA:
        prelim = (
            f"PROVISIONAL CLEAR — median |Δ| = {median_d:.4f} ≥ "
            f"{DECISION_THRESHOLD_MEDIAN_ABS_DELTA}; run null-baseline.py "
            "to confirm z ≥ 3 (final verdict)."
        )
    else:
        prelim = (
            f"PROVISIONAL FAIL — median |Δ| = {median_d:.4f} < "
            f"{DECISION_THRESHOLD_MEDIAN_ABS_DELTA}; null-baseline cannot rescue. "
            "This source does not clear Gate 0.5."
        )
    print(prelim)

    return {
        "source": source_name,
        "n_pairs": len(out),
        "spearman_rho": float(rho),
        "pearson_r": float(pearson_r),
        "median_abs_delta": median_d,
        "p75_abs_delta": float(ad.quantile(0.75)),
        "p95_abs_delta": float(ad.quantile(0.95)),
        "max_abs_delta": float(ad.max()),
        "sign_flip_rate": flips / len(out),
        "n_sign_flips": flips,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True,
                        help="Triples CSV from prep-*.py (columns: benchmark_name, agent, task_id, success).")
    parser.add_argument("--out", type=Path, required=True,
                        help="Output CSV with one row per qualifying agent pair.")
    parser.add_argument("--source-name", type=str, required=True,
                        choices=["swebench-verified", "livecodebench", "mmlu-pro"])
    parser.add_argument("--per-benchmark-out", type=Path, default=None,
                        help="Optional: also write per-benchmark_name pair stats to this path.")
    parser.add_argument("--summary-out", type=Path, default=None,
                        help="Optional: write headline stats summary as one-row CSV.")
    parser.add_argument("--margin-lo", type=float, default=MARGIN_LO,
                        help=f"Lower bound of capability-margin band (default: {MARGIN_LO}).")
    parser.add_argument("--margin-hi", type=float, default=MARGIN_HI,
                        help=f"Upper bound of capability-margin band (default: {MARGIN_HI}).")
    parser.add_argument("--min-shared-full", type=int, default=MIN_SHARED_FULL,
                        help=f"Inclusion threshold: minimum shared full tasks (default: {MIN_SHARED_FULL}).")
    parser.add_argument("--min-shared-margin", type=int, default=MIN_SHARED_MARGIN,
                        help=f"Inclusion threshold: minimum shared margin-band tasks (default: {MIN_SHARED_MARGIN}).")
    parser.add_argument("--filter-benchmark", type=str, default=None,
                        help="Optional: filter input to rows where benchmark_name == this value.")
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: input not found: {args.input}")

    global _MARGIN_LO, _MARGIN_HI, _MIN_SHARED_FULL, _MIN_SHARED_MARGIN
    _MARGIN_LO = args.margin_lo
    _MARGIN_HI = args.margin_hi
    _MIN_SHARED_FULL = args.min_shared_full
    _MIN_SHARED_MARGIN = args.min_shared_margin

    df = load_triples(args.input)
    if args.filter_benchmark is not None:
        before = len(df)
        df = df[df["benchmark_name"] == args.filter_benchmark]
        print(f"  filter-benchmark={args.filter_benchmark!r}: {before:,} -> {len(df):,} rows")
        if df.empty:
            sys.exit(f"ERROR: no rows after filter-benchmark={args.filter_benchmark!r}")
    out = analyze_pooled(df)
    out.to_csv(args.out, index=False)
    print(f"\nWrote {args.out} ({len(out):,} pairs)")

    summary = report(out, args.source_name)

    if args.per_benchmark_out is not None:
        per_bench = analyze_per_benchmark(df)
        per_bench.to_csv(args.per_benchmark_out, index=False)
        print(f"Wrote {args.per_benchmark_out} (per-benchmark texture)")

    if args.summary_out is not None:
        pd.DataFrame([summary]).to_csv(args.summary_out, index=False)
        print(f"Wrote {args.summary_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
