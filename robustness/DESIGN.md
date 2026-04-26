---
project: Plimsoll
kind: post-hoc-sensitivity-design
gate: 0.5
osf_doi: 10.17605/OSF.IO/G9WFY
osf_addendum_doi: [TBD — to be filed before any A2 variant runs; backfilled to this file in a follow-up commit before execution]
status: design v3 (post-second-specialist-review, pre-execution)
created: 2026-04-26
revision: v3 — addresses convergent residuals from methodologist + skeptic + pre-reg-auditor second-pass review
---

# Plimsoll Gate 0.5 — Post-Hoc Sensitivity Pass (v3)

## Honest framing

This document specifies a **pre-specified post-hoc sensitivity analysis**, not a pre-registration. The OSF-registered analysis (DOI 10.17605/OSF.IO/G9WFY, timestamped 2026-04-26T18:18:39Z UTC, before any held-out data was pulled) is the load-bearing analysis. Three sources cleared with z-scores ≥ +230. *This document is being written and committed after those baseline numbers are known to the analyst* — that is an attestation, not a proof, and the commit-timestamp ordering is the only mechanical anchor.

The git-commit-before-execution discipline protects against post-hoc selection of *inputs to a pre-specified menu*; it does **not** protect against post-hoc selection of *the menu itself*. To address that gap, the variants below are split into two categories with different audit anchors:

- **Category A1: OSF-pre-registered sensitivities.** Listed by name in §4.2 of `pre-registration.md`. Git commit of this DESIGN.md plus subsequent run logs is sufficient audit anchor.
- **Category A2: Post-hoc additions.** *Not* listed in the OSF document. To be run only after filing an **OSF Addendum registration** (free, ~5 minutes; locks the variant menu before execution). The addendum DOI is the audit anchor for these.

## Variants to run

### A1 — OSF-pre-registered sensitivities (git anchor sufficient)

**C. LiveCodeBench `--no-dedup` sensitivity.** Re-run with `prep-livecodebench.py --no-dedup`. The registered regex was a no-op (deviation D4), so this run is expected to be identical to baseline. Confirms the regex no-op didn't silently change anything.

**D. SWE-bench `--exclude-no-logs` sensitivity.** Re-run with `prep-swebench.py --exclude-no-logs` (drop no_logs cells instead of treating as failure). Tests robustness to the conservative-failure convention.

### A2 — Post-hoc additions (REQUIRES OSF addendum DOI before execution)

All variants in this section require the OSF Addendum DOI to be filed and backfilled into this file's frontmatter before the run begins.

**A. Margin band sweep (all 3 sources).** Bands `{[0.25, 0.75], [0.30, 0.70] (registered baseline), [0.35, 0.65], [0.40, 0.60]}` — symmetric ±0.05 and ±0.10 around the registered band. The rule "symmetric ±0.05 and ±0.10 only" is locked in this v3; finer-resolution sweeps would inflate forking paths and are explicitly excluded.

**B. MMLU-Pro per-discipline (14 sub-analyses).** Re-run `analyze.py` separately on each of the 14 disciplines with null-baseline z computed per discipline. Cells where n_pairs < 50 (see §"Robustness criteria") are reported descriptive-only.

**E. Logit-space re-run.** SWE-bench Verified primary, re-run with success outcomes converted to logit scale via empirical-logit-with-continuity-correction (per Cox 1970): log((s + 0.5) / (1 − s + 0.5)) where s is per-task pass rate. Tests whether raw-pass-rate Δ vs. logit Δ produces meaningfully different m_b.

**F. Inclusion-threshold sweep.** Re-run all three sources at three threshold settings:
- `(≥10, ≥4)` — looser
- `(≥20, ≥8)` — registered baseline
- `(≥30, ≥15)` — stricter

**G. Null-baseline seed stability (Category A2 — varying the registered seed=42 is post-hoc).** Re-run `null-baseline.py` on SWE-bench Verified primary at 10 different RNG seeds (sweep `{0, 1, ..., 9}` plus the registered 42 for 11 total). Report z mean ± std across seeds.

**H. Audit-by-band sub-pass (Category A2).** For each margin band in A (4 bands), re-run `audit-reasoning-modes.py` against that band's empirically-computed m_b on LiveCodeBench. Report per band: how many of the 13 reasoning-mode pairs change verdict.

**I. Audit under logit (Category A2 — closes skeptic's "largest live attack").** Re-run `audit-reasoning-modes.py` with m_b computed from variant E's logit-space LiveCodeBench analysis (after running E on LiveCodeBench, not just SWE-bench). The audit's "11/13 fail" depends on m_b's *level*, not just its band-conditional value; logit could move m_b materially. Report the same SUBORDINATE / PAIR-UNSTABLE / ROBUST counts under logit-space m_b.

## Genuinely out of scope (deferred to future work, with stated reasons)

- **Per-benchmark-tuned bands.** Would require a principled tuning rule first (open question in parent README). Sweeping bands per-benchmark post-hoc would be p-hacking; explicitly *not* doing it.
- **Multi-step agent traces.** No data of this shape pulled; methodology extension required.
- **Effect-size scaling units beyond raw and logit** (probit, arcsine). Logit covers the IRT-natural alternative; probit/arcsine are monotone-equivalent for this purpose.
- **Scaffold-dedup variant on SWE-bench.** Running it would change the substantive question, not just the analysis convention. *Acknowledged inconsistency with variant D, which also changes a substantive convention (no_logs treatment) — D is in scope because the no_logs convention is mechanical (cell-level treatment of an absent record); scaffold-dedup is taxonomic (which agents count as distinct). The line is defensible but reasonable reviewers may disagree.*
- **Independence-of-sources concerns** (frontier-model leakage across SWE-bench/LiveCodeBench/MMLU-Pro). Analytic-choice sweeps cannot address shared-data exposure; this is a paper-level Limitations item, not a robustness-pass item.
- **External-validity domains** (RL, multimodal, agentic traces). Acknowledged as the most-contested settings for capability-margin filtering; out of scope for this gate, in scope for Gate 1+ design.

## Robustness criteria (pre-committed in this v3 design)

### Headline criterion: per-pair sign-flip rate (NEW — has actual power)

For each variant, compute the fraction of qualifying pairs whose paired effect size flips sign relative to the registered baseline:

> **flip_rate(variant) = #{pairs where sign(Δ_baseline) ≠ sign(Δ_variant)} / N_qualifying_pairs**

This is the load-bearing diagnostic. The verdict-survival check below has near-zero power to fail at the registered z-scores, so it is not load-bearing on its own; the per-pair sign-flip rate actually can fail and is the metric a peer reviewer should attack.

**Pre-committed thresholds:**
- flip_rate < 5%: variant is **stable**
- 5% ≤ flip_rate < 15%: variant is **mildly unstable** — reported in Limitations
- flip_rate ≥ 15%: variant is **destabilizing** — reported in headline alongside the variant name

### Verdict-survival (kept, but not load-bearing)

> **A variant "passes" if the source's CLEARS verdict (median |Δ| ≥ 0.05 AND null-baseline z ≥ 3 at α=0.001) survives unchanged from the registered baseline.**

The registered z-scores (+230, +375, +499) are so large that "passes" is essentially guaranteed for any reasonable variant — the null-baseline test has near-zero power to fail at this n. Verdict-survival is reported, but the per-pair sign-flip rate above is the primary diagnostic. Magnitude CI (95% percentile bootstrap on median |Δ| under the variant) is reported descriptively for completeness.

### Cell-level n_pairs floor (NEW — closes skeptic's n-collapse attack)

For each (source × variant) cell:
- **n_pairs ≥ 50:** cell contributes to pass/fail and to flip-rate aggregates.
- **n_pairs < 50:** cell is reported descriptively only (median |Δ|, n shown). It does **not** trigger pass, fail, or flip-rate verdicts. Narrative claims must not invoke these cells.

This guards against the [0.40, 0.60] band on SWE-bench shrinking the in-band pair count enough to make the 0.05 effect-size floor binding by chance.

### Layered Gate 0.5 verdict

- **Fully robust:** all three sources CLEAR under every variant **and** every cell has flip_rate < 5%.
- **Headline-stable:** SWE-bench (primary) CLEARS under every variant with flip_rate < 5%, but a secondary fails or shows flip_rate ≥ 5%. **Abstract claim drops from "three independent sources" to "one primary source plus two with [variant-specific] caveats."**
- **Fragile:** SWE-bench fails verdict-survival under any A1, A2, E, F, or G variant, **OR** SWE-bench flip_rate ≥ 15% under any variant.

The qualifier "reasonable variant" used in v2 is removed — all listed variants count.

## Failure protocol (pre-committed before execution)

| Outcome | Action |
|---|---|
| All variants pass on all 3 sources with flip_rate < 5% | Methodology paper proceeds with the layered-clear narrative; robustness section is one paragraph. |
| Any *secondary* source (LiveCodeBench or MMLU-Pro) fails verdict OR shows flip_rate ≥ 5% under ≥1 variant | Methodology paper proceeds with the **headline-stable** narrative. **Abstract is rewritten: "three independent sources" → "SWE-bench Verified plus two secondary sources with [variant-specific] caveats."** Failed/unstable variants reported by name in Limitations with their diagnostic numbers (flip_rate, median |Δ|, n_pairs). |
| **SWE-bench Verified (primary) fails verdict OR shows flip_rate ≥ 15% under any variant** | Methodology paper headline is rewritten: replace "Plimsoll Gate 0.5 confirms the capability-margin paired-effect-size shift on three independent sources" with the variant-specific qualified version. A public-corrigendum-shaped note is added to the OSF project before the paper preprints. |
| Variant H (audit-by-band): flip-count of the 13 reasoning-mode pairs changes by ≥2 across any band | Audit blog post is rewritten with **all four band-conditional numbers** ("X/13 fail at [0.25, 0.75]; Y/13 at [0.30, 0.70]; Z/13 at [0.35, 0.65]; W/13 at [0.40, 0.60]"). Single-number headline is dropped. *(No "most conservative" cherry-picking — all bands reported.)* |
| Variant I (audit under logit): SUBORDINATE count under logit-m_b differs from raw-m_b count by ≥2 pairs | Audit blog post must report both numbers ("11/13 under raw m_b; X/13 under logit m_b"). Single-number headline is dropped. |
| Variant G (seed stability): min(z) across 11 seeds < 100 on SWE-bench primary | Re-run all three null-baselines at n=10,000 perms (instead of registered n=1000) and report tightened CIs. *(Threshold is tied to an absolute floor near the α=0.001 cutoff, not to the arbitrary 5% std/mean ratio used in v2.)* |

This protocol is committed in this DESIGN.md *before* any variant is executed. Reframing post-hoc is not permitted; if a SWE-bench variant fails or destabilizes, the headline changes.

## Computational plan

| Variant | Cost (single-thread VPS, 2 cores available) |
|---|---|
| A. Margin sweep (3 sources × 3 new bands × analyze + null-baseline + sign-flip) | 9 analyze + 9 null-baseline (~5–15 min each) — parallelizable |
| B. MMLU-Pro per-discipline (14 with z + sign-flip) | 14 analyze + 14 small null-baselines (~30 min total) |
| C. LiveCodeBench `--no-dedup` | 1 prep + 1 analyze + 1 null-baseline (~15 min) |
| D. SWE-bench `--exclude-no-logs` | 1 prep + 1 analyze + 1 null-baseline (~25 min) |
| E. Logit-space SWE-bench + LiveCodeBench (logit needed on LCB for variant I) | 2 transforms + 2 analyze + 2 null-baseline (~50 min) |
| F. Inclusion-threshold sweep (3 sources × 2 new thresholds) | 6 analyze + 6 null-baseline (~60 min total) |
| G. Seed stability on SWE-bench × 11 seeds | 11 null-baselines (~3 hours sequential, or ~90 min on 2 cores) |
| H. Audit re-run at 4 bands | ~5 min |
| I. Audit under logit-space m_b | ~2 min (after E on LCB completes) |
| **Total wall clock** | **~5.5–6.5 hours on VPS** in tmux session `plimsoll-robust` |

## Output artifacts

- `gate-0.5/robustness/<source>/<variant>/` — analyze + null-baseline outputs per cell
- `gate-0.5/robustness/sign-flip-rates.csv` — per-variant per-source flip rate, n_qualifying_pairs
- `gate-0.5/robustness/audit-by-band/audit-band-*.csv` — variant H outputs
- `gate-0.5/robustness/audit-under-logit.csv` — variant I output
- `gate-0.5/robustness/seed-stability.csv` — 11-seed null-baseline z values
- `gate-0.5/robustness/all-variants.csv` — single summary table (verdict + flip_rate + median |Δ| + CI + n_pairs per cell)
- `gate-0.5/robustness/robustness-summary.md` — narrative summary

## Audit-trail and reproducibility

- DESIGN.md committed BEFORE any variant runs; commit SHA is the v3 design anchor.
- For Category A2 variants: OSF Addendum registration filed before execution; addendum DOI is backfilled to this file's frontmatter in a follow-up commit before step 3 of sequencing runs.
- VPS environment pinned at run start: `requirements.txt` SHA, Python version, `pip freeze` output, `uname -a` (OS/kernel), CPU arch, BLAS backend (`np.show_config()`), and the random source used (numpy default_rng vs legacy RandomState). The seed-stability variant G is the one most exposed to BLAS/CPU-arch differences; for variants A–F + H + I these are documented but not load-bearing.
- Each variant's analyze + null-baseline command is logged to `gate-0.5/robustness/run-log.txt` with timestamp.
- Substantive scope expansion is logged in `gate-0.5/addendum-post-hoc-sensitivity.md` (separate from `registration-deviations.md`, which is reserved for mechanical bug fixes).

## Sequencing

1. Commit this DESIGN.md v3 to public repo (audit anchor for design choices).
2. File OSF Addendum registration listing variants A, B, E, F, G, H, I.
3. **Backfill commit:** replace `osf_addendum_doi: [TBD ...]` in this file's frontmatter with the actual DOI; commit and push.
4. Run on VPS in tmux session `plimsoll-robust` per the computational plan.
5. Pull results.
6. Write `robustness-summary.md` per the failure-protocol decision tree.
7. Commit + push results.
8. Append `addendum-post-hoc-sensitivity.md` to repo.
