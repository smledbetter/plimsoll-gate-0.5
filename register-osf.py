"""Submit Plimsoll Gate 0.5 to OSF as a Pre-Data Collection Registration.

Workflow:
  1. POST /v2/nodes/                              — create OSF project (public)
  2. PUT  files.osf.io/v1/resources/.../          — upload supplementary files
  3. POST /v2/nodes/{id}/draft_registrations/     — create draft tied to schema
  4. PATCH /v2/draft_registrations/{id}/          — fill registration_responses
  5. POST /v2/registrations/                      — finalize (irreversible)

By default --dry-run prints the payload + file list and exits without touching
the API. --skip-finalize runs steps 1-4 but stops before the irreversible
step 5; the draft will appear in the user's OSF account for manual review.

Auth: PAT from osf.io/settings/tokens with osf.full_write scope.

Usage:
  python register-osf.py --dry-run
  python register-osf.py --token $OSF_TOKEN --skip-finalize
  python register-osf.py --token $OSF_TOKEN          # full submission

Reproducibility:
  Frozen at git commit SHA. The RESPONSES dict below is the source of truth
  for what gets registered. Edit there, not in OSF's web UI.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

API_BASE = "https://api.osf.io/v2"
WB_BASE = "https://files.osf.io/v1"
SCHEMA_ID = "697b72f611a8e98484c6139b"  # OSF Preregistration v4
JSON_API = "application/vnd.api+json"

PROJECT_TITLE = "Plimsoll Gate 0.5: Capability-margin effect-size stability — three-source replication"
PROJECT_DESCRIPTION = (
    "Plimsoll Gate 0.5 — prospective replication of capability-margin "
    "effect-size instability on three independent held-out sources "
    "(full SWE-bench Verified, LiveCodeBench, MMLU-Pro). Tests whether the "
    "Gate 0 finding (rank stability ≠ paired effect-size stability under "
    "[0.30, 0.70] capability-margin filtering) generalizes beyond Ndzomga "
    "2026's heatmap. Plimsoll protocol elements 3 (pre-registration) and 5 "
    "(power analysis) satisfied prospectively."
)

# Files relative to the script's working directory (default: cwd).
#
# IMPORTANT: simulation-results/ should contain the authoritative n=1000
# registered-run outputs (from the VPS) before this script is run for the
# actual submission. The smoke-run (n=100) outputs are noise-floor for tail
# quantiles and should not be the published artifact. scp from VPS:
#
#   scp -i ~/.ssh/claude-dev-droplet -r \
#     dev@100.87.64.104:~/projects/plimsoll-gate0.5/simulation-results/ \
#     <gate-0.5-dir>/simulation-results/
#
# Skip: osf-automation-research.md — meta (about OSF, not Plimsoll science).
ATTACH_FILES = [
    "README.md",
    "pre-registration.md",
    "inventory.md",
    "simulation.py",
    "prep-swebench.py",
    "prep-livecodebench.py",
    "prep-mmlu-pro.py",
    "simulation-results/simulation-results.csv",
    "simulation-results/simulation-summary.csv",
    "simulation-results/mde-table.csv",
    "simulation-results/power-table.csv",
    "simulation-results/theoretical-anchor-candidates.csv",
    "inventory-supplement/nl2sql.md",
    "inventory-supplement/math-reasoning.md",
    "inventory-supplement/code-non-swe.md",
    "inventory-supplement/agent-uncertain.md",
]

# Canonical OSF Preregistration v4 select-option strings (verified against the
# live schema 2026-04-26). Storing them as constants here so accidental drift
# from the OSF source is detectable at runtime.
OPT_FOREKNOWLEDGE_OBSERVED_NO_ANALYSES = (
    "Authors have observed the data, but have not performed the proposed "
    "analyses. At least some of the data that will be used for this analysis "
    "plan has been accessed and observed by the authors. The authors have "
    "sufficiently observed relevant evidence to influence their analysis "
    "decisions or conclusions. However, the authors have not yet performed "
    "any of the proposed analyses in this plan and will not do so until "
    "after this plan is registered."
)

OPT_STUDY_NON_RANDOMIZED = (
    "Non-randomized study: Does not include random assignment of subjects to "
    "treatments or conditions. This usually includes correlational studies, "
    "observational studies, surveys, natural experiments, real-world "
    "evidence studies, regression discontinuity designs, and descriptive "
    "studies."
)

OPT_CAUSAL_NONE = (
    "No causal relationship inferred: This study is not intended to inform a "
    "causal relationship. "
)

OPT_BLINDING_NONE = "No blinding is involved."


RESPONSES: dict[str, object] = {
    # ============================================================
    # Overview
    # ============================================================
    "344-2": (
        # Research questions or hypotheses
        "**Hypotheses (per source X ∈ {SWE-bench Verified, LiveCodeBench, "
        "MMLU-Pro}):**\n\n"
        "- **H1(X)** (primary, directional). The median absolute paired "
        "effect-size shift |Δ| between full-task computation and capability-"
        "margin ([0.30, 0.70]) computation on source X exceeds the median "
        "|Δ| produced by a within-pair condition-label permutation null at "
        "p < 0.001 (one-sided, observed ≥ null).\n\n"
        "- **H2(X)** (descriptive). Spearman ρ(effect_full, effect_margin) "
        "≥ 0.85, replicating the rank-stability finding of Ndzomga 2026.\n\n"
        "- **H3(X)** (descriptive). Sign-flip rate (sign(effect_full) ≠ "
        "sign(effect_margin)) exceeds 5%.\n\n"
        "**Per-source clearance.** Source X clears Gate 0.5 iff median |Δ| "
        "≥ 0.05 AND null-baseline z ≥ 3 (P(null ≥ obs) ≤ ~0.001). Otherwise "
        "X fails.\n\n"
        "**Layered verdict combining sources:**\n\n"
        "- All three clear → maximum-scope claim (agentic code + competitive "
        "programming + multi-discipline knowledge).\n"
        "- SWE-bench + LiveCodeBench clear, MMLU-Pro fails → code-eval-scope "
        "claim with MMLU-Pro reported as honest non-replication.\n"
        "- SWE-bench clears alone → single-source prospective replication of "
        "Gate 0; both secondary non-replications discussed as future work.\n"
        "- SWE-bench fails → Gate 0.5 fails; Plimsoll methodology paper does "
        "not ship as currently framed.\n\n"
        "Per-source statistics and per-benchmark texture are reported in all "
        "outcome paths. Background context: see attached pre-registration.md "
        "§1, Plimsoll README, and inventory.md."
    ),

    "344-4": OPT_FOREKNOWLEDGE_OBSERVED_NO_ANALYSES,

    "344-14": (
        # Explanation of foreknowledge and managing unintended influences
        "Asymmetric foreknowledge across the three registered sources, "
        "disclosed in detail:\n\n"
        "**SWE-bench Verified (primary).** The analyst has prior contact via "
        "Ndzomga 2026 (arXiv:2603.23749), who aggregated a 50-instance × "
        "28-agent subset (`swebench_verified_mini`) into a public 22K-row "
        "heatmap. That subset constitutes 1,400 of the 67,000 cells (~2.1%) "
        "of the registered cell space (500 instances × 134 agents). Plimsoll "
        "Gate 0 — a different exploratory analysis — was performed on the "
        "seen 2.1%. Gate 0's observed median |Δ paired effect size| = 0.090 "
        "informed the threshold of 0.05 in this pre-registration's decision "
        "rule. The proposed Gate 0.5 analyses on the held-out cell space "
        "(450 instances × 134 agents minus the seen 1,400 cells, ~98% of "
        "the registered space) have not been performed.\n\n"
        "**LiveCodeBench (confirmatory secondary, code domain).** Wholly "
        "unseen. The analyst has not accessed `LiveCodeBench/submissions` "
        "per-question pass/fail data per submission.\n\n"
        "**MMLU-Pro (confirmatory secondary, scope).** Wholly unseen. The "
        "analyst has not accessed `TIGER-AI-Lab/MMLU-Pro/eval_results` "
        "per-question pred/answer data per model.\n\n"
        "**Mitigation of unintended influences.** The analysis plan, "
        "decision rule thresholds, and per-source preprocessing rules are "
        "frozen in this registration before any held-out data is pulled. The "
        "analysis pipeline (`analyze.py`, `null-baseline.py`, `prep-*.py`) "
        "is also frozen at the registration commit SHA. The simulation "
        "(`simulation.py`) is a methodological prerequisite that "
        "characterises the pipeline's properties on synthetic data; its "
        "results inform the power statement below but do not bias the "
        "held-out analysis. Sensitivity checks are pre-specified as "
        "described in §4.2 of the attached pre-registration.md and exposed "
        "as command-line flags on `prep-swebench.py` (`--exclude-no-logs`) "
        "and `prep-livecodebench.py` (`--any-pass`, `--no-dedup`)."
    ),

    # ============================================================
    # Research Design
    # ============================================================
    "344-17": [OPT_STUDY_NON_RANDOMIZED],

    "344-27": [OPT_CAUSAL_NONE],

    "344-32": [OPT_BLINDING_NONE],

    "344-38": (
        # Additional blinding during research or analysis
        "Not applicable. This is a re-analysis of public leaderboard data; "
        "there are no human or animal subjects, no experimental conditions "
        "to assign, and no manipulation. Outcome data (pass/fail per "
        "(agent/model, task) cell) was generated by the original benchmark "
        "evaluations, not by the analyst."
    ),

    "344-40": (
        # Study design
        "Re-analysis of three independent public per-instance leaderboard "
        "datasets, executed under a single frozen analysis pipeline. The "
        "design is paired-comparison-within-source: for every unordered "
        "agent/model pair within a source, compute paired effect size on "
        "(a) the full task set and (b) the subset filtered to mean-pass-"
        "rate-difficulty ∈ [0.30, 0.70] (the capability-margin band). "
        "Compare distributions.\n\n"
        "**Sources (all three pre-committed in inventory.md and "
        "inventory-supplement/):**\n\n"
        "1. *Primary — Full SWE-bench Verified* via `swe-bench/experiments` "
        "(134 submissions × 500 SWE-bench Verified instances).\n"
        "2. *Confirmatory secondary (code domain) — LiveCodeBench* via "
        "`LiveCodeBench/submissions` (≥50 distinct model families after "
        "canonical dedup × 1055 questions across Codeforces / LeetCode / "
        "AtCoder).\n"
        "3. *Confirmatory secondary (scope) — MMLU-Pro* via "
        "`TIGER-AI-Lab/MMLU-Pro/eval_results` (48 model-output ZIPs × "
        "12,032 questions across 14 disciplines).\n\n"
        "**Pipeline.** Single `analyze.py` and `null-baseline.py` "
        "parametrized over data source. The analysis is identical across "
        "sources at the statistic level; per-source preprocessing rules are "
        "pre-committed in §4.2 of the attached pre-registration.md.\n\n"
        "**Layered decision rule.** Per-source clearance (median |Δ| ≥ 0.05 "
        "AND null-baseline z ≥ 3 at α = 0.001) combined into a four-row "
        "outcome table (see 344-2 above). SWE-bench primary failure is a "
        "hard kill; secondary failures are reported honestly and shape the "
        "scope of the headline claim without killing the gate.\n\n"
        "Detailed pipeline + design rationale: see attached "
        "pre-registration.md §1, §4 and gate-0.5/README.md."
    ),

    "344-42": [],  # Study design - file upload (handled via project file attach)

    "344-44": (
        # Randomization
        "Not applicable. This is a re-analysis design; agents/models are not "
        "assigned to conditions and tasks are not assigned to agents. The "
        "(agent/model, task) cells in each source's score matrix are "
        "fixed by the original benchmark evaluations as published. Within "
        "the analysis pipeline, the null-baseline permutation procedure does "
        "perform per-cell label-swap randomization under H0; that procedure "
        "is a frozen part of `null-baseline.py` (1000 permutations, fixed "
        "seed) and is described in 344-71 below."
    ),

    # ============================================================
    # Sampling
    # ============================================================
    "344-47": (
        # Data collection procedures
        "Data is not collected by the analyst; it is pulled from three "
        "public repositories at the registration's frozen commit SHAs. "
        "Re-analysis of public leaderboard pass/fail outcomes does not "
        "require explicit re-licensing — the data are facts about public "
        "model behaviour (Feist v. Rural Telephone Service, 1991) and the "
        "source repositories are either explicitly published with "
        "reproducibility intent (SWE-bench experiments) or under permissive "
        "licenses (LiveCodeBench MIT; MMLU-Pro Apache + MIT).\n\n"
        "**Source 1 — SWE-bench Verified.** Repository: "
        "`https://github.com/swe-bench/experiments`. Layout: "
        "`evaluation/verified/<submission>/results/results.json`, with "
        "`resolved`, `no_generation`, and `no_logs` instance-ID lists per "
        "submission. Task universe: canonical SWE-bench Verified 500-"
        "instance list (`princeton-nlp/SWE-bench_Verified` on HuggingFace).\n\n"
        "**Source 2 — LiveCodeBench.** Repository: "
        "`https://github.com/LiveCodeBench/submissions`. Layout: "
        "`<model_variant>/Scenario.codegeneration_*_eval_all.json`, with "
        "`graded_list[bool]` per question.\n\n"
        "**Source 3 — MMLU-Pro.** Repository: "
        "`https://github.com/TIGER-AI-Lab/MMLU-Pro`. Layout: "
        "`eval_results/<model>.zip`, with per-discipline JSON containing "
        "per-question records (`pred`, `answer`, `category`).\n\n"
        "Per-source preprocessing scripts (`prep-swebench.py`, "
        "`prep-livecodebench.py`, `prep-mmlu-pro.py`) attached to this "
        "project produce normalised (agent, task, success) triples on a "
        "common CSV schema. Frozen commit SHAs for all three source repos "
        "and for the preprocessing scripts are pinned at registration time."
    ),

    "344-49": [],

    "344-51": (
        # Sample size
        "**Source 1 — SWE-bench Verified:** up to 134 submissions × 500 "
        "instances = up to 67,000 (agent, task) cells; up to C(134, 2) = "
        "8,911 unordered candidate agent pairs before applying the per-pair "
        "inclusion thresholds (≥20 shared full tasks, ≥8 shared margin-band "
        "tasks).\n\n"
        "**Source 2 — LiveCodeBench:** ≥50 distinct model families × 1,055 "
        "questions = ≥52,750 cells (after canonical variant dedup); up to "
        "C(50, 2) = 1,225 unordered candidate pairs before threshold "
        "filtering.\n\n"
        "**Source 3 — MMLU-Pro:** 48 models × 12,032 questions = 577,536 "
        "cells; up to C(48, 2) = 1,128 unordered candidate pairs before "
        "threshold filtering.\n\n"
        "Sample sizes are inherited from the public leaderboards and are "
        "fixed at the registration's frozen commit SHAs; submissions "
        "added to the source repositories after the registration timestamp "
        "are excluded from the analysis by frozen-list intersection. "
        "Post-threshold pair counts will be reported per source in the "
        "results."
    ),

    "344-53": (
        # Sample size rationale
        "Sample sizes are not chosen — they are inherited from the three "
        "public leaderboards at frozen commit SHAs. The methodologically "
        "load-bearing question is whether the inherited sample is "
        "sufficient to detect the median |Δ| ≥ 0.05 effect that the "
        "decision rule requires. Component A's frozen simulation "
        "(`simulation.py`, seed 20260426) characterises the pipeline's "
        "power on the actual source shapes (134×500, 50×1055, 48×12,032) "
        "under three generative families (Rasch / 1PL IRT, compensatory "
        "MIRT at d ∈ {2, 3, 5}, non-compensatory MIRT at d ∈ {2, 3, 5}). "
        "The MDE (smallest signal-strength parameter combination achieving "
        "≥80% power against the Rasch null at α = 0.001) is reported per "
        "(source, generative family, dimensionality) in attached "
        "`simulation-results/mde-table.csv`. See 344-71 below for the "
        "asymmetric power finding (non-compensatory MIRT achieves power "
        "across all three sources; compensatory MIRT does not in any "
        "swept-grid cell, which is itself a pre-registered theoretical "
        "claim)."
    ),

    "344-55": (
        # Starting and stopping rules
        "Single-shot analysis. No interim looks, sequential testing, or "
        "early-stopping. The analysis runs once per source against the "
        "frozen analysis scripts at the registration commit SHA, on the "
        "data pulled from the source repositories at their respective "
        "frozen commit SHAs. Results are reported in their entirety — there "
        "is no selection between multiple analyses or model variants after "
        "data access. The registration commit SHA and three source commit "
        "SHAs serve as the audit anchor: any submission added to the source "
        "repositories after the registration timestamp is excluded from the "
        "analysis."
    ),

    # ============================================================
    # Variables
    # ============================================================
    "344-58": (
        # Manipulated variables
        "Independent variable (within-pair, within-source): **task-selection "
        "regime**, with two levels — `full` and `margin`.\n\n"
        "- `full`: all qualifying tasks for which both agents/models in the "
        "pair have scores (subject to the ≥20 shared-tasks inclusion "
        "threshold).\n"
        "- `margin`: subset where mean-pass-rate difficulty is in the "
        "[0.30, 0.70] capability-margin band (subject to the ≥8 shared-"
        "margin-band-tasks inclusion threshold).\n\n"
        "Difficulty is operationalised per source as `mean(success)` across "
        "all agents/models that attempted the task. The same band is applied "
        "uniformly across all three sources for the primary analysis; "
        "per-source band tuning is a sensitivity check, not the primary "
        "test."
    ),

    "344-60": [],

    "344-62": (
        # Measured variables
        "Dependent variable: **paired effect size**, defined as the mean of "
        "per-task score differences between agents/models A and B over the "
        "qualifying task set:\n\n"
        "    effect = mean(score_A[t] − score_B[t]) for t ∈ qualifying tasks.\n\n"
        "This is a mean-difference effect size, not Cohen's h or d. The "
        "score domain is {0, 1} for all three sources:\n\n"
        "- SWE-bench Verified: 1 if `instance_id ∈ resolved`, else 0 (with "
        "`no_logs` treated as 0 by the pre-registered conservative rule).\n"
        "- LiveCodeBench: `graded_list[0]` (first-attempt pass@1, primary "
        "rule); `any(graded_list)` is a pre-registered sensitivity check.\n"
        "- MMLU-Pro: 1 if `pred == answer` (whitespace-trimmed string "
        "comparison), else 0.\n\n"
        "Each pair contributes two effect-size measurements: `effect_full` "
        "and `effect_margin`. The primary analytic quantity per pair is "
        "Δ = effect_margin − effect_full."
    ),

    "344-64": [],

    "344-66": (
        # Indices
        "Per-source headline statistics computed from the (agent, task, "
        "success) triple matrix and the per-pair effect-size pairs:\n\n"
        "1. **Spearman ρ(effect_full, effect_margin)** — rank-stability "
        "diagnostic. Replicates Ndzomga 2026's claim if ≥ 0.85.\n"
        "2. **Pearson r(effect_full, effect_margin)** — magnitude "
        "diagnostic.\n"
        "3. **Distribution of |Δ|** = |effect_margin − effect_full|: "
        "median, p75, p95, max.\n"
        "4. **Sign-flip rate**: P(sign(effect_full) ≠ sign(effect_margin)).\n"
        "5. **Per-benchmark / per-discipline texture** where coverage "
        "permits (LiveCodeBench: codeforces / leetcode / atcoder; "
        "MMLU-Pro: 14 disciplines).\n\n"
        "**Test statistic for H1 (per source):** median |Δ| across "
        "qualifying pairs, compared to a within-pair label-swap permutation "
        "null distribution. Z-score = (observed median |Δ| − null mean) / "
        "null std; tail probability P(null ≥ observed) reported.\n\n"
        "**Bootstrap CIs:** 95% percentile-method CIs on Spearman ρ and "
        "sign-flip rate (10,000 resamples over pairs). Descriptive only, "
        "not gated."
    ),

    "344-68": [],

    # ============================================================
    # Analysis Plan
    # ============================================================
    "344-71": (
        # Statistical models
        "**Frozen analysis pipeline.** A single `analyze.py` and "
        "`null-baseline.py` parametrized over data source, attached to this "
        "project at the registration's frozen commit SHA. Identical "
        "statistic, identical inclusion thresholds, identical decision rule "
        "across all three sources. Per-source preprocessing rules (which "
        "differ slightly because the source data formats differ) are "
        "pre-committed in §4.2 of the attached pre-registration.md and "
        "exposed as flags on the `prep-*.py` scripts.\n\n"
        "**Inclusion thresholds (per pair):** ≥20 shared tasks for `full`; "
        "≥8 shared margin-band tasks for `margin`. Pairs failing either "
        "threshold are dropped. Identical to Plimsoll Gate 0.\n\n"
        "**Null-baseline permutation test (H1).** For each source, generate "
        "1,000 within-pair condition-label permutations under H0 (agents A "
        "and B are exchangeable on each task; per-cell labels swapped with "
        "probability 0.5 per pair per task). For each permutation, recompute "
        "the median |Δ| across qualifying pairs. The observed median |Δ| is "
        "compared to the resulting null distribution: z = (observed − null "
        "mean) / null std; P(null ≥ obs) computed empirically. Random seed "
        "fixed in `null-baseline.py`.\n\n"
        "**Power analysis (Component A).** The simulation `simulation.py` "
        "(seed 20260426; n=1000 replications per cell) generates synthetic "
        "(agent, task) score matrices at the actual source shapes under "
        "three generative families:\n\n"
        "- *Rasch / 1PL IRT*: P(success) = σ(θ_i − β_j). The null model.\n"
        "- *Compensatory MIRT* at d ∈ {2, 3, 5}: P(success) = σ(θ_i · α_j − "
        "β_j). Skills can substitute.\n"
        "- *Non-compensatory MIRT* at d ∈ {2, 3, 5}: P(success) = ∏_k "
        "σ(θ_{i,k} − β_{j,k}). Every demanded sub-capability must "
        "independently clear its bar.\n\n"
        "Per-source α=0.001 critical values from the Rasch null distribution "
        "are computed first; per (source, MIRT model, parameters) cell, "
        "power = P(simulated median |Δ| > Rasch critical value). The MDE — "
        "smallest signal-strength parameter combination achieving ≥80% "
        "power — is reported per (source, generative family, dimensionality) "
        "in attached `simulation-results/mde-table.csv`.\n\n"
        "**Asymmetric power finding (pre-registered).** The n=1000 "
        "registered-run results (frozen in `simulation-results/mde-table.csv` "
        "and `simulation-results/power-table.csv`) show non-compensatory MIRT "
        "achieves ≥80% power against the Rasch null at α=0.001 across all "
        "three sources at moderate signal levels (SWE-bench non-comp d=2 MDE "
        "at ability=1.5/difficulty=2.0, power 0.877; LiveCodeBench non-comp "
        "d=2 at ability=2.0/difficulty=2.0, power 0.919; MMLU-Pro non-comp "
        "d=2 at ability=2.0/difficulty=2.0, power 0.937; all higher-d cells "
        "achieve power ≥0.842 at smaller signal scales). Compensatory MIRT "
        "achieves 0.000 power in every cell of the swept parameter grid "
        "(ability_scale × difficulty_scale ∈ {0.5, 1.0, 1.5, 2.0}²; 16 cells "
        "× 3 dimensionalities × 3 sources = 144 cells, all 0.000 at n=1000). "
        "This is itself a pre-registered theoretical claim: capability-margin "
        "filtering does not produce paired-effect-size instability under "
        "skill-substitutable models. The observed Gate 0 instability is "
        "therefore a signature of non-compensatory multidimensional skill "
        "structure, not of multidimensionality per se. The full MDE table is "
        "attached as `simulation-results/mde-table.csv`; the theoretical "
        "anchor candidates closest to Gate 0's observed median |Δ| = 0.090 "
        "are exclusively non-compensatory MIRT cells, attached as "
        "`simulation-results/theoretical-anchor-candidates.csv`."
    ),

    "344-73": [],

    "344-75": (
        # Transformations
        "No transformations beyond the per-source preprocessing rules in "
        "344-79. Score outcomes are converted to the {0, 1} domain at "
        "preprocessing time per the source's native scoring (boolean for "
        "SWE-bench `resolved`, `graded_list[0]` for LiveCodeBench, "
        "string-equality `pred == answer` for MMLU-Pro). Effect sizes are "
        "reported on the pass-rate difference scale (∈ [-1, +1]); no "
        "logit, arcsine, or rank transforms are applied to the headline "
        "statistic. Rank transforms are used internally inside Spearman ρ "
        "and the rank correlation in `analyze.py`."
    ),

    "344-77": (
        # Inference criteria
        "**Per-source clearance criterion (identical across all three):** "
        "Source X clears Gate 0.5 iff median |Δ| ≥ 0.05 AND null-baseline "
        "z ≥ 3 (P(null ≥ obs) ≤ ~0.001, one-sided, observed ≥ null). "
        "Otherwise X fails.\n\n"
        "**Layered Gate 0.5 verdict (combination rule across sources):**\n\n"
        "| Outcome path | Plimsoll verdict |\n"
        "|---|---|\n"
        "| All three clear | Gate 0.5 clears with maximum scope (agentic "
        "code + competitive programming + multi-discipline knowledge). |\n"
        "| SWE-bench + LiveCodeBench clear; MMLU-Pro fails | Gate 0.5 "
        "clears with code-eval scope; MMLU-Pro reported as honest "
        "non-replication and discussed as future work. |\n"
        "| SWE-bench clears alone | Gate 0.5 clears as single-source "
        "prospective replication of Gate 0; both secondary non-replications "
        "discussed as future work. |\n"
        "| SWE-bench fails | Gate 0.5 fails. Plimsoll methodology paper "
        "does not ship as currently framed. |\n\n"
        "**No multiple-comparisons correction** is applied to the three H1 "
        "tests. The asymmetric layered rule already encodes the differential "
        "weighting across sources, and applying family-wise correction on "
        "top would conflate the rule's design with a separate inferential "
        "question. Per-benchmark / per-discipline statistics are descriptive "
        "and not gated."
    ),

    "344-79": (
        # Data inclusion and exclusion
        "**Per-pair inclusion thresholds (apply to all three sources):** "
        "≥20 shared full tasks; ≥8 shared margin-band tasks. Pairs failing "
        "either threshold are dropped from the analysis. Identical to "
        "Plimsoll Gate 0.\n\n"
        "**Per-source preprocessing (pre-committed):**\n\n"
        "*SWE-bench Verified (`prep-swebench.py`):* `no_logs` instance IDs "
        "treated as failure (matches public leaderboard scoring; "
        "conservative). Sensitivity check: re-run with `--exclude-no-logs` "
        "and report both. All 134 submissions treated as 134 distinct "
        "agents — no dedup by scaffold-and-model. Submissions missing an "
        "instance ID are treated as failure on that instance.\n\n"
        "*LiveCodeBench (`prep-livecodebench.py`):* Pass/fail = "
        "`graded_list[0]` (first-attempt pass@1). Sensitivity check: "
        "any-pass via `--any-pass`. Variants per model family deduplicated "
        "to one canonical variant per family — the latest-mtime directory "
        "under common variant suffixes (`_thinking`, `_temp\\d+`, "
        "`_seed\\d+`, `_v\\d+`). Override available via `--no-dedup`. Tasks "
        "identified by `(platform, contest_id, question_id)` tuple to avoid "
        "cross-platform ID collision.\n\n"
        "*MMLU-Pro (`prep-mmlu-pro.py`):* Pass/fail = `pred == answer` with "
        "whitespace-trimmed string comparison. Pooled across 14 disciplines "
        "as the primary analysis; per-discipline texture preserved in "
        "`benchmark_name` for supplementary analysis. No model dedup (each "
        "ZIP corresponds to one model). Records missing `pred` or `answer` "
        "are skipped (treated as no-attempt rather than failure).\n\n"
        "**Source-level exclusions (pre-committed):** Submissions added to "
        "any source repository after the registration's frozen commit SHA "
        "are excluded by frozen-list intersection."
    ),

    "344-81": (
        # Missing data
        "No imputation. Missing-data handling is per-pair: a pair is "
        "dropped from a source's analysis if it fails the inclusion "
        "thresholds in 344-79. Per-source missing-data fractions (count of "
        "candidate pairs dropped, with reason: full-threshold failure, "
        "margin-threshold failure, or both) will be reported alongside the "
        "headline statistics.\n\n"
        "Within an included pair, per-task missing values (cells where one "
        "or both agents/models lack a score on a given task) are dropped "
        "from the mean-difference computation for that pair-task; only the "
        "intersection of tasks-with-scores-from-both-agents contributes to "
        "the paired effect size."
    ),

    "344-83": (
        # Other planned analysis
        "**Pre-committed sensitivity analyses (not gated):**\n\n"
        "1. *SWE-bench `no_logs` handling.* Re-run with `--exclude-no-logs` "
        "to drop ambiguous execution-failure cells; compare to the primary "
        "treat-as-failure rule. Report both side-by-side.\n"
        "2. *LiveCodeBench attempt rule.* Re-run with `--any-pass` "
        "(`any(graded_list)` rather than `graded_list[0]`); compare.\n"
        "3. *LiveCodeBench dedup.* Re-run with `--no-dedup` to retain all "
        "73 raw submissions including thinking-on/off and temperature "
        "variants; compare to the canonical-only primary.\n"
        "4. *MMLU-Pro per-discipline.* Per-discipline median |Δ| and "
        "Spearman ρ for each of the 14 disciplines; texture statistic, "
        "not a gate.\n"
        "5. *Per-benchmark texture for LiveCodeBench.* Codeforces vs "
        "LeetCode vs AtCoder split; reports per-platform median |Δ| and "
        "in-band fraction.\n"
        "6. *Per-source [0.30, 0.70] band tuning.* Sensitivity check on "
        "the band edges; reports median |Δ| at [0.25, 0.75] and "
        "[0.40, 0.60]. The primary rule fixes [0.30, 0.70] uniformly per "
        "Ndzomga 2026.\n\n"
        "**Theoretical-anchor lookup from Component A.** "
        "`simulation-results/theoretical-anchor-candidates.csv` reports the "
        "top-3 (generative family, parameters) combinations whose simulated "
        "median |Δ| is closest to the Gate 0 observed 0.090, per source. "
        "This is descriptive (the simulation operates on synthetic data) "
        "but informs the methodology paper's discussion of which "
        "skill-structure assumption is most consistent with the observed "
        "instability."
    ),

    # ============================================================
    # Other
    # ============================================================
    "344-86": (
        # Context and additional information
        "**Project context.** This pre-registration is Plimsoll Gate 0.5, "
        "the prospective replication artifact in a methodology project on "
        "capability-margin discipline for agent-evaluation studies. "
        "Plimsoll Gate 0 (post-hoc re-analysis of Ndzomga 2026's heatmap, "
        "executed 2026-04-25) found rank stability ≠ paired effect-size "
        "stability under [0.30, 0.70] capability-margin filtering; Gate 0.5 "
        "tests whether that pattern generalises beyond the single-dataset "
        "anchor. The Gate 0 artifacts (analyse.py, null-baseline.py, "
        "results CSVs, scatter plot) are at the Plimsoll vault path "
        "`Projects/Research/Plimsoll/gate-0/` in the analyst's local "
        "Obsidian vault and are not attached here (Gate 0 was unregistered "
        "and is preserved as exploratory motivation, not Plimsoll-"
        "compliant).\n\n"
        "**Files attached to this OSF project.** The attached files "
        "constitute the frozen Component A simulation script and results, "
        "the three source preprocessing scripts, the inventory and "
        "supplemental cluster-fan-out documents that justified the source "
        "selection, the gate-0.5 README, and this pre-registration "
        "document. Together they comprise the methodologically load-"
        "bearing artifacts of Gate 0.5.\n\n"
        "**Connection to the broader Plimsoll project.** Plimsoll's "
        "contribution is the assembly of a six-element protocol for agent-"
        "mitigation studies — saturation profiling, capability-margin "
        "selection, pre-registration, paired-comparison design, power "
        "analysis with effect-size disclosure, and null-result discipline. "
        "Gate 0.5 satisfies elements 3 and 5 prospectively for the "
        "methodology paper's headline empirical claim. Element 5's "
        "operationalization for re-analyses (post-hoc effect-size "
        "disclosure with simulation-derived MDE) is a pre-committed "
        "protocol revision driven by working through Gate 0.5 itself.\n\n"
        "**Future work explicitly out of scope.** Re-analyses of specific "
        "published mitigation claims (Madaan 2023 Self-Refine, Du 2023 MAD) "
        "through the Plimsoll protocol are downstream of Gate 0.5 in the "
        "Plimsoll project's gate sequence and will be pre-registered "
        "separately. Application of Plimsoll to multi-step agent traces "
        "(rather than single-turn benchmark items) is a methodological "
        "extension also out of scope here.\n\n"
        "**Hard ship-or-kill date.** 2026-06-24 (60 days from the Plimsoll "
        "Study Gate verdict on 2026-04-25). If Gate 0.5 does not clear by "
        "that date, the methodology paper does not ship."
    ),
}

EXPECTED_KEYS = {
    "344-2", "344-4", "344-14", "344-17", "344-27", "344-32",
    "344-38", "344-40", "344-42", "344-44",
    "344-47", "344-49", "344-51", "344-53", "344-55",
    "344-58", "344-60", "344-62", "344-64", "344-66", "344-68",
    "344-71", "344-73", "344-75", "344-77", "344-79", "344-81", "344-83",
    "344-86",
}


# ===========================================================================
# Validation
# ===========================================================================

def validate_payload() -> list[str]:
    errors = []
    missing = EXPECTED_KEYS - RESPONSES.keys()
    if missing:
        errors.append(f"Missing keys: {sorted(missing)}")
    extra = RESPONSES.keys() - EXPECTED_KEYS
    if extra:
        errors.append(f"Unexpected keys: {sorted(extra)}")
    # Required text fields must be non-empty
    required_text = {
        "344-2", "344-14", "344-40", "344-44", "344-47",
        "344-51", "344-53", "344-55",
        "344-58", "344-62", "344-66",
        "344-71", "344-75", "344-77", "344-79", "344-81",
    }
    for k in required_text:
        v = RESPONSES.get(k, "")
        if not (isinstance(v, str) and v.strip()):
            errors.append(f"{k} must be non-empty string (got {type(v).__name__}: {repr(v)[:40]})")
    # Required select fields
    for k in ("344-17", "344-32"):
        v = RESPONSES.get(k, [])
        if not (isinstance(v, list) and v):
            errors.append(f"{k} multi-select must be non-empty list")
    if not (isinstance(RESPONSES.get("344-4"), str) and RESPONSES["344-4"].strip()):
        errors.append("344-4 single-select must be non-empty string")
    # File-input keys must be lists (we leave empty; files attached at project level)
    for k in ("344-42", "344-49", "344-60", "344-64", "344-68", "344-73"):
        v = RESPONSES.get(k)
        if not isinstance(v, list):
            errors.append(f"{k} file-input must be a list (got {type(v).__name__})")
    return errors


def validate_files(working_dir: Path) -> tuple[list[Path], list[str]]:
    found, missing = [], []
    for f in ATTACH_FILES:
        p = working_dir / f
        if p.exists() and p.is_file():
            found.append(p)
        else:
            missing.append(f)
    return found, missing


# ===========================================================================
# OSF API helpers
# ===========================================================================

def _hdrs(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": JSON_API}


def create_project(token: str, title: str, description: str, public: bool) -> str:
    payload = {
        "data": {
            "type": "nodes",
            "attributes": {
                "title": title,
                "description": description,
                "category": "project",
                "public": public,
            },
        }
    }
    r = requests.post(f"{API_BASE}/nodes/", headers=_hdrs(token), json=payload)
    r.raise_for_status()
    node_id = r.json()["data"]["id"]
    return node_id


def upload_file(token: str, node_id: str, path: Path, dest_name: str) -> None:
    url = f"{WB_BASE}/resources/{node_id}/providers/osfstorage/?name={dest_name}"
    headers = {"Authorization": f"Bearer {token}"}
    with path.open("rb") as f:
        r = requests.put(url, headers=headers, data=f.read())
    r.raise_for_status()


def create_draft(token: str, node_id: str, schema_id: str) -> str:
    payload = {
        "data": {
            "type": "draft_registrations",
            "relationships": {
                "registration_schema": {
                    "data": {"type": "registration_schemas", "id": schema_id},
                },
            },
        }
    }
    r = requests.post(
        f"{API_BASE}/nodes/{node_id}/draft_registrations/",
        headers=_hdrs(token), json=payload,
    )
    r.raise_for_status()
    return r.json()["data"]["id"]


def patch_draft_responses(token: str, draft_id: str, responses: dict) -> None:
    payload = {
        "data": {
            "id": draft_id,
            "type": "draft_registrations",
            "attributes": {"registration_responses": responses},
        }
    }
    r = requests.patch(
        f"{API_BASE}/draft_registrations/{draft_id}/",
        headers=_hdrs(token), json=payload,
    )
    r.raise_for_status()


def finalize_registration(token: str, draft_id: str, embargo_end_date: str | None) -> str:
    attrs: dict[str, object] = {"category": "project"}
    if embargo_end_date:
        attrs["embargo_end_date"] = embargo_end_date
    payload = {
        "data": {
            "type": "registrations",
            "attributes": attrs,
            "relationships": {
                "draft_registration": {
                    "data": {"type": "draft_registrations", "id": draft_id},
                },
            },
        }
    }
    r = requests.post(f"{API_BASE}/registrations/", headers=_hdrs(token), json=payload)
    r.raise_for_status()
    return r.json()["data"]["id"]


# ===========================================================================
# Main
# ===========================================================================

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", help="OSF PAT (or env OSF_TOKEN)")
    parser.add_argument("--working-dir", type=Path, default=Path.cwd(),
                        help="Directory containing the files in ATTACH_FILES (default: cwd).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate payload + file list, print summary, do not call API.")
    parser.add_argument("--skip-files", action="store_true",
                        help="Skip the WaterButler upload step (debug only).")
    parser.add_argument("--skip-finalize", action="store_true",
                        help="Stop after PATCHing the draft; do not POST registration.")
    parser.add_argument("--embargo-until", default=None,
                        help="ISO date (YYYY-MM-DD) for embargoed visibility. Default: public on submission.")
    parser.add_argument("--no-confirm", action="store_true",
                        help="Skip the interactive confirmation before finalize.")
    args = parser.parse_args()

    # Validate payload regardless of mode.
    errors = validate_payload()
    if errors:
        print("PAYLOAD VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    # Validate files.
    found, missing = validate_files(args.working_dir)
    print(f"Files found:   {len(found)}")
    print(f"Files missing: {len(missing)}")
    if missing:
        for f in missing:
            print(f"  - MISSING: {f}")

    if args.dry_run:
        print("\n=== DRY RUN ===")
        print(f"Project title: {PROJECT_TITLE}")
        print(f"Schema id:     {SCHEMA_ID}  (OSF Preregistration v4)")
        print(f"Response keys: {len(RESPONSES)}")
        print()
        for k in sorted(RESPONSES.keys(), key=lambda s: int(s.split('-')[1])):
            v = RESPONSES[k]
            if isinstance(v, list):
                if not v:
                    summary = "[]"
                else:
                    summary = f"[{len(v)} item(s); first: {repr(str(v[0])[:60])}]"
            elif isinstance(v, str):
                summary = f"({len(v)} chars) {repr(v[:80])}"
            else:
                summary = f"{type(v).__name__}: {repr(v)[:60]}"
            print(f"  {k}: {summary}")
        print("\nFiles to attach (load-bearing for reproducibility):")
        for p in found:
            size = p.stat().st_size
            print(f"  {size:>10,} B  {p.relative_to(args.working_dir)}")
        return 0

    token = args.token or os.environ.get("OSF_TOKEN")
    if not token:
        print("ERROR: need --token or OSF_TOKEN env var (PAT from osf.io/settings/tokens with osf.full_write scope)")
        return 1

    # Step 1: Create project.
    print(f"\n[1/5] Creating OSF project ‘{PROJECT_TITLE}’ ...")
    node_id = create_project(token, PROJECT_TITLE, PROJECT_DESCRIPTION, public=True)
    project_url = f"https://osf.io/{node_id}/"
    print(f"      project: {project_url}")

    # Step 2: Upload files.
    if args.skip_files:
        print("[2/5] Skipping file uploads (per --skip-files).")
    else:
        print(f"[2/5] Uploading {len(found)} files via WaterButler ...")
        for p in found:
            dest_name = p.relative_to(args.working_dir).as_posix().replace("/", "__")
            print(f"      uploading {p.relative_to(args.working_dir)} → {dest_name}")
            upload_file(token, node_id, p, dest_name)
            time.sleep(0.5)

    # Step 3: Create draft.
    print("[3/5] Creating draft registration ...")
    draft_id = create_draft(token, node_id, SCHEMA_ID)
    print(f"      draft: https://osf.io/registries/drafts/{draft_id}/")

    # Step 4: PATCH responses.
    print("[4/5] PATCHing draft with registration_responses ...")
    patch_draft_responses(token, draft_id, RESPONSES)

    if args.skip_finalize:
        print("\n[5/5] STOP per --skip-finalize. Draft created but NOT registered.")
        print(f"     Review at: https://osf.io/registries/drafts/{draft_id}/")
        print(f"     Project:   {project_url}")
        print("     Re-run without --skip-finalize to submit, or finalize via the OSF web UI.")
        return 0

    # Step 5: Finalize.
    if not args.no_confirm:
        print("\n[5/5] About to finalize the registration. THIS IS IRREVERSIBLE.")
        print(f"      Project: {project_url}")
        print(f"      Draft:   https://osf.io/registries/drafts/{draft_id}/")
        print(f"      Embargo: {args.embargo_until or 'none (public on submission)'}")
        confirm = input("Type FINALIZE to proceed, anything else to abort: ")
        if confirm.strip() != "FINALIZE":
            print("Aborted. Draft remains; re-run to retry.")
            return 0

    print("[5/5] POSTing /v2/registrations/ to finalize ...")
    reg_id = finalize_registration(token, draft_id, args.embargo_until)
    print(f"\n✅ REGISTERED.")
    print(f"   registration: https://osf.io/{reg_id}/")
    print(f"   project:      {project_url}")
    print(f"   schema:       OSF Preregistration v4 ({SCHEMA_ID})")
    print(f"\nAdd the OSF DOI to gate-0.5/README.md once issued.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
