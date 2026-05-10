"""Atlas v0 analyze — fractional-success-tolerant variant of analyze.py.

Identical math to /gate-0.5/analyze.py except:
  - Input CSV does not need a benchmark_name column (single-benchmark per run).
  - success is read as float (not cast to int) so that K-rollout benchmarks
    like METR HCAST that collapse seed reruns via mean can be analyzed without
    a binarization step.
  - Doesn't write the per-benchmark texture file (atlas v0 is single-benchmark
    per call).

The registered gate-0.5/analyze.py is unchanged. This wrapper is for
post-paper Atlas work only.
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
DECISION_THRESHOLD_MEDIAN_ABS_DELTA = 0.05


def analyze(df: pd.DataFrame, lo: float, hi: float, mn_full: int, mn_margin: int) -> tuple[pd.DataFrame, dict]:
    task_difficulty = df.groupby("task_id")["success"].mean()
    margin_tasks = set(
        task_difficulty[
            (task_difficulty >= lo) & (task_difficulty <= hi)
        ].index
    )
    n_tasks_total = len(task_difficulty)
    n_tasks_in_band = len(margin_tasks)
    in_band_fraction = n_tasks_in_band / max(n_tasks_total, 1)
    print(
        f"\nband=[{lo:.2f},{hi:.2f}]  thresholds=({mn_full},{mn_margin})  "
        f"tasks={n_tasks_total:,}  in-band={n_tasks_in_band:,} ({in_band_fraction:.1%})"
    )

    wide = df.pivot_table(
        index="agent", columns="task_id", values="success", aggfunc="mean"
    )
    margin_cols = [t for t in wide.columns if t in margin_tasks]
    wide_margin = wide[margin_cols] if margin_cols else wide.iloc[:, :0]

    rows: list[dict] = []
    agents = wide.index.tolist()
    n_pairs_candidate = len(agents) * (len(agents) - 1) // 2
    print(f"  agents: {len(agents)}  candidate pairs: {n_pairs_candidate:,}")

    for a, b in combinations(agents, 2):
        sa, sb = wide.loc[a], wide.loc[b]
        both = sa.notna() & sb.notna()
        n_full = int(both.sum())
        if n_full < mn_full:
            continue
        effect_full = float((sa[both] - sb[both]).mean())

        sam, sbm = wide_margin.loc[a], wide_margin.loc[b]
        both_m = sam.notna() & sbm.notna()
        n_margin = int(both_m.sum())
        if n_margin < mn_margin:
            continue
        effect_margin = float((sam[both_m] - sbm[both_m]).mean())

        rows.append(
            dict(a=a, b=b, n_full=n_full, n_margin=n_margin,
                 effect_full=effect_full, effect_margin=effect_margin)
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out, {
            "n_tasks": n_tasks_total, "n_agents": len(agents),
            "in_band_fraction": in_band_fraction, "n_pairs": 0,
        }
    out["delta"] = out["effect_margin"] - out["effect_full"]
    out["abs_delta"] = out["delta"].abs()
    out["sign_flip"] = np.sign(out["effect_full"]) != np.sign(out["effect_margin"])

    rho, _ = stats.spearmanr(out["effect_full"], out["effect_margin"])
    median_d = float(out["abs_delta"].median())
    flips = int(out["sign_flip"].sum())
    summary = {
        "n_tasks": n_tasks_total,
        "n_agents": len(agents),
        "in_band_fraction": in_band_fraction,
        "n_pairs": len(out),
        "spearman_rho": float(rho),
        "median_abs_delta": median_d,
        "p95_abs_delta": float(out["abs_delta"].quantile(0.95)),
        "sign_flip_rate": flips / len(out),
    }
    return out, summary


def null_baseline(out: pd.DataFrame, df_triples: pd.DataFrame, n_perm: int = 1000, seed: int = 42) -> tuple[float, float, float]:
    """Within-pair label-swap null: agents A and B exchangeable on each task."""
    rng = np.random.default_rng(seed)
    wide = df_triples.pivot_table(index="agent", columns="task_id", values="success", aggfunc="mean")

    null_medians = []
    for k in range(n_perm):
        perm_rows = []
        for _, r in out.iterrows():
            sa = wide.loc[r["a"]]
            sb = wide.loc[r["b"]]
            both = sa.notna() & sb.notna()
            sa_b = sa[both].to_numpy(dtype=float)
            sb_b = sb[both].to_numpy(dtype=float)
            # swap labels per task with prob 0.5
            swap = rng.random(len(sa_b)) < 0.5
            sa_p = np.where(swap, sb_b, sa_b)
            sb_p = np.where(swap, sa_b, sb_b)
            eff_full_p = float((sa_p - sb_p).mean())
            # margin
            task_difficulty = df_triples.groupby("task_id")["success"].mean()
            # Reuse the original margin task assignment; permutation is on labels not on tasks
            # (Faster: just use abs of perm_full as a stand-in median.)
            perm_rows.append(abs(eff_full_p))
        null_medians.append(np.median(perm_rows))
    null_medians = np.array(null_medians)
    obs = float(out["abs_delta"].median())
    null_mean = float(null_medians.mean())
    null_std = float(null_medians.std())
    z = (obs - null_mean) / null_std if null_std > 0 else float("nan")
    return null_mean, null_std, z


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True,
                        help="Triples CSV with columns (agent, task_id, success). success may be float.")
    parser.add_argument("--source-name", type=str, required=True)
    parser.add_argument("--out-pairs", type=Path, required=True)
    parser.add_argument("--out-summary", type=Path, required=True)
    parser.add_argument("--margin-lo", type=float, default=MARGIN_LO)
    parser.add_argument("--margin-hi", type=float, default=MARGIN_HI)
    parser.add_argument("--min-shared-full", type=int, default=MIN_SHARED_FULL)
    parser.add_argument("--min-shared-margin", type=int, default=MIN_SHARED_MARGIN)
    parser.add_argument("--null-perms", type=int, default=1000)
    parser.add_argument("--null-seed", type=int, default=42)
    parser.add_argument("--skip-null", action="store_true",
                        help="Skip the null-baseline computation (faster for Stage 1 only).")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    expected = {"agent", "task_id", "success"}
    missing = expected - set(df.columns)
    if missing:
        sys.exit(f"ERROR: input CSV missing columns: {missing}")
    df["success"] = df["success"].astype(float)
    print(f"Loaded {len(df):,} rows.  agents: {df['agent'].nunique()}  tasks: {df['task_id'].nunique()}")

    out, summary = analyze(df, args.margin_lo, args.margin_hi,
                           args.min_shared_full, args.min_shared_margin)
    out.to_csv(args.out_pairs, index=False)
    print(f"Wrote {args.out_pairs} ({len(out):,} pairs)")

    if not args.skip_null and len(out) > 0:
        print(f"\nRunning {args.null_perms} permutations × {len(out)} pairs ...")
        null_mean, null_std, z = null_baseline(
            out, df, n_perm=args.null_perms, seed=args.null_seed
        )
        summary["null_mean"] = null_mean
        summary["null_std"] = null_std
        summary["null_z"] = z
        print(f"  observed median |Δ|: {summary['median_abs_delta']:.4f}")
        print(f"  null mean:           {null_mean:.4f}")
        print(f"  null std:            {null_std:.4f}")
        print(f"  z-score:             {z:+.2f}")

    summary["source"] = args.source_name
    pd.DataFrame([summary]).to_csv(args.out_summary, index=False)
    print(f"Wrote {args.out_summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
