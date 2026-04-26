"""Plimsoll Gate 0.5 — random-subset null-baseline (sampling-artifact test).

Tests whether the registered capability-margin signal is statistically
distinguishable from random task subsampling of the same size. This is the
deepest possible null on the methodology — if it fails, the m_b we measured
is sampling structure dressed up as instability, and the methodology paper
headline must be qualified.

This script is filed under OSF Addendum-2 (DOI 10.17605/OSF.IO/EKCUQ,
registered 2026-04-26T21:20:20Z UTC, public + approved 2026-04-26).
URL: https://osf.io/ekcuq/

The script's commit SHA (23104aa) is the audit anchor for the analytic
choices below; the OSF Addendum-2 DOI EKCUQ is the timestamp anchor for
the variant menu and decision rule.

==============================================================================
NULL HYPOTHESIS
==============================================================================
H0: For pairs that survive the registered inclusion thresholds, the median
across pairs of |effect_margin − effect_full| under capability-margin
filtering [0.30, 0.70] is statistically indistinguishable from the median
under random task-subset selection of the same per-pair size n_margin.

In English: maybe the [0.30, 0.70] band is doing nothing more than any
random subset of the same size would do. If so, the "capability-margin
shift" framing is a misnomer; what we're measuring is finite-sample variance.

==============================================================================
TEST CONSTRUCTION
==============================================================================
For each qualifying pair (a, b):
  - n_margin (this pair) = the integer count of shared tasks falling in the
    pre-registered margin band [0.30, 0.70]; matches analyze.py exactly
  - effect_full = mean((s_a − s_b)) across all n_full shared tasks; FROZEN at
    the analyze.py-computed value
  - For each permutation k in 1..N_PERM:
      random_subset = np.random.choice of size n_margin from the n_full shared
                      tasks WITHOUT replacement; matches per-pair n_margin
      effect_random[k] = mean((s_a − s_b) restricted to random_subset)
      delta_random[k] = |effect_random[k] − effect_full|
  - Store: (delta_random[k] for k in 1..N_PERM)

Per-perm aggregate: median across pairs of delta_random[k] → null_medians[k].
Observed: median across pairs of |effect_margin − effect_full| (read
unchanged from the registered analyze.py output).

z = (observed_median − null_medians.mean()) / null_medians.std()
P(null ≥ obs) = mean(null_medians ≥ observed)

==============================================================================
DECISION RULE (pre-committed BEFORE any held-out run)
==============================================================================
Per source independently:
  z ≥ 3 → capability-margin signal is statistically distinguishable from
          random-subset baseline (signal is REAL, methodology defended for
          this source).
  z < 3 → capability-margin signal is NOT distinguishable from random-subset
          baseline on this source (signal is SAMPLING ARTIFACT for this
          source; methodology paper headline must be qualified).

Layered verdict (all 3 sources):
  PASS:    z ≥ 3 on all 3 sources → headline survives intact.
  PARTIAL: z ≥ 3 on SWE-bench (primary) but < 3 on a secondary → headline
           drops "three independent sources" claim, retains primary.
  FAIL:    z < 3 on SWE-bench primary → headline rewritten; methodology
           paper acknowledges the registered m_b is sampling structure
           on the primary source. Public corrigendum on OSF.

Magnitude check (descriptive, not gated):
  ratio = observed_median / null_medians.mean()
  Reported alongside z as a magnitude diagnostic. ratio ≈ 1 means signal is
  fully sampling-artifact-shaped even if z is technically ≥ 3 due to small
  null variance.

==============================================================================
NOT IN SCOPE
==============================================================================
- Per-pair sign-flip rate of effect_random vs effect_margin (a different
  diagnostic; could be added later under a separate addendum if useful).
- Audit re-run under random-subset m_b (analogous to variant I; could be
  added later).
- Logit-space random-subset null (compose with variant E if desired).

These are not blanket-deferred to dodge attack — they are simply downstream
analyses that this addendum does not commit to running.

==============================================================================
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

DECISION_Z_THRESHOLD = 3.0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True,
                   help="Triples CSV (matches analyze.py / null-baseline.py).")
    p.add_argument("--pairs", type=Path, required=True,
                   help="pairwise-results.csv from analyze.py "
                        "(defines the qualifying pair set; also provides "
                        "observed median |Δ|).")
    p.add_argument("--out", type=Path, required=True,
                   help="Null distribution CSV: one row per permutation.")
    p.add_argument("--source-name", type=str, required=True,
                   choices=["swebench-verified", "livecodebench", "mmlu-pro"])
    p.add_argument("--n-perm", type=int, default=N_PERM)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--margin-lo", type=float, default=MARGIN_LO)
    p.add_argument("--margin-hi", type=float, default=MARGIN_HI)
    p.add_argument("--min-shared-full", type=int, default=MIN_SHARED_FULL)
    p.add_argument("--min-shared-margin", type=int, default=MIN_SHARED_MARGIN)
    p.add_argument("--summary-out", type=Path, default=None,
                   help="Optional: one-row CSV with z, ratio, verdict.")
    args = p.parse_args()

    if not args.input.exists():
        sys.exit(f"ERROR: input not found: {args.input}")
    if not args.pairs.exists():
        sys.exit(f"ERROR: pairs not found: {args.pairs}")

    rng = np.random.default_rng(args.seed)
    df = pd.read_csv(args.input)
    df["success"] = df["success"].astype(int)
    obs = pd.read_csv(args.pairs)
    obs_median = float(obs["abs_delta"].median())
    print(f"[{args.source_name}] Observed median |Δ| (capability-margin): {obs_median:.4f}")
    print(f"  band=[{args.margin_lo:.2f},{args.margin_hi:.2f}]  "
          f"thresholds=({args.min_shared_full},{args.min_shared_margin})")
    print(f"  pairs in observed set: {len(obs):,}")

    task_difficulty = df.groupby("task_id")["success"].mean()
    margin_tasks = set(
        task_difficulty[
            (task_difficulty >= args.margin_lo) & (task_difficulty <= args.margin_hi)
        ].index
    )
    wide = df.pivot_table(
        index="agent", columns="task_id", values="success", aggfunc="mean"
    )

    # Reconstruct per-pair task vectors. For each pair we store:
    #   diff: np.ndarray of (s_a − s_b) over all n_full shared tasks
    #   n_margin: integer count of those that fall in the registered band
    # We do NOT store the margin mask — random subsets are drawn from indices
    # 0..n_full−1, the band membership is irrelevant to the random null.
    pair_data: list[tuple[np.ndarray, int]] = []
    skipped_inclusion = 0
    skipped_missing_agent = 0
    for _, row in obs.iterrows():
        a, b = row["a"], row["b"]
        if a not in wide.index or b not in wide.index:
            skipped_missing_agent += 1
            continue
        sa, sb = wide.loc[a], wide.loc[b]
        both = sa.notna() & sb.notna()
        if int(both.sum()) < args.min_shared_full:
            skipped_inclusion += 1
            continue
        task_ids = sa[both].index
        margin_mask = np.fromiter(
            (t in margin_tasks for t in task_ids), dtype=bool
        )
        n_margin = int(margin_mask.sum())
        if n_margin < args.min_shared_margin:
            skipped_inclusion += 1
            continue
        diff = (sa[both].to_numpy(dtype=float)
                - sb[both].to_numpy(dtype=float))
        pair_data.append((diff, n_margin))

    n_pairs = len(pair_data)
    print(f"  pairs reconstructed: {n_pairs:,} "
          f"(skipped: {skipped_inclusion} inclusion, {skipped_missing_agent} missing-agent)")
    if n_pairs == 0:
        sys.exit("ERROR: no pairs reconstructed.")
    if n_pairs != len(obs):
        print(f"  WARNING: reconstructed {n_pairs} but obs has {len(obs)}; "
              "check --input matches the analyze.py run that produced --pairs.")

    # Pre-compute per-pair effect_full (FROZEN; same for every permutation).
    effect_full = np.array([d.mean() for d, _ in pair_data], dtype=float)

    null_medians = np.zeros(args.n_perm, dtype=float)
    null_p95s = np.zeros(args.n_perm, dtype=float)

    print(f"\nRunning {args.n_perm:,} random-subset permutations × {n_pairs:,} pairs ...")
    for k in range(args.n_perm):
        deltas = np.empty(n_pairs, dtype=float)
        for i, (diff, n_margin) in enumerate(pair_data):
            n_full = diff.shape[0]
            # Sample without replacement; n_margin <= n_full by construction.
            idx = rng.choice(n_full, size=n_margin, replace=False)
            effect_random = float(diff[idx].mean())
            deltas[i] = abs(effect_random - effect_full[i])
        null_medians[k] = float(np.median(deltas))
        null_p95s[k] = float(np.quantile(deltas, 0.95))
        if (k + 1) % 100 == 0:
            print(f"  {k + 1:,}/{args.n_perm:,} done — running null mean: "
                  f"{null_medians[:k+1].mean():.4f}")

    bar = "=" * 60
    print(f"\n{bar}\n[{args.source_name}] RANDOM-SUBSET NULL DISTRIBUTION OF MEDIAN |Δ|\n{bar}")
    print(f"  mean:    {null_medians.mean():.4f}")
    print(f"  std:     {null_medians.std():.4f}")
    print(f"  p2.5:    {np.quantile(null_medians, 0.025):.4f}")
    print(f"  median:  {np.median(null_medians):.4f}")
    print(f"  p97.5:   {np.quantile(null_medians, 0.975):.4f}")

    z = (obs_median - null_medians.mean()) / null_medians.std()
    p_extreme = float((null_medians >= obs_median).mean())
    ratio = obs_median / null_medians.mean() if null_medians.mean() > 0 else float("inf")

    print(f"\n{bar}\n[{args.source_name}] COMPARISON\n{bar}")
    print(f"  observed median |Δ| (cap-margin): {obs_median:.4f}")
    print(f"  null mean (random-subset):        {null_medians.mean():.4f}")
    print(f"  z-score:                          {z:+.2f}")
    print(f"  P(null ≥ obs):                    {p_extreme:.4f}")
    print(f"  ratio (obs / null_mean):          {ratio:.2f}x")

    print(f"\n{bar}\n[{args.source_name}] DECISION\n{bar}")
    if z >= DECISION_Z_THRESHOLD:
        verdict = (
            f"DEFENDED — z = {z:+.2f} ≥ {DECISION_Z_THRESHOLD}: "
            f"capability-margin signal is statistically distinguishable from "
            f"random-subset baseline. Plimsoll signal on {args.source_name} is "
            f"NOT a sampling artifact at this n. Magnitude ratio: {ratio:.2f}x."
        )
    else:
        verdict = (
            f"FAILED — z = {z:+.2f} < {DECISION_Z_THRESHOLD}: "
            f"capability-margin signal on {args.source_name} is NOT "
            f"distinguishable from random task-subset selection of the same "
            f"size. The registered m_b is plausibly sampling artifact on this "
            f"source. Methodology paper headline must be qualified or "
            f"rewritten for {args.source_name}."
        )
    print(verdict)

    pd.DataFrame({
        "perm": range(args.n_perm),
        "null_median": null_medians,
        "null_p95": null_p95s,
    }).to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")

    if args.summary_out is not None:
        pd.DataFrame([dict(
            source=args.source_name,
            test="random-subset-null",
            obs_median_abs_delta=obs_median,
            null_mean=float(null_medians.mean()),
            null_std=float(null_medians.std()),
            z=float(z),
            p_extreme=p_extreme,
            ratio_obs_over_null_mean=float(ratio),
            decision="defended" if z >= DECISION_Z_THRESHOLD else "failed",
            n_pairs=n_pairs,
            n_perm=args.n_perm,
            seed=args.seed,
        )]).to_csv(args.summary_out, index=False)
        print(f"Wrote {args.summary_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
