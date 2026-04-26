---
project: Plimsoll
kind: pre-registration
gate: 0.5
template: OSF Pre-Data Collection Registration (orthodox)
status: registered (DOI 10.17605/OSF.IO/G9WFY, public 2026-04-26)
updated: 2026-04-26
---

# Plimsoll Gate 0.5 — OSF Pre-Registration

## 0. Honesty disclosure

This is a **prospective** pre-registration with one disclosed asymmetry. Per the OSF Preregistration v4 schema's foreknowledge taxonomy, this study corresponds to option **"Authors have observed the data, but have not performed the proposed analyses"** — for the SWE-bench Verified primary source. LiveCodeBench and MMLU-Pro are wholly unseen and would qualify under the stricter "Data exists but the authors have not observed it yet" but the layered design is registered together under the single (more conservative) classification.

The asymmetry, in detail:
- **SWE-bench Verified (primary).** The analyst has prior contact via Ndzomga 2026, who aggregated a 50-instance × 28-agent subset (`swebench_verified_mini`). That subset constitutes 1,400 of the 67,000 cells (~2.1%) of the registered cell space. The remaining ~98% (450 instances × 134 agents minus the seen 1,400 cells) is unseen. Plimsoll Gate 0 (a different exploratory analysis) was performed on the seen 2.1%. The result of Gate 0 — observed median |Δ paired effect size| = 0.090 on Ndzomga's heatmap — informed the threshold of 0.05 in this pre-reg's decision rule. The proposed Gate 0.5 analyses on the held-out cell space have not been performed.
- **LiveCodeBench (confirmatory secondary, code domain).** Wholly unseen. The analyst has not accessed the per-question pass/fail data per submission.
- **MMLU-Pro (confirmatory secondary, scope).** Wholly unseen. The analyst has not accessed the per-question pred/answer data per model.

This document supersedes a draft Gate 0 post-hoc registration (see `gate-0/pre-registration.md`, marked SUPERSEDED), which the original Study Gate prescribed as Change 2 but which was dropped 2026-04-26 in favor of this prospective gate.

## 1. Study Information

**Title.** Plimsoll Gate 0.5: Prospective replication of capability-margin effect-size instability on three independent held-out sources.

**Authors.** Steven M. Ledbetter (sole, smledbetter@gmail.com).

**Description.** Plimsoll Gate 0 (a post-hoc re-analysis of Ndzomga 2026's 22K-row agent-leaderboard heatmap) found that filtering to capability-margin tasks (mean pass rate ∈ [0.30, 0.70]) preserves rank order (ρ = 0.958) but does *not* preserve paired effect size (median |Δ| = 0.090, sign flips 11.3%). Gate 0.5 is a prospective replication on three held-out sources to test whether this pattern generalizes beyond a single dataset and to satisfy Plimsoll protocol elements 3 (pre-registration) and 5 (power analysis) the orthodox way.

**Hypotheses.**

For each source X ∈ {SWE-bench Verified, LiveCodeBench, MMLU-Pro}:

- **H1(X).** Median absolute paired effect-size shift |Δ| between full-task computation and margin-band ([0.30, 0.70]) computation on source X exceeds the median |Δ| produced by a within-pair condition-label permutation null at p < 0.001 (one-sided, observed ≥ null).
- **H2(X).** Spearman ρ(effect_full, effect_margin) ≥ 0.85, replicating the rank-stability pattern.
- **H3(X).** Sign-flip rate exceeds 5%.

The Gate 0.5 verdict combines per-source verdicts via the layered decision rule below.

**Decision rule (per source).** Source X **clears** iff median |Δ| ≥ 0.05 AND null-baseline z ≥ 3 (P(null ≥ obs) ≤ ~0.001). Otherwise X **fails**.

**Layered verdict combining sources:**

| Outcome path | Plimsoll verdict |
|---|---|
| All three clear | Gate 0.5 clears with maximum scope ("agentic code + competitive programming + multi-discipline knowledge"). |
| SWE-bench + LiveCodeBench clear; MMLU-Pro fails | Gate 0.5 clears with code-eval scope ("Plimsoll for code-eval; multi-discipline knowledge differs — discussed as open question"). |
| SWE-bench clears alone | Gate 0.5 clears as single-source prospective replication of Gate 0; both secondary non-replications discussed as future work. |
| SWE-bench fails | **Gate 0.5 fails.** Plimsoll methodology paper does not ship as currently framed. |

Per-source statistics and per-benchmark texture are reported in all outcome paths.

## 2. Sampling Plan / Data Sources

Three public held-out sources, all to be pulled *after* this registration is timestamped on OSF:

### 2.1 SWE-bench Verified — Primary

- **Repository.** `https://github.com/swe-bench/experiments` (no LICENSE file; data treated as public facts about a public leaderboard per Feist v. Rural 1991, and per the repo's own stated reproducibility intent: "publicly accessible and meant to enable greater reproducibility and transparency").
- **Frozen commit SHA.** [TBD at registration time — pinned by analyst before pulling data].
- **Layout.** `evaluation/verified/<submission>/results/results.json` per submission, with `resolved`, `no_generation`, `no_logs` instance-ID lists.
- **Task universe.** Canonical SWE-bench Verified 500-instance list from the `princeton-nlp/SWE-bench_Verified` dataset on HuggingFace. Frozen at registration time.
- **Submission count.** 134 (as of 2026-04-26). Submissions added between this registration and Component C run will be excluded by frozen-list intersection.
- **Cell coverage vs Gate 0.** Ndzomga 2026's `swebench_verified_mini` covered 50 of 500 instances × 28 of 134 agents (1,400 of 67,000 cells, ~2%). The remaining ~98% is held out from the analyst's view.

### 2.2 LiveCodeBench — Confirmatory secondary (code domain)

- **Repository.** `https://github.com/LiveCodeBench/submissions` (MIT-licensed).
- **Frozen commit SHA.** [TBD at registration time].
- **Layout.** `<model_variant>/Scenario.codegeneration_*_eval_all.json` per submission.
- **Coverage.** 73 model-submission directories; 1055 questions across Codeforces, LeetCode, AtCoder; explicit `graded_list[bool]` per question.
- **Dedup.** ≥50 distinct model families after canonical dedup (see preprocessing rule §4.2).

### 2.3 MMLU-Pro — Confirmatory secondary (scope)

- **Repository.** `https://github.com/TIGER-AI-Lab/MMLU-Pro` (Apache-2.0 code, MIT dataset).
- **Frozen commit SHA.** [TBD at registration time].
- **Layout.** `eval_results/<model>.zip`, each ZIP containing per-discipline JSON with per-question records (`pred`, `answer`, `category`).
- **Coverage.** 48 model-output ZIPs, 12,032 questions across 14 disciplines.

## 3. Variables

**Independent variable (within-pair).** Task selection regime: `full` (all qualifying tasks for which both agents in the pair have scores) vs. `margin` (subset where mean-pass-rate difficulty falls in [0.30, 0.70]).

**Dependent variable.** Paired effect size, defined as the mean of per-task score differences between agents A and B over the qualifying task set:

> effect = mean(score_A[t] − score_B[t]) for t ∈ qualifying tasks.

This is a mean-difference effect size. Score domain is {0, 1} for SWE-bench (resolved/not), {0, 1} for LiveCodeBench (graded_list[0]), {0, 1} for MMLU-Pro (pred==answer).

**Pairing unit.** (source, agent A, agent B) unordered pair, computed within source and (for LiveCodeBench / MMLU-Pro) also reportable per-benchmark / per-discipline.

**Difficulty operationalization.** Task difficulty defined per source as `mean(success)` across all agents that attempted the task. Margin band membership: difficulty ∈ [0.30, 0.70]. Same band for all three sources; per-source band tuning is a sensitivity check, not the primary analysis.

## 4. Design Plan / Analysis Plan

### 4.1 Frozen analysis pipeline

Single `analyze.py` and `null-baseline.py` parametrized over data source. Frozen at git commit SHA at registration time. The analysis is identical to Gate 0's, with vectorization improvements to handle the larger MMLU-Pro shape; the statistic and decision rule are unchanged.

**Inclusion thresholds (per pair):** ≥20 shared tasks for `full` analysis; ≥8 shared margin-band tasks for `margin` analysis. Pairs failing either threshold are dropped. Identical to Gate 0.

**Headline statistics (per source):**
- Spearman ρ(effect_full, effect_margin) and Pearson r over all qualifying pairs.
- Distribution of |Δ| = |effect_margin − effect_full|: median, p75, p95, max.
- Sign-flip rate: P(sign(effect_full) ≠ sign(effect_margin)).
- Per-benchmark / per-discipline breakdown where coverage permits.

**Inference (H1) — null-baseline permutation.** For each source: 1000 within-pair condition-label permutations under H0 (agents A and B exchangeable on each task). Compute median |Δ| across qualifying pairs per permutation. Z-score and tail probability vs. observed.

**Inference (H2, H3).** Descriptive only. Reported with 95% bootstrap CIs (10,000 resamples over pairs, percentile method). Not gated.

### 4.2 Per-source preprocessing — pre-committed

**SWE-bench Verified** (`prep-swebench.py`):
- `no_logs` instance IDs treated as **failure** (matches public leaderboard scoring; the conservative interpretation). Sensitivity check: re-run with `--exclude-no-logs` and report both. Default = primary.
- All 134 submissions treated as **134 distinct agents**. No dedup by scaffold-and-model; Plimsoll's claim is about (agent, task) pairs, not (scaffold, model) factorization.
- Submissions missing an instance ID treated as **failure** (conservative).

**LiveCodeBench** (`prep-livecodebench.py`):
- Pass/fail = `graded_list[0]` (first-attempt pass@1). Sensitivity check: any-pass via `--any-pass`.
- Variants per model family **deduplicated** to one canonical variant per family — the latest-mtime directory under common variant suffixes (`_thinking`, `_temp\d+`, `_seed\d+`, `_v\d+`). Override available via `--no-dedup`. Default = dedup.
- Tasks identified by `(platform, contest_id, question_id)` tuple to avoid cross-platform ID collision.

**MMLU-Pro** (`prep-mmlu-pro.py`):
- Pass/fail = `pred == answer` with whitespace-trimmed string comparison.
- Pooled across 14 disciplines = primary analysis. Per-discipline texture preserved in `benchmark_name` column; per-discipline analysis is supplementary.
- Records missing `pred` or `answer` are skipped (treated as no-attempt rather than failure).

### 4.3 Power analysis — derived from Component A simulation

The minimum detectable effect (MDE) per source is derived from a frozen simulation that generates synthetic (agent, task) score matrices under three generative families and applies the Gate 0 pipeline:

- **Rasch / 1PL IRT** — single-ability null model. P(success) = σ(θ_i − β_j).
- **Compensatory MIRT** at d ∈ {2, 3, 5} — agents have skill vectors θ ∈ R^d; tasks have skill loadings; skills can substitute. P(success) = σ(θ_i · α_j − β_j).
- **Non-compensatory MIRT** at d ∈ {2, 3, 5} — every demanded skill must independently clear its bar; no substitution. P(success) = ∏_k σ(θ_{i,k} − β_{j,k}).

The simulation is run at the actual source shapes (SWE-bench: 134×500; LiveCodeBench: 50×1055; MMLU-Pro: 48×12,032). For each (source, model, parameters) cell, n=1000 replications produce a distribution of median |Δ paired effect size| under that data-generating process. The simulation computes:

1. The α=0.001 critical value of the Rasch (no-MIRT-signal) median |Δ| distribution per source — the threshold above which we reject Rasch.
2. Per-(source, MIRT model, parameters): power = P(simulated median |Δ| > Rasch critical value).

**Asymmetric power finding (pre-registered).** Component A n=1000 results reveal an asymmetric pattern that this registration formalizes:

- **Non-compensatory MIRT achieves ≥80% power against the Rasch null at α=0.001** across all three sources at moderate signal levels. Component A's MDE table reports the smallest signal-scale combination clearing 80% power per (source, d ∈ {2, 3, 5}).
- **Compensatory MIRT achieves 0% power** in every cell of the swept parameter grid (ability_scale × difficulty_scale ∈ {0.5, 1.0, 1.5, 2.0}², 16 cells per (source, d), 144 cells total at n=1000). No parameter combination produces a median |Δ| distribution exceeding the Rasch α=0.001 critical value. **This is itself a pre-registered theoretical finding**: capability-margin filtering does not produce paired-effect-size instability under skill-substitutable models. The instability that Gate 0 observed is therefore a *signature of non-compensatory multidimensional skill structure* (every demanded sub-capability must independently clear), not of multidimensionality per se.

**Implication for the held-out replication.** Under the registered decision rule (median |Δ| ≥ 0.05 AND null-baseline z ≥ 3 per source), Gate 0.5 has high power if the underlying generative process is non-compensatory MIRT at any d ∈ {2, 3, 5} with moderate signal. If the underlying process is compensatory or weak Rasch, the test will not clear — which is methodologically appropriate (those processes do not produce the instability Gate 0 found, and the verdict should reflect the absence of the phenomenon).

**MDE table** (n=1000, frozen from `simulation-results/mde-table.csv`; SEED=20260426). MDE = smallest (ability_scale, difficulty_scale) combination on the {0.5, 1.0, 1.5, 2.0}² grid achieving ≥80% power against the Rasch α=0.001 critical value. "Power at MDE" is the actual achieved power at that grid point.

| Source | Generative family | d | MDE ability scale | MDE difficulty scale | Power at MDE |
|---|---|---|---|---|---|
| SWE-bench Verified | compensatory MIRT | 2 / 3 / 5 | not achieved on grid | not achieved on grid | 0.000 across all 48 cells |
| SWE-bench Verified | non-compensatory MIRT | 2 | 1.5 | 2.0 | 0.877 |
| SWE-bench Verified | non-compensatory MIRT | 3 | 0.5 | 0.5 | 1.000 |
| SWE-bench Verified | non-compensatory MIRT | 5 | 0.5 | 1.5 | 1.000 |
| LiveCodeBench | compensatory MIRT | 2 / 3 / 5 | not achieved on grid | not achieved on grid | 0.000 across all 48 cells |
| LiveCodeBench | non-compensatory MIRT | 2 | 2.0 | 2.0 | 0.919 |
| LiveCodeBench | non-compensatory MIRT | 3 | 0.5 | 0.5 | 0.956 |
| LiveCodeBench | non-compensatory MIRT | 5 | 0.5 | 1.5 | 1.000 |
| MMLU-Pro | compensatory MIRT | 2 / 3 / 5 | not achieved on grid | not achieved on grid | 0.000 across all 48 cells |
| MMLU-Pro | non-compensatory MIRT | 2 | 2.0 | 2.0 | 0.937 |
| MMLU-Pro | non-compensatory MIRT | 3 | 1.0 | 0.5 | 0.842 |
| MMLU-Pro | non-compensatory MIRT | 5 | 0.5 | 1.0 | 1.000 |

**Theoretical-anchor proximity to Gate 0.** Gate 0's observed median |Δ| on Ndzomga's 50×28 SWE-bench subset was 0.090. The Component A simulation cells producing median-of-median |Δ| within 0.005 of that value are exclusively non-compensatory MIRT at d ∈ {2, 3} with low-to-moderate signal scales (e.g., SWE-bench non-comp d=3 at ability=0.5/difficulty=1.0 → 0.0883; LiveCodeBench non-comp d=3 at ability=1.0/difficulty=1.5 → 0.0928; MMLU-Pro non-comp d=3 at ability=1.0/difficulty=2.0 → 0.0889). No compensatory cell reproduces Gate 0's effect magnitude under any swept parameter. This is consistent with the asymmetric power finding above and is itself a pre-registered theoretical anchor: Gate 0's empirical signal is in the regime where Gate 0.5 is well-powered.

Component A's simulation script (`simulation.py`, frozen at git commit SHA at registration time) is itself a methodological prerequisite, not a result — the seed (20260426) and parameter grid are pinned at module level so re-running reproduces the MDE table bit-identically.

### 4.4 Multiple comparisons

Three primary tests (H1 per source). Family-wise correction not applied to the primary tests because the layered decision rule (§1) already encodes the asymmetric weighting across sources. Per-benchmark / per-discipline statistics are descriptive and not subjected to correction.

### 4.5 Missing data

Per-pair: a pair is dropped from a source's analysis if it fails the inclusion thresholds (§4.1). No imputation. Missing-data fractions are reported per source.

## 5. Other / Contingencies

### 5.1 What would falsify Gate 0.5

- SWE-bench Verified failure (median |Δ| < 0.05 OR null-baseline z < 3) → hard kill, paper does not ship as currently framed.
- All three secondary failures with primary clearing → Gate 0.5 still clears as single-source prospective replication (per layered rule), but the existential claim narrows to "SWE-bench Verified specifically."
- Either secondary failing alone is reported honestly per the layered rule and shapes the headline scope but does not kill the gate.

### 5.2 Anticipated reviewer concerns and pre-committed responses

- *"Why a single decision rule across three different benchmark formats?"* — The rule is on the median |Δ| paired-effect-size statistic, which is benchmark-format-agnostic (it operates on any (agent, task, success) triple matrix). The differences between benchmarks are absorbed into the per-source preprocessing rules in §4.2.
- *"Why 80% power at α=0.001 rather than the conventional α=0.05?"* — The Gate 0 result on Ndzomga's data was z=+20.77 against the null — comfortably below α=0.001. Tightening α to match that result's strength makes Gate 0.5 a meaningful test; α=0.05 would clear trivially.
- *"What if the held-out repos add submissions between registration and run?"* — Submissions added after the frozen commit SHA are excluded by frozen-list intersection. The registration timestamp + commit SHAs serve as the audit anchor.

### 5.3 Frozen artifacts at registration time

- Analysis scripts: `analyze.py`, `null-baseline.py`, `simulation.py`, `prep-swebench.py`, `prep-livecodebench.py`, `prep-mmlu-pro.py` — all at git commit SHA [TBD].
- Data source commits: SWE-bench experiments [TBD], LiveCodeBench submissions [TBD], MMLU-Pro [TBD].
- Component A simulation results: `simulation-results/mde-table.csv`, `simulation-results/theoretical-anchor-candidates.csv`, `simulation-results/power-table.csv`, `simulation-results/simulation-summary.csv`.
- This registration document — registered as the OSF pre-registration of record.

### 5.4 Data provenance

Re-analysis of public leaderboard data does not require explicit re-licensing; pass/fail outcomes from automated test runs are facts (Feist v. Rural 1991), and the source repos either explicitly state reproducibility intent (SWE-bench experiments) or carry permissive licenses (LiveCodeBench MIT, MMLU-Pro Apache + MIT). Post-publication courtesy emails to repository maintainers are appropriate academic norm but are not blocking dependencies for this registration.

## 6. Plimsoll protocol cross-walk

| Plimsoll element | How Gate 0.5 satisfies it |
|---|---|
| 1. Saturation profiling | Per-source per-benchmark difficulty distribution computed; ceiling/floor patterns identified |
| 2. Capability-margin selection | [0.30, 0.70] band per Ndzomga 2026, applied uniformly across all three sources |
| 3. Pre-registration | This document, prospectively timestamped on OSF before any held-out data is touched |
| 4. Paired comparison design | Within-pair, within-source; same agents on full vs. margin task sets |
| 5. Power analysis with effect-size disclosure | Component A simulation MDE table (§4.3) per source per generative family |
| 6. Null-result discipline | Decision rule explicitly admits per-source failures and a hard-kill outcome |

## Pre-submission checklist

- [ ] Pin git commit SHA for `swe-bench/experiments`, `LiveCodeBench/submissions`, `TIGER-AI-Lab/MMLU-Pro`.
- [ ] Push `Projects/Research/Plimsoll/gate-0.5/` to a public git remote and pin commit SHA for the analysis scripts.
- [x] Run `simulation.py --n-sims 1000` once and pin the resulting MDE table; fill the §4.3 table from `mde-table.csv`. *Completed 2026-04-26; results in `simulation-results/`.*
- [x] Verify the smoke-run MDE numbers are stable under the registered run (n=1000) before submitting. *Verified — non-compensatory MIRT MDEs match smoke-run pattern; compensatory 0% replicates at n=1000.*
- [ ] Run `prep-*.py` scripts dry — do they produce non-empty (agent, task, success) tables on small subsets without errors? (Validation only; the full data pull happens *after* registration.)
- [ ] Submit to OSF as Pre-Data Collection Registration; copy section headings into OSF form fields.
- [ ] Add OSF DOI to `gate-0.5/README.md` once issued.
- [ ] Pull held-out data, run Component C, populate `gate-0.5/results/`.
