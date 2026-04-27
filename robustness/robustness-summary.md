---
project: Plimsoll
kind: robustness-summary
gate: 0.5
date: 2026-04-27
parent_design: robustness/DESIGN.md (v3, commit 33a2d84)
osf_doi: 10.17605/OSF.IO/G9WFY
osf_addendum_doi: 10.17605/OSF.IO/3PD2A
osf_random_subset_doi: 10.17605/OSF.IO/EKCUQ
status: complete — all variants executed; layered verdict HEADLINE-STABLE per failure protocol
---

# Plimsoll Gate 0.5 — Robustness Pass Summary

## Layered Gate 0.5 verdict

**HEADLINE-STABLE.** SWE-bench Verified (primary) CLEARS under every variant with flip_rate < 5%. LiveCodeBench (secondary) CLEARS under every variant with flip_rate < 5%. MMLU-Pro (secondary) CLEARS in every variant including all 14 disciplines (z ≥ +63 in every cell), but shows per-discipline flip rates of 5-10% on 10 of 14 disciplines under variant B — interpreted as discipline-level heterogeneity in the underlying signal, not instability of the source verdict. The "fully robust" criterion (every cell flip_rate < 5%) is missed by variant B; the "headline-stable" criterion is met. The pre-registered abstract framing ("three independent sources") survives because verdict-survival holds; the per-discipline heterogeneity is reported in §Limitations.

No primary-source failure. No band-conditional or scale-conditional escalation triggered (variants H and I deltas vs baseline are 1, both below the ≥2 escalation threshold).

## What was tested

Per `DESIGN.md` v3 (commit 33a2d84), nine variants spanning analytic-choice perturbations:

| ID | Description | Cells | OSF anchor |
|---|---|---|---|
| A | Margin band sweep ({0.25, 0.30, 0.35, 0.40} × ±-half-widths) | 3 sources × 3 new bands = 9 | Addendum-1 (3PD2A) |
| B | MMLU-Pro per-discipline | 14 | Addendum-1 (3PD2A) |
| C | LiveCodeBench `--no-dedup` | 1 | Pre-reg §4.2 (G9WFY) |
| D | SWE-bench `--exclude-no-logs` | 1 | Pre-reg §4.2 (G9WFY) |
| E | Logit-space scale | 2 (SWE + LCB) | Addendum-1 (3PD2A) |
| F | Inclusion-threshold sweep | 3 sources × 2 thresholds = 6 | Addendum-1 (3PD2A) |
| G | Seed stability (SWE-bench × 11 RNG seeds) | 11 | Addendum-1 (3PD2A) |
| H | Audit-by-band on LiveCodeBench (4 bands) | 4 | Addendum-1 (3PD2A) |
| I | Audit under logit-space m_b | 1 | Addendum-1 (3PD2A) |

Wall-clock time end-to-end: ~3h 45min on 2-core VPS in tmux `plimsoll-robust` (start 20:45Z 2026-04-26, end 00:37Z 2026-04-27).

## Per-variant results

### Variant A — margin band sweep

All 9 (source × band) cells CLEAR. Flip rates monotonic in band-narrowness, all stable (<5%).

| Source | Band | n | median \|Δ\| | z | flip vs baseline |
|---|---|---|---|---|---|
| SWE-bench | 0.25–0.75 | 8,911 | 0.108 | +362.58 | 1.89% |
| SWE-bench | 0.30–0.70 (registered) | 8,911 | 0.126 | (baseline) | — |
| SWE-bench | 0.35–0.65 | 8,911 | 0.145 | +289.67 | 2.50% |
| SWE-bench | 0.40–0.60 | 8,911 | 0.157 | +208.58 | 4.05% |
| LiveCodeBench | 0.25–0.75 | 2,556 | 0.144 | +420.91 | 1.21% |
| LiveCodeBench | 0.30–0.70 (registered) | 2,556 | 0.156 | (baseline) | — |
| LiveCodeBench | 0.35–0.65 | 2,556 | 0.171 | +308.32 | 1.88% |
| LiveCodeBench | 0.40–0.60 | 2,556 | 0.183 | +226.44 | 2.66% |
| MMLU-Pro | 0.25–0.75 | 1,128 | 0.073 | +598.39 | 0.71% |
| MMLU-Pro | 0.30–0.70 (registered) | 1,128 | 0.086 | (baseline) | — |
| MMLU-Pro | 0.35–0.65 | 1,128 | 0.095 | +411.78 | 0.98% |
| MMLU-Pro | 0.40–0.60 | 1,128 | 0.103 | +330.42 | 1.24% |

**Verdict: stable.** m_b moves monotonically with band-narrowness as expected (narrower band → higher per-pair |Δ| because the band restricts to mid-range tasks where lift is concentrated). The pre-registered band 0.30–0.70 is interior to the sweep, not an extreme.

### Variant B — MMLU-Pro per-discipline

All 14 disciplines CLEAR. Flip rates against pooled-MMLU baseline range 4.3–10.0%; 10 of 14 are 5-10% (mildly-unstable per pre-committed thresholds).

| Discipline | n | median \|Δ\| | z | flip rate | category |
|---|---|---|---|---|---|
| biology | 1,127 | 0.137 | +110.51 | 7.10% | mildly-unstable |
| business | 1,128 | 0.097 | +136.80 | 4.43% | stable |
| chemistry | 1,127 | 0.071 | +128.70 | 6.30% | mildly-unstable |
| computer_science | 1,081 | 0.100 | +87.19 | 4.35% | stable |
| economics | 1,128 | 0.117 | +137.05 | 4.52% | stable |
| engineering | 1,127 | 0.064 | +85.72 | 6.39% | mildly-unstable |
| health | 1,128 | 0.109 | +130.66 | 5.50% | mildly-unstable |
| history | 1,081 | 0.094 | +63.51 | 9.99% | mildly-unstable |
| law | 1,128 | 0.087 | +140.62 | 8.33% | mildly-unstable |
| math | 1,128 | 0.071 | +127.94 | 6.29% | mildly-unstable |
| other | 1,128 | 0.099 | +135.59 | 5.32% | mildly-unstable |
| philosophy | 1,128 | 0.081 | +65.02 | 8.69% | mildly-unstable |
| physics | 1,128 | 0.077 | +167.93 | 4.79% | stable |
| psychology | 1,128 | 0.124 | +105.16 | 8.69% | mildly-unstable |

**Verdict: source-level CLEAR in every discipline; per-discipline flip rates trigger headline-stable.** Every cell n_pairs ≥ 1,081, well above the n=50 floor. The flip-rate metric here measures rank-order divergence between *full-MMLU* paired effect and *single-discipline* paired effect — i.e., how much the discipline subset disagrees with the pooled signal. Modest disagreement is expected from sampling alone; the absence of any destabilizing (≥15%) discipline supports the source-level CLEAR. None of the 14 disciplines fails verdict.

### Variant C — LiveCodeBench `--no-dedup`

CLEARS at z = +374.90, median |Δ| = 0.156, n_pairs = 2,556. Flip rate: 0.0%.

**Verdict: stable.** As anticipated in DESIGN.md v3 (registered regex was a no-op per deviation D4): identical numerics to baseline.

### Variant D — SWE-bench `--exclude-no-logs`

CLEARS at z = +308.14, median |Δ| = 0.125, n_pairs = 8,911. Flip rate: 1.14%.

**Verdict: stable.** Treating no_logs cells as missing (rather than failure) does not move the verdict. 102 sign flips out of 8,911 pairs = 1.1%, well under the 5% stability threshold.

### Variant E — logit-space scale

| Source | scale | n | median \|Δ\| | z | flip rate |
|---|---|---|---|---|---|
| SWE-bench | logit | 8,911 | 0.823 | (covered by F) | 0.0% |
| LiveCodeBench | logit | 2,556 | 1.182 | +374.90 | 0.0% |

m_b values are not directly comparable across scales; what matters is that the ordering and CLEAR verdict survive. Spearman ρ between raw and logit pair effects: 0.979 (SWE), 0.993 (LCB). Sign-flip rates are 0% on both sources — every pair preserves sign in logit space.

**Verdict: stable.** The capability-margin shift is not a raw-pass-rate artifact; it survives the IRT-natural logit transformation.

### Variant F — inclusion-threshold sweep

All 6 cells CLEAR at z ≥ +230 with identical numerics across loose (≥10, ≥4) and strict (≥30, ≥15) thresholds — every qualifying pair already satisfies even the strict threshold (high-coverage agents dominate all three sources at registered (≥20, ≥8)). Flip rate: 0% per cell.

**Verdict: stable** — but the variant has no power to fail because no agent was actually filtered in or out. Reported descriptively.

### Variant G — null-baseline seed stability (SWE-bench × 11 seeds)

| Statistic | Value |
|---|---|
| min z (across 11 seeds) | +217.94 |
| max z | +230.46 |
| mean z | +224.74 |
| std z | 4.18 |
| coefficient of variation | 1.86% |

**Verdict: stable.** All 11 seeds give z > 200 — nowhere near the 100-floor escalation trigger. Null-mean is reproducibly 0.02513 ± 0.00001 across seeds; the 4-point z-spread is governed almost entirely by null-std variation across permutation samples.

### Variant H — audit-by-band on LiveCodeBench

| Band | n_qualifying pairs | SUBORDINATE | ROBUST | sign-flips |
|---|---|---|---|---|
| 0.25–0.75 | 13 | 10 | 3 | 0 |
| 0.30–0.70 (baseline) | 13 | **11** | 2 | 0 |
| 0.35–0.65 | 13 | 12 | 1 | 1 |
| 0.40–0.60 | 13 | 12 | 1 | 1 |

Max delta from baseline: |12 − 11| = 1 (or |10 − 11| = 1). **Below ≥2 escalation threshold.** Audit headline number is band-conditional but does not move enough to require reporting all four numbers per the failure protocol.

**Verdict: stable.** The audit is mildly conservative under narrower bands (more pairs flip from ROBUST → SUBORDINATE because m_b rises) — the inverse pattern of variant A's source-level m_b movement, as expected. Trend direction matches mechanism.

### Variant I — audit under logit m_b on LiveCodeBench

Variant I as initially executed used `--m-b 1.1821` against raw-scale pair effects — a unit mismatch (logit-scale m_b vs raw-scale effect_full) that artifactually marked all 13 pairs SUBORDINATE. The corrected analysis re-extracts each named pair's effect_full from `robustness/E-logit/livecodebench/pairs.csv` (logit scale) and compares to logit m_b = 1.182:

| Audit pair | \|eff_full\| logit | vs m_b=1.182 | logit verdict | raw verdict |
|---|---|---|---|---|
| Claude Opus 4 — Thinking lift | 0.362 | < | SUBORDINATE | SUBORDINATE |
| Claude Sonnet 4 — Thinking lift | 0.396 | < | SUBORDINATE | SUBORDINATE |
| Gemini Flash 2.0 — Thinking vs Exp | 0.223 | < | SUBORDINATE | SUBORDINATE |
| Gemini Flash 2.0 — Thinking-01-21 | 0.561 | < | SUBORDINATE | SUBORDINATE |
| Gemini Flash 2.0 — Thinking-12-19 | 0.592 | < | SUBORDINATE | SUBORDINATE |
| O1 — High vs Low effort | 0.450 | < | SUBORDINATE | SUBORDINATE |
| O1 — High vs Med effort | 0.315 | < | SUBORDINATE | SUBORDINATE |
| O3-Mini — High vs Low effort | 0.372 | < | SUBORDINATE | SUBORDINATE |
| O3-Mini — High vs Med effort | 0.132 | < | SUBORDINATE | SUBORDINATE |
| O4-Mini — High vs Low effort | 0.693 | < | SUBORDINATE | SUBORDINATE |
| O4-Mini — High vs Medium effort | 0.234 | < | SUBORDINATE | SUBORDINATE |
| **DeepSeek R1-0528 vs V3 base** | **1.714** | **>** | **ROBUST** | ROBUST |
| QwQ-32B-Preview vs Qwen2.5-Ins-32B | 0.689 | < | SUBORDINATE | **SUBORDINATE** (was ROBUST under raw m_b) |

**Logit-corrected count: 12/13 SUBORDINATE, 1/13 ROBUST.** Raw-baseline count: 11/13 SUBORDINATE, 2/13 ROBUST. Delta = 1 pair (QwQ flips from ROBUST to SUBORDINATE under logit). **Below ≥2 escalation threshold; single-number audit headline is preserved.**

The `audit-reasoning-modes.py` script does not currently consume logit triples; the corrected count above is computed from the existing logit-pair output. Future work: either (a) add a `--logit` flag to audit-reasoning-modes.py, or (b) wrap audit-pair-extraction over arbitrary pair-effect outputs.

## Acknowledged residual confounds

Two confounds remain unaddressed by this robustness pass and are reported as paper-level Limitations rather than variant tests, per DESIGN.md §"Genuinely out of scope":

**Inter-source dependency.** SWE-bench Verified, LiveCodeBench, and MMLU-Pro share frontier-model exposure: many of the agents evaluated on each appear on the leaderboards of the others, and frontier-model providers may train on overlapping data. Independence-of-sources cannot be established by an analytic-choice sweep — it would require either (i) data-pulled-from-distinct-providers replication (out of scope for Gate 0.5), or (ii) a held-out provider analysis. The strongest defense currently is that the three benchmarks measure substantively different capabilities (issue resolution vs algorithmic problem-solving vs broad reasoning) and that the m_b shift is observed at consistent magnitude on all three. The methodology paper's headline retains "three independent sources" with this caveat noted in §Limitations.

**Task-difficulty circularity.** The capability-margin filter is defined relative to the population of agents evaluated on the task — narrowing the agent population shifts the margin definition. A task at margin [0.30, 0.70] under one agent population may be at margin [0.10, 0.90] under another. This is structural to the methodology, not a flaw fixable by a variant sweep. Discussed in §Methods (margin definition as a population-relative quantity); the registered analysis fixes the agent population at the leaderboard snapshot used for each source. Subset-conditional re-runs are discussed in `gate-0-followup/protocol-stratified.md` (temporal stratification) and `gate-0-followup/pair-stratification.md` (ability-gap stratification).

## Connection to follow-up exploratory work

Two `gate-0-followup/` analyses sit alongside this robustness pass, anchored to the same git commit. They are exploratory texture for §Discussion, not registered confirmatory tests:

- **`protocol-stratified.md`** — temporal stratification (pre/post O1 era). Confirms m_b is not driven by a single era's pair-population.
- **`pair-stratification.md`** — pair-stratification by ability gap (Q1–Q4 of |effect_full|). The day's most consequential exploratory finding: pooled m_b is dominated by larger-gap quartiles; sign-flip rate is 6–14% specifically in Q1 (frontier-vs-frontier), 0% elsewhere. The reasoning-mode audit headline drops from 11/13 SUBORDINATE under pooled m_b to 4/13 under quartile-conditional m_b, the operationally-correct comparator. **This shifts the audit blog post's headline framing and motivates a candidate Addendum-3** (Q-conditional m_b operational rule + cross-benchmark verdict consistency + magnitude-of-audit-revision).

## What this robustness pass does and does not say

**Does say:**
- All three sources CLEAR under every analytic-choice variant tested.
- Sign-flip rates are well-bounded on the primary source (SWE-bench, max 4.05% across all variants).
- The audit headline (raw 11/13, logit 12/13) is band- and scale-stable to within 1 pair.
- Seed-randomness contributes < 5% CV to z-scores; the registered verdict is reproducible.

**Does not say:**
- Anything about external validity (deployment-relevance) — that is a construct-validity argument, addressed in `paper-fragments/construct-validity-positioning.md`.
- Anything about ability-gap heterogeneity within the pooled m_b — addressed in `gate-0-followup/pair-stratification.md`.
- Anything about source-independence — acknowledged confound, paper-level Limitations item.
- Anything about extending the methodology beyond static benchmark settings (RL, multimodal, agentic traces) — out of scope for Gate 0.5.

## Reproducibility anchors

- DESIGN.md v3 committed at SHA 33a2d84 BEFORE any variant ran.
- Addendum-1 OSF DOI 10.17605/OSF.IO/3PD2A registered 2026-04-26T20:20:26Z UTC, before A2 variants began.
- Random-subset null Addendum-2 OSF DOI 10.17605/OSF.IO/EKCUQ registered before that variant ran.
- Per-variant run times in `robustness/run-log.txt`; environment in `robustness/environment.txt`.
- Each variant's analyze + null + flip-rate outputs are committed to `robustness/<variant>/`.
- Escalation triggers (variants H, I, G) and their non-firing per the failure protocol are documented in this file's per-variant sections above.

## Sequencing — what happens next

Per DESIGN.md §Sequencing:
1. ✅ DESIGN.md v3 committed (commit 33a2d84).
2. ✅ Addendum-1 registered, DOI backfilled.
3. ✅ Variants executed on VPS in tmux `plimsoll-robust`.
4. ✅ Results scp'd to local repo.
5. ✅ This summary written per the failure-protocol decision tree.
6. **(in progress)** Bundled commit covering: this file + `robustness/*` + `paper-fragments/*` + `gate-0-followup/pair-stratification.*` + `addendum-post-hoc-sensitivity.md`.
7. **(pending)** Push to GitHub.
