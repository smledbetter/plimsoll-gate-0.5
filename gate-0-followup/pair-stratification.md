---
title: Plimsoll Gate 0.5 — pair-stratification by ability gap (exploratory)
status: exploratory texture for §Discussion (NOT registered)
date: 2026-04-26
parent_design: gate-0.5/robustness/DESIGN.md (v3, commit 33a2d84)
prompted_by: K&B literature review (paper-fragments/equating-tradition-positioning.md)
git_anchor: this commit
---

# Pair-stratification by ability gap

## Why this exists

The Kolen & Brennan literature-review agent flagged a real methodological gap in Plimsoll's current Gate 0.5 protocol:

> "Aggregating across pairs treats model-pairs as exchangeable, which they are not (frontier vs. frontier differs from frontier vs. weak). Stratify pairs by ability gap before pooling m_b, or report m_b conditional on gap quantile. This is a real methodological gap in the current Gate 0.5 protocol and is worth a pre-registered amendment before Gate 1."

Pooled m_b masks heterogeneity if pairs at different ability gaps have systematically different paired-effect-size shifts.

This file is exploratory texture for the methodology paper's §Discussion. It is NOT registered, NOT confirmatory, and does not feed the Gate 0.5 verdict. Same provenance discipline as `gate-0-followup/protocol-stratified.md` — git-commit anchor sufficient.

## Method

For each of the 3 sources (SWE-bench Verified, LiveCodeBench, MMLU-Pro), bin qualifying pairs by `|effect_full|` quartile and compute m_b (median |abs_delta|), p75, p95, sign_flip_rate, and n per quartile. `effect_full` is the registered pair-restricted-to-shared-tasks paired effect; its absolute value is a pair-specific ability-gap proxy that is already computed in the registered `pairs.csv` outputs.

Code: `gate-0-followup/pair-stratification.py`. Runs in seconds against the registered `component-c-runs/<source>/<source>-pairs.csv` files.

## Result

| Source | Q | n | gap range | m_b | p95 \|Δ\| | flip rate |
|---|---|---|---|---|---|---|
| **SWE-bench** | Q1 | 2,230 | [0.000, 0.082] | **0.033** | 0.108 | **14.1%** |
|  | Q2 | 2,259 | [0.084, 0.188] | 0.105 | 0.210 | 0.0% |
|  | Q3 | 2,206 | [0.190, 0.318] | 0.215 | 0.310 | 0.0% |
|  | Q4 | 2,216 | [0.320, 0.788] | **0.250** | 0.342 | 0.0% |
|  | OVERALL | 8,911 | [0.000, 0.788] | 0.126 | 0.317 | 3.5% |
| **LiveCodeBench** | Q1 | 639 | [0.000, 0.090] | **0.029** | 0.088 | **12.8%** |
|  | Q2 | 639 | [0.091, 0.223] | 0.115 | 0.220 | 0.0% |
|  | Q3 | 640 | [0.223, 0.383] | 0.250 | 0.360 | 0.0% |
|  | Q4 | 638 | [0.383, 0.820] | **0.319** | 0.392 | 0.0% |
|  | OVERALL | 2,556 | [0.000, 0.820] | 0.156 | 0.372 | 3.2% |
| **MMLU-Pro** | Q1 | 282 | [0.000, 0.091] | **0.018** | 0.070 | **6.0%** |
|  | Q2 | 282 | [0.091, 0.183] | 0.069 | 0.134 | 0.0% |
|  | Q3 | 282 | [0.183, 0.305] | 0.143 | 0.197 | 0.0% |
|  | Q4 | 282 | [0.305, 0.688] | **0.203** | 0.243 | 0.0% |
|  | OVERALL | 1,128 | [0.000, 0.688] | 0.086 | 0.227 | 1.5% |

**m_b ratio (max-Q / min-Q):** 7.6× (SWE), 11.1× (LCB), 11.1× (MMLU). Substantial heterogeneity — pooled m_b is dominated by the larger-gap quartiles.

## Two findings

### Finding 1: rank stability fails specifically in Q1 (frontier-vs-frontier)

Sign-flip rate is 12.8–14.1% on the two larger sources at Q1 and ~0% at Q2–Q4. The "rank-stable but effect-size-unstable" headline holds *with structure*: rank stability *fails* for frontier-vs-frontier pairs (small ability gap) and *holds* for pairs with meaningful ability gaps. For larger gaps, rank is preserved cleanly — magnitude is what swings.

This is a sharper claim than the original "rank stable / effect-size unstable" framing, and arguably more interesting: it tells you *which* comparisons the methodology should worry about (frontier-vs-frontier) and *which* are safe under pooled m_b (larger gaps).

### Finding 2: the audit's headline depends on which m_b you compare against

The Gate 0.5 reasoning-mode audit on LiveCodeBench applied **pooled m_b = 0.156** to all 13 paired claims and found 11/13 SUBORDINATE-TO-SHIFT. But the audited pairs (frontier model variants like Claude Opus 4 Thinking vs Claude Opus 4) have small ability gaps — they live in Q1 or Q2 of LCB, not in the pooled distribution.

Re-running the audit with **quartile-conditional m_b** — comparing each pair to the m_b for pairs of its ability-gap quartile:

| Audit pair | \|effect_full\| | Q | Q m_b | Pooled verdict | Q-conditional verdict |
|---|---|---|---|---|---|
| Claude Opus 4 Thinking | 0.081 | Q1 | 0.029 | SUBORDINATE | **ROBUST** |
| Claude Sonnet 4 Thinking | 0.091 | Q2 | 0.115 | SUBORDINATE | SUBORDINATE |
| Gemini Flash 2.0 Thinking vs Exp | 0.056 | Q1 | 0.029 | SUBORDINATE | **ROBUST** |
| Gemini Flash 2.0 Thinking-01-21 | 0.139 | Q2 | 0.115 | SUBORDINATE | **ROBUST** |
| Gemini Flash 2.0 Thinking-12-19 | 0.147 | Q2 | 0.115 | SUBORDINATE | **ROBUST** |
| O1 High vs Low | 0.073 | Q1 | 0.029 | SUBORDINATE | **ROBUST** |
| O1 High vs Med | 0.049 | Q1 | 0.029 | SUBORDINATE | **ROBUST** |
| O3-Mini High vs Low | 0.071 | Q1 | 0.029 | SUBORDINATE | **ROBUST** |
| O3-Mini High vs Med | 0.024 | Q1 | 0.029 | SUBORDINATE | SUBORDINATE |
| O4-Mini High vs Low | 0.099 | Q2 | 0.115 | SUBORDINATE | SUBORDINATE |
| O4-Mini High vs Medium | 0.028 | Q1 | 0.029 | SUBORDINATE | SUBORDINATE |
| DeepSeek R1 vs V3 | 0.349 | Q3 | 0.250 | ROBUST | ROBUST |
| QwQ-32B vs Qwen2.5 | 0.168 | Q2 | 0.115 | ROBUST | ROBUST |

Under quartile-conditional m_b: **4 of 13 SUBORDINATE-TO-SHIFT** (Claude Sonnet 4 Thinking; O3-Mini High vs Med; O4-Mini High vs Low; O4-Mini High vs Medium).

Under pooled m_b: 11 of 13 SUBORDINATE-TO-SHIFT.

The qualitative claim survives — flagship reasoning-mode lifts from Anthropic and OpenAI fall below their pair-class noise floor — but the magnitude is materially different.

## Methodological resolution

Quartile-conditional m_b is the **operationally correct comparator** for an audit. The audited pair has a specific ability gap; the right noise floor is the m_b for pairs of that gap, not the pooled value dominated by larger-gap pairs whose paired-effect-size variance has more headroom.

This is methodologically analogous to DIF analysis conditioning on ability — Plimsoll's pooled m_b doesn't condition; quartile-conditional m_b does. The K&B agent flagged this exact gap.

The paper's resolution should be:

1. **Report quartile-conditional m_b alongside pooled m_b** in §Methods.
2. **Audit each pair against the appropriate m_b for its ability-gap quartile** in §Audit.
3. **Headline empirical claim restated:** "4 of 13 paired reasoning-mode lift claims on LiveCodeBench are SUBORDINATE-TO-SHIFT under the operationally correct quartile-conditional m_b — including Claude Sonnet 4 Thinking and three OpenAI O-mini effort tiers."

The pooled-m_b 11/13 number is reportable as a cautionary illustration: pooled m_b is misleading for audits because it averages across heterogeneous pair classes.

## Implications for the audit blog post

The audit blog post (currently held in draft, not yet published) was written against pooled m_b. Under the methodologically-correct framing, the post needs:

- Updated headline: "Four of thirteen reasoning-mode lifts on LiveCodeBench are below their pair-class noise floor" — or, with named products, "Claude Sonnet 4 Thinking and three OpenAI O-mini effort tiers fail the pair-class noise floor."
- A short technical note explaining why quartile-conditional m_b is the correct comparator (one paragraph, links to this writeup).
- The pooled-m_b 11/13 number can be retained as "under naive pooled m_b" with a clear methodological footnote.

This is a real strengthening of the methodology, not a weakening of the empirical claim — but the marketing-friendly "11 of 13" headline is gone.

## Implications for variant H of the robustness pass

Variant H (audit-by-band) of the currently-running robustness pass tests m_b under different *band* settings, not different *ability-gap* settings. The two are independent perturbations. Variant H's result will speak to band-sensitivity; this exploratory texture speaks to ability-gap-sensitivity. Both should appear in the paper's robustness story.

If variant H also moves the audit count by ≥2 (the registered escalation threshold), the paper must report all four band-conditional numbers per its DESIGN.md commitment. Combined with the quartile-conditional finding here, the audit becomes a multi-perspective diagnostic, not a single-number headline.

## Sequencing

This finding is exploratory texture for §Discussion. Sequencing implications:

1. **Before paper drafting (Gate 1):** the audit blog post draft must be revised to match the quartile-conditional framing.
2. **Before publication:** consider filing a candidate Addendum-3 that pre-registers quartile-conditional m_b as a confirmatory audit rule (in addition to the cross-benchmark verdict consistency test already proposed).
3. **In the bundled push:** this writeup + the CSV ship together with the rest of the robustness pass artifacts.

## Caveats

- The `effect_full` quartile is a pair-specific gap proxy, not a global agent-ability estimate. A future variant could substitute |overall_pass_rate[a] − overall_pass_rate[b]| for `|effect_full|` and check robustness of the finding to the gap definition.
- Boundary effects: pairs near quartile cuts (e.g., Claude Sonnet 4 Thinking at 0.091, just above LCB Q1 max 0.0898) are sensitive to bin-edge placement. Continuous m_b-as-function-of-gap (e.g., LOWESS over `(|effect_full|, |abs_delta|)`) would be a more honest visualization.
- This is single-source quartile binning. A more rigorous version would use cross-source ability-gap quartiles (e.g., quartile by overall MMLU score across all three benchmarks). Future work.

## Output files

- `gate-0-followup/pair-stratification.py` — the analysis script
- `gate-0-followup/pair-stratification-by-ability-gap.csv` — per-source × per-quartile m_b table
- `gate-0-followup/pair-stratification.md` — this writeup
