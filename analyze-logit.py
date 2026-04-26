"""Plimsoll Gate 0.5 — paired effect-size stability in LOGIT space.

Variant E from `robustness/DESIGN.md` v3 (OSF Addendum DOI 10.17605/OSF.IO/3PD2A).

Drop-in replacement for `analyze.py` that computes paired effect sizes on the
empirical-logit-with-continuity-correction scale (per Cox 1970, Analysis of
Binary Data) instead of raw pass-rate differences:

    p_a = mean(success_a)  over shared tasks
    p_b = mean(success_b)  over shared tasks
    logit_corr(p) = log((p + 0.5/n) / (1 - p + 0.5/n))    [Cox 1970]
    effect_full   = logit_corr(p_a_full)   - logit_corr(p_b_full)
    effect_margin = logit_corr(p_a_margin) - logit_corr(p_b_margin)

The continuity correction uses 0.5/n in numerator AND denominator (where n is
the number of shared trials for that pair-and-band) to avoid blowing up at
p ∈ {0, 1}. This is the standard Cox-Haldane-Anscombe form.

Output schema matches `analyze.py` (a, b, n_full, n_margin, effect_full,
effect_margin, delta, abs_delta, sign_flip), so downstream null-baseline.py
and compute-flip-rate.py work unchanged.

Tests "whether raw-pass-rate Δ vs. logit Δ produces meaningfully different m_b"
per the addendum's per-pair sign-flip diagnostic.
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

_MARGIN_LO = MARGIN_LO
_MARGIN_HI = MARGIN_HI
_MIN_SHARED_FULL = MIN_SHARED_FULL
_MIN_SHARED_MARGIN = MIN_SHARED_MARGIN


def empirical_logit(p: float, n: int) -> float:
    """Cox 1970 empirical logit with 0.5/n continuity correction."""
    c = 0.5 / max(n, 1)
    return float(np.log((p + c) / (1.0 - p + c)))


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


def analyze_logit_pooled(df: pd.DataFrame) -> pd.DataFrame:
    task_difficulty = df.groupby("task_id")["success"].mean()
    margin_tasks = set(
        task_difficulty[
            (task_difficulty >= _MARGIN_LO) & (task_difficulty <= _MARGIN_HI)
        ].index
    )
    print(
        f"\n[POOLED LOGIT] band=[{_MARGIN_LO:.2f},{_MARGIN_HI:.2f}]  "
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
        p_a_full = float(sa[both].mean())
        p_b_full = float(sb[both].mean())
        effect_full = empirical_logit(p_a_full, n_full) - empirical_logit(p_b_full, n_full)

        sam, sbm = wide_margin.loc[a], wide_margin.loc[b]
        both_m = sam.notna() & sbm.notna()
        n_margin = int(both_m.sum())
        if n_margin < _MIN_SHARED_MARGIN:
            continue
        p_a_margin = float(sam[both_m].mean())
        p_b_margin = float(sbm[both_m].mean())
        effect_margin = (
            empirical_logit(p_a_margin, n_margin)
            - empirical_logit(p_b_margin, n_margin)
        )

        rows.append(dict(
            a=a, b=b,
            n_full=n_full, n_margin=n_margin,
            p_a_full=p_a_full, p_b_full=p_b_full,
            p_a_margin=p_a_margin, p_b_margin=p_b_margin,
            effect_full=effect_full, effect_margin=effect_margin,
        ))

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["delta"] = out["effect_margin"] - out["effect_full"]
    out["abs_delta"] = out["delta"].abs()
    out["sign_flip"] = np.sign(out["effect_full"]) != np.sign(out["effect_margin"])
    return out


def report(out: pd.DataFrame, source_name: str) -> dict:
    bar = "=" * 60
    print(f"\n{bar}\n{source_name} (LOGIT) — POOLED PAIRWISE: {len(out):,}\n{bar}")
    if out.empty:
        return {"source": source_name, "n_pairs": 0}

    rho, pval = stats.spearmanr(out["effect_full"], out["effect_margin"])
    pearson_r, _ = stats.pearsonr(out["effect_full"], out["effect_margin"])
    print(f"\nSpearman ρ(effect_full, effect_margin): {rho:.3f}  (p={pval:.2e})")
    print(f"Pearson  r:                              {pearson_r:.3f}")

    ad = out["abs_delta"]
    print("\n|effect_margin − effect_full| (logit units):")
    print(f"  median: {ad.median():.4f}")
    print(f"  p75:    {ad.quantile(0.75):.4f}")
    print(f"  p95:    {ad.quantile(0.95):.4f}")
    print(f"  max:    {ad.max():.4f}")

    flips = int(out["sign_flip"].sum())
    print(f"\nSign flips: {flips:,} / {len(out):,} ({flips / len(out):.1%})")

    return {
        "source": source_name,
        "scale": "logit",
        "n_pairs": len(out),
        "spearman_rho": float(rho),
        "pearson_r": float(pearson_r),
        "median_abs_delta": float(ad.median()),
        "p75_abs_delta": float(ad.quantile(0.75)),
        "p95_abs_delta": float(ad.quantile(0.95)),
        "max_abs_delta": float(ad.max()),
        "sign_flip_rate": flips / len(out),
        "n_sign_flips": flips,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-name", type=str, required=True)
    parser.add_argument("--summary-out", type=Path, default=None)
    parser.add_argument("--margin-lo", type=float, default=MARGIN_LO)
    parser.add_argument("--margin-hi", type=float, default=MARGIN_HI)
    parser.add_argument("--min-shared-full", type=int, default=MIN_SHARED_FULL)
    parser.add_argument("--min-shared-margin", type=int, default=MIN_SHARED_MARGIN)
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: input not found: {args.input}")

    global _MARGIN_LO, _MARGIN_HI, _MIN_SHARED_FULL, _MIN_SHARED_MARGIN
    _MARGIN_LO = args.margin_lo
    _MARGIN_HI = args.margin_hi
    _MIN_SHARED_FULL = args.min_shared_full
    _MIN_SHARED_MARGIN = args.min_shared_margin

    df = load_triples(args.input)
    out = analyze_logit_pooled(df)
    out.to_csv(args.out, index=False)
    print(f"\nWrote {args.out} ({len(out):,} pairs)")

    summary = report(out, args.source_name)
    if args.summary_out is not None:
        pd.DataFrame([summary]).to_csv(args.summary_out, index=False)
        print(f"Wrote {args.summary_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
