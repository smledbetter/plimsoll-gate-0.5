"""Plimsoll Gate 0.5 — exploratory pair-stratification by ability gap.

Question: does m_b vary across ability-gap quartiles? The K&B literature-review
agent flagged that "aggregating across pairs treats model-pairs as exchangeable,
which they are not — frontier-vs-frontier differs from frontier-vs-weak." Pooled
m_b masks this if it is real.

Status: exploratory texture for the methodology paper's §Discussion. NOT a
confirmatory test — does not feed Gate 0.5 verdict, does not require OSF
registration. Pattern matches gate-0-followup/protocol-stratified.py.

Method
------
For each of the 3 sources (SWE-bench Verified, LiveCodeBench, MMLU-Pro), bin the
qualifying pairs by |effect_full| quartile. effect_full is the paired effect
size restricted to shared tasks — a pair-specific ability-gap proxy that is
already computed in the registered pairs.csv. Compute m_b (median |abs_delta|),
p75, p95, sign_flip_rate, and n per quartile. Pool overall as the reference.

Output
------
- pair-stratification-by-ability-gap.csv  (one row per source × quartile + OVERALL)
- pair-stratification.md                  (narrative writeup)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SOURCES = {
    "swebench-verified": "component-c-runs/swebench/swebench-pairs.csv",
    "livecodebench": "component-c-runs/livecodebench/livecodebench-pairs.csv",
    "mmlu-pro": "component-c-runs/mmlu-pro/mmlu-pro-pairs.csv",
}


def stratify(df: pd.DataFrame) -> pd.DataFrame:
    """Bin by |effect_full| quartile and compute per-bin m_b et al."""
    df = df.copy()
    df["ability_gap"] = df["effect_full"].abs()
    df["quartile"] = pd.qcut(df["ability_gap"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rows = []
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        sub = df[df["quartile"] == q]
        rows.append(dict(
            quartile=q,
            n_pairs=int(len(sub)),
            gap_min=float(sub["ability_gap"].min()),
            gap_max=float(sub["ability_gap"].max()),
            gap_median=float(sub["ability_gap"].median()),
            m_b=float(sub["abs_delta"].median()),
            p75_abs_delta=float(sub["abs_delta"].quantile(0.75)),
            p95_abs_delta=float(sub["abs_delta"].quantile(0.95)),
            sign_flip_rate=float(sub["sign_flip"].mean()),
        ))
    rows.append(dict(
        quartile="OVERALL",
        n_pairs=int(len(df)),
        gap_min=float(df["ability_gap"].min()),
        gap_max=float(df["ability_gap"].max()),
        gap_median=float(df["ability_gap"].median()),
        m_b=float(df["abs_delta"].median()),
        p75_abs_delta=float(df["abs_delta"].quantile(0.75)),
        p95_abs_delta=float(df["abs_delta"].quantile(0.95)),
        sign_flip_rate=float(df["sign_flip"].mean()),
    ))
    return pd.DataFrame(rows)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--gate-dir", type=Path, default=Path.cwd())
    p.add_argument("--out", type=Path,
                   default=Path("gate-0-followup/pair-stratification-by-ability-gap.csv"))
    args = p.parse_args()

    all_rows = []
    for src, rel in SOURCES.items():
        path = args.gate_dir / rel
        if not path.exists():
            print(f"[{src}] WARN: not found at {path}; skipping")
            continue
        df = pd.read_csv(path)
        per_source = stratify(df)
        per_source.insert(0, "source", src)
        all_rows.append(per_source)
        print(f"\n=== {src}  (n_pairs total = {len(df):,}) ===")
        print(per_source.to_string(index=False))

    combined = pd.concat(all_rows, ignore_index=True)
    combined.to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")

    # Summary diagnostic: ratio of max-quartile m_b to min-quartile m_b per source
    print("\n=== STRATIFICATION DIAGNOSTIC ===")
    for src in SOURCES:
        sub = combined[(combined["source"] == src) & (combined["quartile"] != "OVERALL")]
        if len(sub) == 0:
            continue
        ratio = sub["m_b"].max() / sub["m_b"].min()
        print(f"  {src}: m_b ratio (max-quartile / min-quartile) = {ratio:.2f}x")
        if ratio < 1.5:
            print(f"    -> BENIGN: pooling defensible; ability-gap pooling does not mask heterogeneity")
        elif ratio < 2.5:
            print(f"    -> MILD heterogeneity; report quartile-conditional m_b in §Discussion")
        else:
            print(f"    -> SUBSTANTIAL heterogeneity; headline must restrict to a quartile or report all four")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
