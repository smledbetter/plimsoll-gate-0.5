"""Plimsoll Gate 0.5 Component A — simulation-based power analysis.

Generates synthetic (agent, task) score matrices under three generative
families (Rasch / 1PL IRT, compensatory MIRT, non-compensatory MIRT),
applies the Gate 0 pipeline (paired effect size with capability-margin
filtering), and produces:

  1. Per-source per-model distributions of median |Δ paired effect size|.
     Theoretical-anchor lookup: which generative model + parameter
     combination reproduces the Gate 0 observed median |Δ| ≈ 0.090?

  2. Per-source MDE — minimum detectable effect:
     Under each MIRT family, what's the smallest signal-strength
     parameter combo whose median |Δ| distribution exceeds the Rasch
     no-signal null's α=0.001 critical value with ≥80% power?

The MDE numbers populate the OSF pre-registration's power section.
The theoretical-anchor lookup feeds the methodology paper's discussion
of what skill-structure assumption explains Gate 0.

Outputs (under --out-dir, default `simulation-results/`):
  simulation-results.csv  — one row per simulation (raw)
  simulation-summary.csv  — per-cell aggregates
  power-table.csv         — power per (source, model, params) cell
  mde-table.csv           — per-source MDE summary for the pre-reg

Run:
  python simulation.py                   # default 100 sims/cell
  python simulation.py --n-sims 500      # tighter quantiles for the OSF table

Frozen artifact for OSF Component A registration. Parameter grids and
seed are fixed at module level; do not edit after registration without
re-registering. Source shapes are pinned to the Component B inventory
(see gate-0.5/README.md and gate-0.5/inventory-supplement/).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import rankdata


def fast_spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman ρ via rankdata + Pearson on ranks.

    Equivalent to scipy.stats.spearmanr (with average-ties handling) but
    much cheaper because we skip the p-value tail computation. Significant
    speedup for the inner loop on the SWE-bench shape (~9000 pair vector).
    """
    rx = rankdata(x)
    ry = rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])

# === Frozen configuration ===

SEED = 20260426

# Margin band — same as Gate 0 (do not change)
MARGIN_LO = 0.30
MARGIN_HI = 0.70
MIN_MARGIN_TASKS = 8

# Held-out source shapes (from Component B inventory, locked 2026-04-26)
SOURCES: dict[str, dict[str, int]] = {
    "swebench-verified": dict(n_agents=134, n_tasks=500),
    "livecodebench":     dict(n_agents=50,  n_tasks=1055),
    "mmlu-pro":          dict(n_agents=48,  n_tasks=12032),
}

# Signal-strength sweep grid
ABILITY_SCALES    = [0.5, 1.0, 1.5, 2.0]   # std of agent ability θ
DIFFICULTY_SCALES = [0.5, 1.0, 1.5, 2.0]   # std of task difficulty β
MIRT_DIMS         = [2, 3, 5]               # MIRT skill-vector dimensions

# Decision-rule thresholds for downstream MDE (matches gate-0.5/README.md)
ALPHA_LEVEL  = 0.001
POWER_TARGET = 0.80


# === Generative models ===

def gen_rasch(rng: np.random.Generator,
              n_agents: int, n_tasks: int,
              ability_scale: float = 1.0,
              difficulty_scale: float = 1.0) -> np.ndarray:
    """1PL IRT — null model. P(success | i, j) = σ(θ_i - β_j)."""
    theta = rng.normal(0, ability_scale, n_agents)
    beta  = rng.normal(0, difficulty_scale, n_tasks)
    p = expit(theta[:, None] - beta[None, :])
    return rng.binomial(1, p).astype(float)


def gen_compensatory_mirt(rng: np.random.Generator,
                          n_agents: int, n_tasks: int, d: int,
                          ability_scale: float = 1.0,
                          difficulty_scale: float = 1.0) -> np.ndarray:
    """Compensatory MIRT. P(success) = σ(θ_i · α_j - β_j). Skills substitute."""
    theta = rng.normal(0, ability_scale, (n_agents, d))
    alpha = rng.normal(0, 1.0, (n_tasks, d))            # task skill loadings
    beta  = rng.normal(0, difficulty_scale, n_tasks)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        p = expit(theta @ alpha.T - beta[None, :])
    return rng.binomial(1, p).astype(float)


def gen_non_compensatory_mirt(rng: np.random.Generator,
                              n_agents: int, n_tasks: int, d: int,
                              ability_scale: float = 1.0,
                              difficulty_scale: float = 1.0) -> np.ndarray:
    """Non-compensatory MIRT. P(success) = ∏_k σ(θ_{i,k} - β_{j,k}).

    Every demanded skill must independently clear its bar (no substitution).
    Plausibly closer to multi-step agent benchmarks where any required
    sub-capability failing collapses the task.
    """
    theta = rng.normal(0, ability_scale, (n_agents, d))
    beta  = rng.normal(0, difficulty_scale, (n_tasks, d))
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        p = np.prod(expit(theta[:, None, :] - beta[None, :, :]), axis=2)
    return rng.binomial(1, p).astype(float)


# === Gate 0 pipeline (vectorized) ===

def gate0_stats(score_matrix: np.ndarray) -> dict | None:
    """Apply the Gate 0 pipeline to a synthetic score matrix.

    Returns None if too few qualifying margin-band tasks.

    Vectorized: builds pairwise effect arrays via per-agent task means
    rather than the O(n_agents² × n_tasks) Python loop in the original
    Gate 0 script. Faithful to the same statistic; necessary for the
    larger MMLU-Pro shape.
    """
    n_agents, _ = score_matrix.shape

    difficulty = score_matrix.mean(axis=0)
    margin_mask = (difficulty >= MARGIN_LO) & (difficulty <= MARGIN_HI)
    n_margin = int(margin_mask.sum())
    if n_margin < MIN_MARGIN_TASKS:
        return None

    full_means   = score_matrix.mean(axis=1)
    margin_means = score_matrix[:, margin_mask].mean(axis=1)

    iu = np.triu_indices(n_agents, k=1)
    effect_full   = full_means[iu[0]]   - full_means[iu[1]]
    effect_margin = margin_means[iu[0]] - margin_means[iu[1]]

    delta = np.abs(effect_margin - effect_full)
    sign_flip = np.sign(effect_full) != np.sign(effect_margin)
    rho = fast_spearman(effect_full, effect_margin)

    return dict(
        n_pairs=int(len(effect_full)),
        n_margin_tasks=n_margin,
        in_band_fraction=float(margin_mask.mean()),
        median_abs_delta=float(np.median(delta)),
        p95_abs_delta=float(np.percentile(delta, 95)),
        sign_flip_rate=float(sign_flip.mean()),
        spearman_rho=rho,
    )


# === Sweep ===

def _sweep_cell(rng, model_name, source_name, n_sims, *, d=None, **kwargs):
    src = SOURCES[source_name]
    rows: list[dict] = []
    for _ in range(n_sims):
        if model_name == "rasch":
            sm = gen_rasch(rng, src["n_agents"], src["n_tasks"], **kwargs)
        elif model_name == "compensatory-mirt":
            sm = gen_compensatory_mirt(rng, src["n_agents"], src["n_tasks"], d, **kwargs)
        elif model_name == "non-compensatory-mirt":
            sm = gen_non_compensatory_mirt(rng, src["n_agents"], src["n_tasks"], d, **kwargs)
        else:
            raise ValueError(f"unknown model: {model_name}")
        s = gate0_stats(sm)
        if s is None:
            continue
        s["source"] = source_name
        s["model"] = model_name
        s["d"] = d if d is not None else 1
        s.update(kwargs)
        rows.append(s)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sims", type=int, default=100,
                        help="Replications per cell. Use 500+ for OSF-quality MDE quantiles.")
    parser.add_argument("--out-dir", type=Path, default=Path("simulation-results"))
    args = parser.parse_args()
    args.out_dir.mkdir(exist_ok=True)

    rng = np.random.default_rng(SEED)
    all_rows: list[dict] = []

    for source_name in SOURCES:
        print(f"[{source_name}] n_agents={SOURCES[source_name]['n_agents']} n_tasks={SOURCES[source_name]['n_tasks']}")

        print("  rasch (null) ...")
        for ab in ABILITY_SCALES:
            for dif in DIFFICULTY_SCALES:
                all_rows.extend(_sweep_cell(rng, "rasch", source_name, args.n_sims,
                                            ability_scale=ab, difficulty_scale=dif))

        for d in MIRT_DIMS:
            print(f"  compensatory-mirt d={d} ...")
            for ab in ABILITY_SCALES:
                for dif in DIFFICULTY_SCALES:
                    all_rows.extend(_sweep_cell(rng, "compensatory-mirt", source_name, args.n_sims,
                                                d=d, ability_scale=ab, difficulty_scale=dif))

        for d in MIRT_DIMS:
            print(f"  non-compensatory-mirt d={d} ...")
            for ab in ABILITY_SCALES:
                for dif in DIFFICULTY_SCALES:
                    all_rows.extend(_sweep_cell(rng, "non-compensatory-mirt", source_name, args.n_sims,
                                                d=d, ability_scale=ab, difficulty_scale=dif))

    df = pd.DataFrame(all_rows)
    raw_path = args.out_dir / "simulation-results.csv"
    df.to_csv(raw_path, index=False)
    print(f"\nWrote {raw_path} ({len(df):,} rows)")

    # === Summary ===
    summary = (
        df.groupby(["source", "model", "d", "ability_scale", "difficulty_scale"], dropna=False)
        .agg(
            median_of_median_abs_delta=("median_abs_delta", "median"),
            p2_5=("median_abs_delta", lambda x: float(np.percentile(x, 2.5))),
            p97_5=("median_abs_delta", lambda x: float(np.percentile(x, 97.5))),
            mean_sign_flip=("sign_flip_rate", "mean"),
            mean_rho=("spearman_rho", "mean"),
            mean_in_band=("in_band_fraction", "mean"),
            n=("median_abs_delta", "count"),
        )
        .reset_index()
    )
    summary_path = args.out_dir / "simulation-summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"Wrote {summary_path}")

    # === Theoretical-anchor lookup ===
    # Which (model, params) reproduce observed Gate 0 median |Δ| ≈ 0.090?
    target = 0.090
    anchor_candidates = (
        summary[summary.model != "rasch"]
        .assign(distance=lambda x: (x.median_of_median_abs_delta - target).abs())
        .sort_values(["source", "distance"])
        .groupby("source")
        .head(3)
        [["source", "model", "d", "ability_scale", "difficulty_scale",
          "median_of_median_abs_delta", "p2_5", "p97_5", "distance"]]
    )
    anchor_path = args.out_dir / "theoretical-anchor-candidates.csv"
    anchor_candidates.to_csv(anchor_path, index=False)
    print(f"Wrote {anchor_path}")
    print("\n=== Top-3 theoretical-anchor candidates (closest to Gate 0's 0.090) ===")
    print(anchor_candidates.to_string(index=False))

    # === Power analysis ===
    # H0 critical value per source = (1 - α) quantile of Rasch median |Δ|.
    h0_critical = (
        df[df.model == "rasch"]
        .groupby("source")["median_abs_delta"]
        .quantile(1 - ALPHA_LEVEL)
        .reset_index()
        .rename(columns={"median_abs_delta": "h0_critical"})
    )
    print(f"\n=== H0 (Rasch) critical values at α={ALPHA_LEVEL} ===")
    print(h0_critical.to_string(index=False))

    df_with_h0 = df.merge(h0_critical, on="source")
    df_with_h0["exceeds_h0"] = df_with_h0["median_abs_delta"] > df_with_h0["h0_critical"]
    power_table = (
        df_with_h0[df_with_h0.model != "rasch"]
        .groupby(["source", "model", "d", "ability_scale", "difficulty_scale"], dropna=False)["exceeds_h0"]
        .mean()
        .reset_index()
        .rename(columns={"exceeds_h0": "power"})
    )
    power_path = args.out_dir / "power-table.csv"
    power_table.to_csv(power_path, index=False)
    print(f"Wrote {power_path}")

    # === MDE table for OSF pre-registration ===
    # For each (source, MIRT model, d): smallest combined signal achieving power ≥ 0.8.
    # "Combined signal" = ability_scale × difficulty_scale (rough heuristic for ordering).
    mde_rows: list[dict] = []
    for (src, model, d), grp in power_table.groupby(["source", "model", "d"], dropna=False):
        clearing = grp[grp.power >= POWER_TARGET].copy()
        if clearing.empty:
            mde_rows.append(dict(
                source=src, model=model, d=d,
                mde_achieved=False,
                best_power=float(grp.power.max()),
                best_ability_scale=float(grp.sort_values("power").iloc[-1].ability_scale),
                best_difficulty_scale=float(grp.sort_values("power").iloc[-1].difficulty_scale),
            ))
        else:
            clearing["combined"] = clearing.ability_scale * clearing.difficulty_scale
            best = clearing.sort_values("combined").iloc[0]
            mde_rows.append(dict(
                source=src, model=model, d=d,
                mde_achieved=True,
                mde_ability_scale=float(best.ability_scale),
                mde_difficulty_scale=float(best.difficulty_scale),
                mde_combined=float(best.combined),
                power_at_mde=float(best.power),
            ))
    mde_table = pd.DataFrame(mde_rows)
    mde_path = args.out_dir / "mde-table.csv"
    mde_table.to_csv(mde_path, index=False)
    print(f"\nWrote {mde_path}")
    print("\n=== MDE summary ===")
    print(mde_table.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
