"""Plimsoll Audit v2 (Q-conditional) — reasoning-mode lift claims, ability-gap-quartile-conditional rule.

Pre-registered methodology: parent OSF DOI 10.17605/OSF.IO/G9WFY (Plimsoll Gate 0.5);
sibling registrations 10.17605/OSF.IO/3PD2A (Addendum-1 robustness pass) and
10.17605/OSF.IO/EKCUQ (Addendum-2 random-subset null).

Addendum-3 (this script's anchor) registers Q-conditional m_b as a confirmatory
audit rule, replacing source-level pooled m_b for any pair whose effect-size
class differs from the source's pair-population median. Motivation: pooled m_b
is dominated by the larger-gap quartiles by approximately an order of magnitude
on every Gate 0.5 source (m_b ratio max-Q / min-Q: 7.6x SWE, 11.1x LCB,
11.1x MMLU per gate-0-followup/pair-stratification.md). Frontier-vs-frontier
pairs live in Q1; comparing them to a pooled m_b inflated by frontier-vs-weak
pairs is methodologically backwards.

Definitions (this script):
  effect_full(a, b)     = mean over shared full tasks of (success_b - success_a)
  effect_margin(a, b)   = same on the [0.30, 0.70] capability-margin task subset
  pair_shift            = |effect_margin - effect_full|
  ability_gap           = |effect_full|  (per Gate 0.5 pair-population convention)
  Q1..Q4                = ability-gap quartiles of the source's qualifying-pair
                          population, computed via pd.qcut on |effect_full|
                          with labels ['Q1','Q2','Q3','Q4'] (pandas default
                          right-inclusive binning)
  Q m_b                 = median |abs_delta| across qualifying pairs in the
                          audited pair's quartile (NOT the pooled source m_b)

Quartile assignment for the audited pair:
  pd.cut(audited.|effect_full|, bins=quartile_edges, include_lowest=True,
         right=True)
  An audited pair whose |effect_full| equals the upper edge of Q_n is assigned
  to Q_n; |effect_full| just above the edge is assigned to Q_{n+1}. This is
  the pandas default and produces the 4 SUBORDINATE / 2 PAIR-UNSTABLE / 7 ROBUST
  count on LCB (the 4 SUBORDINATE matches gate-0-followup/pair-stratification.md;
  the PAIR-UNSTABLE count is recovered by the three-way decision rule below
  that the exploratory writeup simplified to binary). Boundary example:
  Claude Sonnet 4 Thinking at |effect_full| = 0.0910 > LCB Q1/Q2 bin edge
  0.0906 -> Q2 -> SUBORDINATE.

Decision per pair (locked here):
  - SUBORDINATE-TO-SHIFT   |effect_full| < Q m_b
                             The reported lift is smaller than the pair's
                             ability-gap class noise floor.
  - PAIR-UNSTABLE          |effect_full| >= Q m_b AND pair_shift > |effect_full|
                             The lift exceeds the Q-class noise floor, but the
                             pair-specific shift exceeds the lift.
  - ROBUST                 |effect_full| >= Q m_b AND pair_shift <= |effect_full|

Inputs:
  --pairs <SOURCE-pairs.csv>   The source's qualifying-pair distribution from
                                the registered analyze.py output. Used to
                                compute quartile edges and per-quartile m_b.
                                (Inputs FROZEN; this script does not mutate
                                analyze.py's output.)
  --audit <audit.csv>           The audit-input table (one row per pair) with
                                columns: pair, n_full, n_margin, effect_full,
                                effect_margin, pair_shift, sign_flip. Defaults
                                to component-c-runs/livecodebench/audit-reasoning-modes.csv.

Outputs:
  - audit-by-quartile.csv   per-pair (pair, |effect_full|, Q, Q m_b, verdict, ...)
  - stdout summary with SUBORDINATE/PAIR-UNSTABLE/ROBUST counts.

Audit-trail: this script's git commit SHA in https://github.com/smledbetter/plimsoll-gate-0.5
is the audit anchor for OSF Addendum-3. Locked rules above must match the
addendum's SUMMARY exactly.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

QUARTILE_LABELS = ["Q1", "Q2", "Q3", "Q4"]


def compute_quartile_table(pairs_csv: Path) -> tuple[pd.DataFrame, np.ndarray]:
    """Return (per-Q m_b table, quartile edges) for one source.

    Reads the registered pairs.csv (analyze.py output), bins by |effect_full|
    via pd.qcut into 4 equal-frequency quartiles, and returns the per-quartile
    m_b (median |abs_delta|) plus the bin edges for use by pd.cut on audited
    pairs.
    """
    df = pd.read_csv(pairs_csv)
    df = df.copy()
    df["ability_gap"] = df["effect_full"].abs()
    # pd.qcut with retbins=True gives both labels and the edges we need to
    # apply to audited pairs deterministically via pd.cut.
    df["Q"], edges = pd.qcut(
        df["ability_gap"], 4, labels=QUARTILE_LABELS, retbins=True
    )
    table = (
        df.groupby("Q", observed=True)
        .agg(
            n=("ability_gap", "size"),
            gap_min=("ability_gap", "min"),
            gap_max=("ability_gap", "max"),
            m_b=("abs_delta", "median"),
        )
        .reindex(QUARTILE_LABELS)
    )
    return table, edges


def assign_quartile(effect_full_abs: float, edges: np.ndarray) -> str | None:
    """Assign an audited pair to a quartile via the registered bin edges.

    pd.cut with right=True, include_lowest=True replicates pd.qcut's binning
    on the source distribution. A pair whose |effect_full| equals the upper
    edge of Q_n falls in Q_n; just above the edge falls in Q_{n+1}.
    Returns None if |effect_full| is below the lowest edge or above the
    highest edge of the source distribution.
    """
    cat = pd.cut(
        [effect_full_abs],
        bins=edges,
        labels=QUARTILE_LABELS,
        include_lowest=True,
        right=True,
    )
    val = cat[0]
    if pd.isna(val):
        return None
    return str(val)


def evaluate_pair(effect_full: float,
                  effect_margin: float,
                  pair_shift: float,
                  edges: np.ndarray,
                  q_table: pd.DataFrame) -> dict:
    abs_eff = abs(effect_full)
    q = assign_quartile(abs_eff, edges)
    if q is None:
        return {
            "Q": "OUT-OF-RANGE",
            "Q_m_b": float("nan"),
            "verdict": "UNASSIGNED",
            "verdict_short": "out-of-range",
        }
    q_m_b = float(q_table.loc[q, "m_b"])
    above_floor = abs_eff >= q_m_b
    if not above_floor:
        verdict = "SUBORDINATE-TO-SHIFT"
        verdict_short = "below Q m_b"
    elif pair_shift > abs_eff:
        verdict = "PAIR-UNSTABLE"
        verdict_short = "pair-unstable"
    else:
        verdict = "ROBUST"
        verdict_short = "robust"
    return {
        "Q": q,
        "Q_m_b": q_m_b,
        "above_floor": bool(above_floor),
        "verdict": verdict,
        "verdict_short": verdict_short,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pairs", type=Path, required=True,
        help="Source pairs.csv from registered analyze.py output "
             "(e.g. component-c-runs/livecodebench/livecodebench-pairs.csv).",
    )
    parser.add_argument(
        "--audit", type=Path,
        default=Path("component-c-runs/livecodebench/audit-reasoning-modes.csv"),
        help="Audit-input CSV from audit-reasoning-modes.py.",
    )
    parser.add_argument(
        "--out", type=Path, default=Path("audit-by-quartile.csv"),
    )
    args = parser.parse_args()

    if not args.pairs.exists():
        sys.exit(f"ERROR: pairs file not found: {args.pairs}")
    if not args.audit.exists():
        sys.exit(f"ERROR: audit file not found: {args.audit}")

    q_table, edges = compute_quartile_table(args.pairs)
    print(f"Quartile table from {args.pairs.name} "
          f"(n={int(q_table['n'].sum()):,} qualifying pairs):")
    print(q_table.to_string(float_format=lambda x: f"{x:.4f}"))
    print(f"\nBin edges: {[f'{e:.4f}' for e in edges]}")

    audit_df = pd.read_csv(args.audit)
    evaluated = audit_df[audit_df["skipped"] == False].copy()  # noqa: E712
    print(f"\nAuditing {len(evaluated)} pairs from {args.audit.name}\n")

    rows = []
    bar = "=" * 100
    print(bar)
    print(f"{'pair':<46} {'|eff_full|':>10} {'Q':>4} {'Q m_b':>8} "
          f"{'pair_shift':>11}  verdict")
    print(bar)
    for _, r in evaluated.iterrows():
        eff_full = float(r["effect_full"])
        eff_margin = float(r["effect_margin"])
        shift = float(r["pair_shift"])
        result = evaluate_pair(eff_full, eff_margin, shift, edges, q_table)
        row = {
            "pair": r["pair"],
            "n_full": int(r["n_full"]),
            "n_margin": int(r["n_margin"]),
            "effect_full": eff_full,
            "effect_margin": eff_margin,
            "abs_effect_full": abs(eff_full),
            "pair_shift": shift,
            "sign_flip": bool(r["sign_flip"]),
            **result,
        }
        rows.append(row)
        print(f"{r['pair']:<46} {abs(eff_full):>10.4f} {result['Q']:>4} "
              f"{result['Q_m_b']:>8.4f} {shift:>11.4f}  {result['verdict_short']}")
    print(bar)

    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")

    n = len(out)
    n_sub = int((out["verdict"] == "SUBORDINATE-TO-SHIFT").sum())
    n_unstable = int((out["verdict"] == "PAIR-UNSTABLE").sum())
    n_robust = int((out["verdict"] == "ROBUST").sum())
    print(f"\n=== Q-conditional summary across {n} evaluated pairs ===")
    print(f"  SUBORDINATE-TO-SHIFT  {n_sub}/{n} ({n_sub/n:.0%})")
    print(f"  PAIR-UNSTABLE         {n_unstable}/{n} ({n_unstable/n:.0%})")
    print(f"  ROBUST                {n_robust}/{n} ({n_robust/n:.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
