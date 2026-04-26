"""Plimsoll Audit v1 — reasoning-mode lift claims on LiveCodeBench.

Pre-registered methodology: OSF DOI 10.17605/OSF.IO/G9WFY (Plimsoll Gate 0.5).
LiveCodeBench null-baseline result (n=1000 perms, frozen 2026-04-26):
  median absolute paired-effect-size shift under capability-margin filtering
  = 0.156 at α=0.001 (z = +374.90 vs Rasch null permutation distribution).

This audit asks: for paired reasoning/non-reasoning (or effort-tier) model
runs on LiveCodeBench, do the headline effect-size lifts exceed the
benchmark's median capability-margin shift?

Definitions:
  effect_full   = mean over shared full tasks of (success_advanced − success_base)
  effect_margin = same on the [0.30, 0.70] capability-margin task subset
  pair_shift    = |effect_margin − effect_full|  (this pair's shift magnitude)
  m_b           = median |Δ paired effect size| across all qualifying pairs
                  on benchmark b (the per-benchmark Plimsoll statistic;
                  for LiveCodeBench, m_b = 0.156)

Decision per pair:
  - SUBORDINATE-TO-SHIFT   |effect_full| < m_b
                             The reported lift is smaller than the
                             benchmark's median capability-margin shift.
                             The effect-size claim is contingent on the
                             specific task selection in a way that exceeds
                             the claim's own magnitude.
  - PAIR-UNSTABLE          |effect_full| ≥ m_b AND pair_shift > |effect_full|
                             The lift exceeds the benchmark median, but
                             the pair-specific shift exceeds the lift —
                             the effect is itself unstable to the
                             margin-band view.
  - ROBUST                 |effect_full| ≥ m_b AND pair_shift ≤ |effect_full|
                             The lift exceeds the benchmark median and
                             is stable across full vs margin-band views.

Output: one row per pair to stdout + audit-reasoning-modes.csv.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

M_B_LIVECODEBENCH = 0.156  # median |Δ paired effect size| on LiveCodeBench
                            # (n=1000 permutations, frozen 2026-04-26)
MARGIN_LO = 0.30
MARGIN_HI = 0.70
MIN_SHARED_FULL = 20
MIN_SHARED_MARGIN = 8


# (description, base_agent_dir, advanced_agent_dir)
PAIRS: list[tuple[str, str, str]] = [
    # Anthropic — reasoning-mode flag
    ("Claude Opus 4 — Thinking lift",
     "Claude-Opus-4", "Claude-Opus-4 (Thinking)"),
    ("Claude Sonnet 4 — Thinking lift",
     "Claude-Sonnet-4", "Claude-Sonnet-4 (Thinking)"),

    # Google — Gemini Thinking variants vs Exp baseline
    ("Gemini Flash 2.0 — Thinking vs Exp",
     "Gemini-Flash-2.0-Exp", "Gemini-Flash-2.0-Thinking"),
    ("Gemini Flash 2.0 — Thinking-01-21 vs Exp",
     "Gemini-Flash-2.0-Exp", "Gemini-Flash-2.0-Thinking-01-21"),
    ("Gemini Flash 2.0 — Thinking-12-19 vs Exp",
     "Gemini-Flash-2.0-Exp", "Gemini-Flash-2.0-Thinking-12-19"),

    # OpenAI O-series — effort-tier extremes
    ("O1 — High vs Low effort",
     "O1-2024-12-17 (Low)", "O1-2024-12-17 (High)"),
    ("O1 — High vs Med effort",
     "O1-2024-12-17 (Med)", "O1-2024-12-17 (High)"),
    ("O3-Mini — High vs Low effort",
     "O3-Mini-2025-01-31 (Low)", "O3-Mini-2025-01-31 (High)"),
    ("O3-Mini — High vs Med effort",
     "O3-Mini-2025-01-31 (Med)", "O3-Mini-2025-01-31 (High)"),
    ("O4-Mini — High vs Low effort",
     "O4-Mini (Low)", "O4-Mini (High)"),
    ("O4-Mini — High vs Medium effort",
     "O4-Mini (Medium)", "O4-Mini (High)"),

    # Cross-architecture reasoning vs base
    ("DeepSeek R1-0528 vs V3 base",
     "DeepSeek-V3", "DeepSeek-R1-0528"),
    ("QwQ-32B-Preview vs Qwen2.5-Ins-32B",
     "Qwen2.5-Ins-32B", "QwQ-32B-Preview"),
]


def load_triples(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["success"] = df["success"].astype(int)
    return df


def evaluate_pair(df: pd.DataFrame,
                  base_agent: str,
                  advanced_agent: str,
                  m_b: float) -> dict | None:
    """Compute effect_full, effect_margin, pair_shift, verdict for one pair."""
    task_difficulty = df.groupby("task_id")["success"].mean()
    margin_tasks = set(
        task_difficulty[
            (task_difficulty >= MARGIN_LO) & (task_difficulty <= MARGIN_HI)
        ].index
    )

    wide = df.pivot_table(
        index="agent", columns="task_id", values="success", aggfunc="mean"
    )
    if base_agent not in wide.index or advanced_agent not in wide.index:
        missing = [a for a in (base_agent, advanced_agent) if a not in wide.index]
        return {"missing_agents": missing}

    sa = wide.loc[base_agent]
    sb = wide.loc[advanced_agent]
    both = sa.notna() & sb.notna()
    n_full = int(both.sum())
    if n_full < MIN_SHARED_FULL:
        return {"insufficient_overlap": (n_full, "full")}

    effect_full = float((sb[both] - sa[both]).mean())

    task_ids_both = sa[both].index
    margin_mask = np.fromiter(
        (t in margin_tasks for t in task_ids_both), dtype=bool
    )
    n_margin = int(margin_mask.sum())
    if n_margin < MIN_SHARED_MARGIN:
        return {"insufficient_overlap": (n_margin, "margin")}

    sa_m = sa[both].to_numpy(dtype=float)[margin_mask]
    sb_m = sb[both].to_numpy(dtype=float)[margin_mask]
    effect_margin = float((sb_m - sa_m).mean())
    pair_shift = abs(effect_margin - effect_full)
    sign_flip = (np.sign(effect_full) != np.sign(effect_margin)
                 and effect_full != 0 and effect_margin != 0)

    above_floor = abs(effect_full) >= m_b
    if not above_floor:
        verdict = "SUBORDINATE-TO-SHIFT"
        verdict_short = "below m_b"
    elif pair_shift > abs(effect_full):
        verdict = "PAIR-UNSTABLE"
        verdict_short = "pair-unstable"
    else:
        verdict = "ROBUST"
        verdict_short = "robust"

    return {
        "n_full": n_full,
        "n_margin": n_margin,
        "effect_full": effect_full,
        "effect_margin": effect_margin,
        "pair_shift": pair_shift,
        "sign_flip": bool(sign_flip),
        "above_floor": bool(above_floor),
        "verdict": verdict,
        "verdict_short": verdict_short,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True,
                        help="LiveCodeBench triples CSV from prep-livecodebench.py.")
    parser.add_argument("--out", type=Path,
                        default=Path("audit-reasoning-modes.csv"))
    parser.add_argument("--m-b", type=float,
                        default=M_B_LIVECODEBENCH,
                        help="Per-benchmark median |Δ paired effect size| "
                             "(the Plimsoll capability-margin statistic m_b).")
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: {args.input} not found.")

    df = load_triples(args.input)
    print(f"Loaded {len(df):,} rows; agents={df['agent'].nunique()}; "
          f"tasks={df['task_id'].nunique()}")
    print(f"Benchmark median |Δ paired effect size| (m_b) = {args.m_b:.4f}")
    print(f"  source: LiveCodeBench null-baseline at OSF DOI 10.17605/OSF.IO/G9WFY\n")

    rows = []
    bar = "=" * 96
    print(bar)
    print(f"{'pair':<46} {'eff_full':>9} {'eff_margin':>11} "
          f"{'pair_shift':>11}  verdict")
    print(bar)
    for label, base, adv in PAIRS:
        result = evaluate_pair(df, base, adv, args.m_b)
        if result is None:
            continue
        if "missing_agents" in result:
            print(f"{label:<46}  SKIP: missing {result['missing_agents']}")
            rows.append({"pair": label, "skipped": True,
                         "skip_reason": f"missing {result['missing_agents']}"})
            continue
        if "insufficient_overlap" in result:
            n, kind = result["insufficient_overlap"]
            print(f"{label:<46}  SKIP: only {n} shared {kind} tasks")
            rows.append({"pair": label, "skipped": True,
                         "skip_reason": f"only {n} shared {kind}"})
            continue
        rows.append({"pair": label, "skipped": False, "skip_reason": "",
                     **result})
        flip = " sign-flip" if result["sign_flip"] else ""
        print(f"{label:<46} {result['effect_full']:>+9.4f} "
              f"{result['effect_margin']:>+11.4f} "
              f"{result['pair_shift']:>11.4f}  "
              f"{result['verdict_short']}{flip}")

    print(bar)
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(f"\nWrote {args.out} ({len(out)} rows)")

    if "verdict" in out.columns:
        evaluated = out[~out["skipped"]]
        n = len(evaluated)
        n_sub = int((evaluated["verdict"] == "SUBORDINATE-TO-SHIFT").sum())
        n_unstable = int((evaluated["verdict"] == "PAIR-UNSTABLE").sum())
        n_robust = int((evaluated["verdict"] == "ROBUST").sum())
        n_flips = int(evaluated["sign_flip"].sum())
        print(f"\n=== Summary across {n} evaluated pairs ===")
        print(f"  SUBORDINATE-TO-SHIFT (|effect_full| < m_b={args.m_b:.3f}): "
              f"{n_sub}/{n} ({n_sub/n:.0%})")
        print(f"  PAIR-UNSTABLE        (above m_b but pair_shift > effect):     "
              f"{n_unstable}/{n} ({n_unstable/n:.0%})")
        print(f"  ROBUST                                                        "
              f"{n_robust}/{n} ({n_robust/n:.0%})")
        print(f"  margin-band sign-flips:                                       "
              f"{n_flips}/{n} ({n_flips/n:.0%})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
