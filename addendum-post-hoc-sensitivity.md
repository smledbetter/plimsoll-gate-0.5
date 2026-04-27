---
project: Plimsoll
kind: addendum-post-hoc-sensitivity
gate: 0.5
osf_doi: 10.17605/OSF.IO/G9WFY
osf_addendum_doi: 10.17605/OSF.IO/3PD2A
osf_random_subset_doi: 10.17605/OSF.IO/EKCUQ
created: 2026-04-27
parent_design: robustness/DESIGN.md (v3, commit 33a2d84)
status: complete — robustness pass executed; verdict HEADLINE-STABLE
---

# Plimsoll Gate 0.5 — Post-Hoc Sensitivity Addendum

This file is a parallel of `registration-deviations.md`, covering substantive scope expansions (additional sensitivity analyses) rather than mechanical bug fixes. The robustness pass was a *pre-specified post-hoc sensitivity analysis*, not a pre-registration: its load-bearing audit anchor is the OSF Addendum-1 registration ([DOI 10.17605/OSF.IO/3PD2A](https://doi.org/10.17605/OSF.IO/3PD2A), registered 2026-04-26T20:20:26Z UTC), the git commit of `robustness/DESIGN.md` v3 at SHA `33a2d84`, and the subsequent run logs. This addendum documents *what was added*, *why*, and *how the protocol's audit discipline was preserved*.

The OSF-registered Gate 0.5 analysis (DOI [10.17605/OSF.IO/G9WFY](https://doi.org/10.17605/OSF.IO/G9WFY), 2026-04-26T18:18:39Z UTC) is the load-bearing analysis. Three sources cleared on the registered headline at z = +362.6 / +374.9 / +498.8. The robustness variants below test analytic-choice perturbations *around* that registered analysis — they cannot, and do not, replace it.

## Variants added by Addendum-1 (DOI 10.17605/OSF.IO/3PD2A)

Addendum-1 listed by name, before any held-out variant ran:

- **A.** Margin band sweep (3 sources × 3 new bands = 9 cells).
- **B.** MMLU-Pro per-discipline (14 sub-analyses).
- **E.** Logit-space scale on SWE-bench Verified and LiveCodeBench.
- **F.** Inclusion-threshold sweep (3 sources × 2 thresholds = 6 cells).
- **G.** Null-baseline seed stability on SWE-bench (11 seeds).
- **H.** Audit-by-band on LiveCodeBench (4 bands).
- **I.** Audit under logit-space m_b on LiveCodeBench.

Variants C and D were already named in the registered §4.2 sensitivities; they are git-commit-anchored under the parent registration (G9WFY).

## Variant added by Addendum-2 (DOI 10.17605/OSF.IO/EKCUQ)

Addendum-2 added a **random-subset null-baseline** test: under the null that the capability-margin filter has no preferential effect on |Δ paired effect size|, replacing the margin-conditional subset with a random subset of equal size should produce comparable median |Δ|. The test rejects this null on all three sources at z = +434.4 (SWE-bench), +482.8 (LiveCodeBench), +581.0 (MMLU-Pro). Defended against the most natural skeptical attack ("you'd see a similar shift if you took any 30% subset"). Scripts and results in `random-subset-null/`.

## Why these are post-hoc and not part of the parent registration

The parent registration's §4.2 listed substantive sensitivities (the registered band of 0.30 ± 0.05 and 0.30 ± 0.10 plus C and D). Variants A, B, E, F, G, H, I extend that menu with additional perturbations identified during the methodology paper drafting process — *after* the registered analysis was specified but *before* any held-out variant was executed. The git-commit-before-execution discipline of `DESIGN.md` v3 protects against post-hoc selection of inputs to the menu (the variant inputs were all available at design time and the design fixed them); it does *not* by itself protect against post-hoc selection of the menu. To address that gap, OSF Addendum-1 was registered before the A2 variants ran, locking the variant menu and the failure protocol.

This is the same discipline the parent registration applied to the substantive analysis: register before you pull held-out data, then commit your decision rule mechanically.

## Failure protocol — pre-committed in DESIGN.md v3

Reproduced here for self-containment. The protocol fired none of its escalation triggers on the executed pass:

| Pre-committed trigger | Was it triggered? |
|---|---|
| Variant H flip-count change ≥ 2 from baseline (across any band) | **No** — max delta = 1 (10, 11-baseline, 12, 12) |
| Variant I logit-m_b SUBORDINATE count differs from raw by ≥ 2 | **No** — corrected logit count is 12/13 vs raw 11/13, delta = 1 |
| Variant G min(z) across 11 seeds < 100 on SWE-bench primary | **No** — min z = +217.94 |
| SWE-bench (primary) verdict-survival fail OR flip_rate ≥ 15% under any variant | **No** — all SWE variants flip < 5% (max 4.05% at band 0.40-0.60) |
| Any *secondary* source verdict-fail OR flip_rate ≥ 5% under ≥ 1 variant | **Yes** (variant B per-discipline on MMLU-Pro: 10 of 14 disciplines show flip_rate 5-10%). Triggers HEADLINE-STABLE narrative per protocol. |

Per the protocol, the methodology paper's headline framing remains "three independent sources" because verdict-survival holds in every cell. The MMLU-Pro per-discipline flip rates are reported in §Limitations as discipline-level heterogeneity in the underlying signal, not as instability of the source verdict — every discipline still passes m_b ≥ 0.05 AND z ≥ 3 with the smallest discipline z = +63.51 (history) and the smallest discipline median |Δ| = 0.064 (engineering).

## What is *not* in scope of this addendum

Per DESIGN.md v3 §"Genuinely out of scope" — explicitly excluded from the variant menu, with stated reasons:

- Per-benchmark-tuned bands (would require a principled tuning rule first; sweeping bands per-benchmark post-hoc would be p-hacking).
- Multi-step agent traces (no data of this shape pulled).
- Effect-size scaling units beyond raw and logit (probit, arcsine — monotone-equivalent for this purpose).
- Scaffold-dedup variant on SWE-bench (changes the substantive question, not the analysis convention).
- Independence-of-sources concerns (frontier-model leakage across SWE/LCB/MMLU — analytic-choice sweeps cannot address shared-data exposure; this is a paper-level Limitations item, not a robustness-pass item).
- External-validity domains (RL, multimodal, agentic traces — out of scope for this gate).

## Exploratory follow-up files (NOT part of this addendum)

Two `gate-0-followup/` analyses are exploratory texture for §Discussion and are *not* registered confirmatory tests. They are anchored to the same git commit as `DESIGN.md` v3, and their output files ship alongside the robustness pass:

- `gate-0-followup/protocol-stratified.md` — temporal stratification by release-era. Provides post-hoc cross-validation that the registered pooled-source m_b is not era-driven.
- `gate-0-followup/pair-stratification.md` — stratification of paired effects by `|effect_full|` quartile (ability-gap proxy). Reveals that pooled m_b is dominated by larger-gap quartiles; the audit's headline number is sensitive to which quartile-conditional m_b is used as the comparator. Motivates a candidate Addendum-3 (Q-conditional m_b operational rule + cross-benchmark verdict consistency + magnitude-of-audit-revision metric).

These files are clearly marked as exploratory and do not feed the Gate 0.5 verdict. They exist to inform §Discussion of the methodology paper and to motivate Gate 1 study designs.

## Reproducibility

- Per-variant output: `robustness/<variant>/{summary,null,flip-rate,pairs}.csv`
- Per-variant audit (where applicable): `robustness/<variant>/audit.csv`
- Aggregate narrative: `robustness/robustness-summary.md`
- Run log: `robustness/run-log.txt`
- Environment: `robustness/environment.txt`
- Random-subset null: `random-subset-null/<source>-{null,summary}.csv` plus `random-subset-null.py`
- Pair-stratification (exploratory): `gate-0-followup/pair-stratification.{py,csv,md}`
- Protocol-stratified (exploratory): `gate-0-followup/protocol-stratified.{py,csv,md}`

All outputs are committed to the public GitHub repository at the bundled-push commit (see commit log accompanying this file).
