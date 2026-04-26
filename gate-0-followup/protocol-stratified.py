"""Plimsoll Gate 0 exploratory follow-up — protocol-stratified |Δ effect size|.

Attacks README open question #3: "Effect-size stability under scaffold/temporal
shift specifically. Gate 0 measured stability across agent-pair composition.
Ndzomga measured rank stability across his 5 protocols (LOAO/LOSO/temporal/
random/intra-scaffold). The natural follow-up is computing |Δ effect size|
across those same protocols — does the instability worsen under scaffold shift
specifically? (Tractable on the same data.)"

==============================================================================
EXPLORATORY — NOT PLIMSOLL-COMPLIANT, NOT OSF-REGISTERED.
==============================================================================

This script descends from Gate 0, which is itself reclassified as exploratory
motivation. Output is descriptive supplementary texture, not a confirmatory
claim. The methodology paper should cite results from this script in
Limitations / Future Work, never as a load-bearing finding.

If a result here turns out to be paper-headline-worthy, the upgrade path is
**registered prospective replication on held-out data** (Gate 0.75 / Gate 1.5
shape), not retroactive promotion of this exploratory analysis.

Audit anchor: this file's git commit timestamp predates the run; analytic
choices (scaffold parser, temporal bucket boundary, pair stratification rule,
band, inclusion thresholds) are pinned at the SHA the run uses.

==============================================================================

Method:
  1. Read Ndzomga 2026 heatmap (22,304 rows: agent, task, success, benchmark,
     download_timestamp).
  2. Parse scaffold per agent: "Scaffold (Model)" → "Scaffold". Same logic as
     Ndzomga's `scripts/data.py:parse_scaffold_from_name`.
  3. Parse year-month per agent from download_timestamp.
  4. For each (benchmark, pair_a, pair_b): compute effect_full and
     effect_margin in Plimsoll [0.30, 0.70] band; median |Δ| reused from
     Gate 0 pipeline.
  5. Stratify pairs:
       SCAFFOLD: intra (a.scaffold == b.scaffold) vs inter (different)
       TEMPORAL: intra (same year-month download) vs inter (different)
  6. Report median |Δ effect size| per stratum per benchmark.

Decision rule (descriptive, not gated):
  - Report ratio inter/intra for each stratum.
  - Flag benchmarks where inter > 2× intra as suggestive of scaffold/temporal-
    driven instability.

Output:
  protocol-stratified-summary.csv  — one row per (benchmark, stratification, stratum)
  protocol-stratified-pairs.csv    — one row per pair × benchmark with stratum labels
"""
from __future__ import annotations

import argparse
import re
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

MARGIN_LO = 0.30
MARGIN_HI = 0.70
MIN_SHARED_FULL = 20
MIN_SHARED_MARGIN = 8


def parse_scaffold_from_name(name: str) -> str:
    """Match Ndzomga 2026 `scripts/data.py:parse_scaffold_from_name`."""
    if "(" in name:
        return name.split("(")[0].strip()
    return name.split()[0] if " " in name else name


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def parse_release_year_month(name: str) -> str | None:
    """Extract model release YYYY-MM from agent name's parenthetical
    "Scaffold (Model (Month Year))" — matches Ndzomga 2026
    `scripts/data.py:parse_date_from_name`."""
    m = re.search(r"\(([A-Za-z]+)\s+(\d{4})\)", name)
    if not m:
        return None
    month = _MONTHS.get(m.group(1).lower())
    if month is None:
        return None
    return f"{m.group(2)}-{month:02d}"


def compute_pair_effects(df: pd.DataFrame) -> pd.DataFrame:
    """Per-(benchmark, pair) effect_full, effect_margin, |Δ|."""
    out_rows: list[dict] = []
    for benchmark in sorted(df["benchmark_name"].unique()):
        bdf = df[df["benchmark_name"] == benchmark]
        # task difficulty
        task_diff = bdf.groupby("task_id")["success"].mean()
        margin_tasks = set(task_diff[
            (task_diff >= MARGIN_LO) & (task_diff <= MARGIN_HI)
        ].index)
        if len(margin_tasks) < MIN_SHARED_MARGIN:
            continue
        wide = bdf.pivot_table(
            index="agent", columns="task_id", values="success", aggfunc="mean"
        )
        agents = wide.index.tolist()
        for a, b in combinations(agents, 2):
            sa, sb = wide.loc[a], wide.loc[b]
            both = sa.notna() & sb.notna()
            n_full = int(both.sum())
            if n_full < MIN_SHARED_FULL:
                continue
            ef = float((sa[both] - sb[both]).mean())
            task_ids = sa[both].index
            margin_mask = np.fromiter(
                (t in margin_tasks for t in task_ids), dtype=bool
            )
            n_margin = int(margin_mask.sum())
            if n_margin < MIN_SHARED_MARGIN:
                continue
            sa_arr = sa[both].to_numpy(dtype=float)[margin_mask]
            sb_arr = sb[both].to_numpy(dtype=float)[margin_mask]
            em = float((sa_arr - sb_arr).mean())
            out_rows.append(dict(
                benchmark=benchmark, a=a, b=b,
                n_full=n_full, n_margin=n_margin,
                effect_full=ef, effect_margin=em,
                abs_delta=abs(em - ef),
                sign_flip=(np.sign(ef) != np.sign(em)
                           and ef != 0 and em != 0),
            ))
    return pd.DataFrame(out_rows)


def stratify_summary(pairs: pd.DataFrame, agent_meta: pd.DataFrame) -> pd.DataFrame:
    """Add stratum labels and aggregate per benchmark × stratification × stratum."""
    meta = agent_meta.set_index("agent")
    pairs = pairs.copy()
    pairs["scaffold_a"] = pairs["a"].map(meta["scaffold"])
    pairs["scaffold_b"] = pairs["b"].map(meta["scaffold"])
    pairs["yearmonth_a"] = pairs["a"].map(meta["yearmonth"])
    pairs["yearmonth_b"] = pairs["b"].map(meta["yearmonth"])
    pairs["scaffold_stratum"] = np.where(
        pairs["scaffold_a"] == pairs["scaffold_b"],
        "intra-scaffold", "inter-scaffold",
    )
    pairs["temporal_stratum"] = np.where(
        pairs["yearmonth_a"] == pairs["yearmonth_b"],
        "intra-month", "inter-month",
    )
    # Where a yearmonth is missing, mark NaN -> exclude from temporal stratification.
    pairs.loc[pairs["yearmonth_a"].isna() | pairs["yearmonth_b"].isna(),
              "temporal_stratum"] = pd.NA

    rows: list[dict] = []
    for benchmark in sorted(pairs["benchmark"].unique()):
        bp = pairs[pairs["benchmark"] == benchmark]
        # All-pairs (Gate 0 baseline reproduction)
        rows.append(dict(
            benchmark=benchmark, stratification="all", stratum="all",
            n_pairs=len(bp),
            median_abs_delta=float(bp["abs_delta"].median()) if len(bp) else float("nan"),
            p75_abs_delta=float(bp["abs_delta"].quantile(0.75)) if len(bp) else float("nan"),
            p95_abs_delta=float(bp["abs_delta"].quantile(0.95)) if len(bp) else float("nan"),
            sign_flip_rate=float(bp["sign_flip"].mean()) if len(bp) else float("nan"),
        ))
        for stratum in ("intra-scaffold", "inter-scaffold"):
            sp = bp[bp["scaffold_stratum"] == stratum]
            rows.append(dict(
                benchmark=benchmark, stratification="scaffold", stratum=stratum,
                n_pairs=len(sp),
                median_abs_delta=float(sp["abs_delta"].median()) if len(sp) else float("nan"),
                p75_abs_delta=float(sp["abs_delta"].quantile(0.75)) if len(sp) else float("nan"),
                p95_abs_delta=float(sp["abs_delta"].quantile(0.95)) if len(sp) else float("nan"),
                sign_flip_rate=float(sp["sign_flip"].mean()) if len(sp) else float("nan"),
            ))
        for stratum in ("intra-month", "inter-month"):
            sp = bp[bp["temporal_stratum"] == stratum]
            rows.append(dict(
                benchmark=benchmark, stratification="temporal", stratum=stratum,
                n_pairs=len(sp),
                median_abs_delta=float(sp["abs_delta"].median()) if len(sp) else float("nan"),
                p75_abs_delta=float(sp["abs_delta"].quantile(0.75)) if len(sp) else float("nan"),
                p95_abs_delta=float(sp["abs_delta"].quantile(0.95)) if len(sp) else float("nan"),
                sign_flip_rate=float(sp["sign_flip"].mean()) if len(sp) else float("nan"),
            ))
    return pd.DataFrame(rows), pairs


def report(summary: pd.DataFrame) -> None:
    bar = "=" * 78
    print(bar)
    print("PROTOCOL-STRATIFIED |Δ EFFECT SIZE| — exploratory texture (NOT confirmatory)")
    print(bar)
    for benchmark in sorted(summary["benchmark"].unique()):
        bs = summary[summary["benchmark"] == benchmark]
        print(f"\n--- {benchmark} ---")
        for _, row in bs.iterrows():
            print(f"  {row['stratification']:>9s}.{row['stratum']:<15s}  "
                  f"n={int(row['n_pairs']):>4d}  "
                  f"median|Δ|={row['median_abs_delta']:.4f}  "
                  f"p95={row['p95_abs_delta']:.4f}  "
                  f"flip={row['sign_flip_rate']:.1%}")
        # Compute and print ratios
        try:
            intra_s = bs[(bs.stratification == "scaffold") & (bs.stratum == "intra-scaffold")]["median_abs_delta"].iloc[0]
            inter_s = bs[(bs.stratification == "scaffold") & (bs.stratum == "inter-scaffold")]["median_abs_delta"].iloc[0]
            if intra_s > 0:
                ratio_s = inter_s / intra_s
                flag_s = " ** SUGGESTIVE (>2x)" if ratio_s > 2 else ""
                print(f"  scaffold ratio (inter/intra):  {ratio_s:.2f}x{flag_s}")
        except (IndexError, ZeroDivisionError):
            pass
        try:
            intra_t = bs[(bs.stratification == "temporal") & (bs.stratum == "intra-month")]["median_abs_delta"].iloc[0]
            inter_t = bs[(bs.stratification == "temporal") & (bs.stratum == "inter-month")]["median_abs_delta"].iloc[0]
            if intra_t > 0:
                ratio_t = inter_t / intra_t
                flag_t = " ** SUGGESTIVE (>2x)" if ratio_t > 2 else ""
                print(f"  temporal ratio (inter/intra):  {ratio_t:.2f}x{flag_t}")
        except (IndexError, ZeroDivisionError):
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True,
                        help="Path to Ndzomga's all_benchmarks_task_heatmap_data.csv")
    parser.add_argument("--out-summary", type=Path,
                        default=Path("protocol-stratified-summary.csv"))
    parser.add_argument("--out-pairs", type=Path,
                        default=Path("protocol-stratified-pairs.csv"))
    args = parser.parse_args()

    if not args.data.exists():
        sys.exit(f"ERROR: data not found: {args.data}")

    df = pd.read_csv(args.data)
    df = df.rename(columns={
        "Agent Name": "agent",
        "Task ID": "task_id",
        "Success": "success",
    })
    df["success"] = pd.to_numeric(df["success"], errors="coerce").fillna(0).astype(int)
    print(f"Loaded {len(df):,} rows; agents={df['agent'].nunique()}; "
          f"tasks={df['task_id'].nunique()}; benchmarks={df['benchmark_name'].nunique()}")

    # Build agent metadata
    agent_meta = (
        df[["agent"]]
        .drop_duplicates(subset=["agent"])
        .copy()
    )
    agent_meta["scaffold"] = agent_meta["agent"].apply(parse_scaffold_from_name)
    agent_meta["yearmonth"] = agent_meta["agent"].apply(parse_release_year_month)
    n_dated = int(agent_meta["yearmonth"].notna().sum())
    print(f"Agent meta: {len(agent_meta)} agents; "
          f"scaffolds={agent_meta['scaffold'].nunique()}; "
          f"release year-months parsed={n_dated}/{len(agent_meta)}; "
          f"distinct year-months={agent_meta['yearmonth'].dropna().nunique()}")

    pairs = compute_pair_effects(df)
    print(f"Computed pairs: {len(pairs):,}")
    summary, pairs_with_strata = stratify_summary(pairs, agent_meta)
    summary.to_csv(args.out_summary, index=False)
    pairs_with_strata.to_csv(args.out_pairs, index=False)
    print(f"\nWrote {args.out_summary}")
    print(f"Wrote {args.out_pairs}")
    report(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
