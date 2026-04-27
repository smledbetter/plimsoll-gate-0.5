---
title: Methodology paper — random-subset null section (draft)
status: draft, ready to merge into manuscript
intended_section: §Validation against null hypotheses (or §Robustness checks)
osf_addendum: 10.17605/OSF.IO/EKCUQ
data_anchor: gate-0.5/random-subset-null/
---

# Random-subset null: ruling out the sampling-artifact confound

## Why this test is the deepest

Plimsoll's headline diagnostic is **m_b**, the median across pairs of |effect_margin − effect_full|, where `effect_margin` is the paired effect size restricted to the capability-margin band [0.30, 0.70] and `effect_full` is the same paired effect size measured over all shared tasks. A natural skeptic's reading: m_b might be nothing more than what *any* random subset of the same per-pair size produces, because subsetting a noisy estimator inflates its variance whether or not the subset is "structured" by capability. If true, the capability-margin framing is decorative; what's being measured is finite-sample variance of paired pass-rate differences.

Distinguishing the two requires a null in which the **size** of the per-pair subset matches the band's per-pair n_margin, but the **selection mechanism** is random rather than band-conditional. Under the null, the only thing left to explain a non-zero |Δ| is finite-sample noise. If the observed band-conditional median |Δ| is statistically indistinguishable from this random-subset null, the band is doing no analytic work; if it is distinguishable, the band is selecting for something the random subset misses.

This null was filed prospectively as **OSF Addendum-2** (DOI 10.17605/OSF.IO/EKCUQ) before any held-out execution; the analytic code (commit `23104aa`) was committed and smoke-tested on synthetic data — under no signal it returned z = -1.48 (correctly rejecting falsely-positive runs); under a planted signal it returned z = +3.39 (correctly identifying the true positive) — before the registration was filed.

## Construction

For each pair of agents (a, b) that satisfies the registered inclusion thresholds (≥20 shared tasks, ≥8 within the [0.30, 0.70] band):

- Let `n_full` be the number of shared tasks for the pair, and `n_margin` the integer count falling in the band. Both are read from the registered `analyze.py` output.
- Compute `effect_full = mean(s_a − s_b)` across all `n_full` shared tasks, treating it as fixed.
- For each of N = 1000 permutations (seed = 42, `numpy.random.default_rng`):
  - Sample `n_margin` task indices uniformly without replacement from the `n_full` shared tasks.
  - Compute `effect_random[k] = mean(s_a − s_b)` restricted to that subset.
  - Record `delta_random[k] = |effect_random[k] − effect_full|`.
- Per permutation, aggregate across pairs: `null_median[k] = median(delta_random[k])`.

The random-subset null distribution of m_b is the empirical distribution of `null_median` across the 1000 permutations.

## Decision rule (pre-committed)

Per source independently:

- **z ≥ 3** → capability-margin signal is statistically distinguishable from the random-subset null (signal is real; methodology defended for that source).
- **z < 3** → capability-margin signal is NOT distinguishable (signal is plausibly sampling-artifact-shaped on that source; methodology paper headline must be qualified).

Layered verdict across the three sources:

- **PASS:** z ≥ 3 on all three sources → headline survives intact.
- **PARTIAL:** z ≥ 3 on SWE-bench (primary) but < 3 on a secondary → headline drops "three independent sources" claim, retains primary.
- **FAIL:** z < 3 on SWE-bench primary → headline rewritten; methodology paper acknowledges the registered m_b is sampling structure on the primary source. Public corrigendum on OSF.

A magnitude diagnostic, `ratio = observed_median / null_mean`, is reported alongside z. A ratio near 1 with a technically large z (because the null is very tight) is descriptively concerning even if z passes; the decision rule is gated only on z, but the ratio is reported in every cell.

## Result

| source | n_pairs | observed median \|Δ\| | null mean | null std | z | ratio | decision |
|---|---|---|---|---|---|---|---|
| swebench-verified (primary) | 8,911 | 0.1262 | 0.0198 | 0.000245 | **+434.44** | **6.38×** | DEFENDED |
| livecodebench (secondary) | 2,556 | 0.1562 | 0.0128 | 0.000297 | **+482.75** | **12.24×** | DEFENDED |
| mmlu-pro (secondary) | 1,128 | 0.0865 | 0.0040 | 0.000142 | **+581.00** | **21.44×** | DEFENDED |

P(null ≥ obs) = 0 on every source (no permutation produced a null median ≥ the observed median).

**Layered verdict: PASS.** All three sources clear the z ≥ 3 threshold by approximately two orders of magnitude. The capability-margin signal is statistically distinguishable from the random-subset null on every source, by a wide margin. The registered m_b is **not** a sampling artifact at the registered n.

The magnitude ratios — 6.38× on SWE-bench, 12.24× on LiveCodeBench, 21.44× on MMLU-Pro — also rule out the more cosmetic version of the confound, in which z passes only because the null variance is very small. The observed median |Δ| is between 6× and 21× the random-subset baseline, depending on source.

## What this defends, and what it does not

**Defends:** the capability-margin band [0.30, 0.70] is selecting for something a random subset of the same size cannot reproduce. Whatever m_b is measuring on these three sources, it is not finite-sample variance of paired effect sizes. The headline empirical claim — "Plimsoll Gate 0.5 confirms a meaningful capability-margin paired-effect-size shift on three independent sources" — survives this confound.

**Does not defend:** independence of the three sources from one another (frontier-model leakage between SWE-bench/LiveCodeBench/MMLU-Pro is a separate concern, addressed in Limitations); the specific choice of [0.30, 0.70] over a narrower or wider band (separately addressed in robustness variant A); the choice of raw pass-rate Δ versus logit (separately addressed in variant E); or the choice of the registered n_margin floor of 8 (separately addressed in variant F).

## Audit anchor

Code: `gate-0.5/random-subset-null.py` (commit `23104aa`).
Registration: OSF Addendum-2, DOI 10.17605/OSF.IO/EKCUQ, registered 2026-04-26T21:20:20Z UTC.
DOI backfill into source: commit `7c71699`.
Result CSVs: `gate-0.5/random-subset-null/{swebench-verified,livecodebench,mmlu-pro}-{null,summary}.csv` (commit `4eac434`).
