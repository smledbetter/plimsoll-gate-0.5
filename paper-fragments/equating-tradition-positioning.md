---
title: Methodology paper — equating-tradition positioning (draft)
status: draft, ready to merge into manuscript lit-review
intended_section: §Prior work / §Relation to psychometric equating tradition
date_compiled: 2026-04-26
verdict: NOVELTY-NARROWED
provenance: Spawned-agent literature review against Kolen & Brennan + Dorans/Holland line; web sources only
---

# Equating-tradition positioning — verdict and drop-in paragraph

This file captures a structured review of one specific objection to Plimsoll's central novelty claim, conducted against Kolen & Brennan (2014) *Test Equating, Scaling, and Linking* and adjacent psychometric equating literature.

## The objection (verbatim from domain-specialist swarm)

> "Rank stability vs. effect-size stability is not new. Test-equating literature distinguishes 'rank-preserving linkage' (concordance) from 'score-equivalent linkage' (equating proper); Kolen & Brennan formalize when each is defensible. Plimsoll's headline claim — rank stable but effect sizes unstable — is the equating-vs-concordance distinction restated."

## Verdict

**NOVELTY-NARROWED.** The equating tradition contains the *concept* the reviewer points to — and contains it more rigorously than the objection states — but does not contain Plimsoll's specific *operationalization* (per-pair |Δ paired effect size| over capability-margin-filtered AI benchmarks, with non-compensatory MIRT as the pre-registered generative anchor). The paper survives, but only with explicit citation of the equating literature and a tightened novelty claim. The headline "rank-stable but effect-size-unstable" framing as currently written invites exactly this reviewer to dismiss the paper.

## Evidence map

**A. Concordance vs. equating in K&B.** Real and central. K&B (3rd ed., 2014) summarize the Mislevy/Linn taxonomy — "equating, vertical scaling, concordance, projection, statistical moderation" — with equating as the strongest form, characterized by population invariance, equity, and symmetry; concordance as a weaker rank/distributional alignment that is *not* expected to be population-invariant. Treated explicitly in the early framing chapters and revisited in the linking chapter (Chs. 1 and 8 across editions, per the publisher and review summaries). Foundational: Mislevy (1992), Linn (1993), then Holland & Dorans's 4th-ed. *Educational Measurement* chapter (2006), which compresses the taxonomy into three classes — equating / scale aligning / predicting.

**B. Isomorphism check.** Partial, not full. The equating tradition's distinction is between *kinds of linkage* (a property of a function joining two test scales for a population). Plimsoll's distinction is between *kinds of stability of a comparison* (rank order of two models vs. magnitude of their paired effect size, across slices of a fixed benchmark). These are adjacent but not identical: K&B treat the *function* as the object whose invariance fails; Plimsoll treats the *paired-effect-size statistic* as the object whose invariance fails. The reviewer is correct that the *spirit* is the same; they overstate when calling it a restatement.

**C. Per-pair |Δ effect size| diagnostic.** The closest precedent is the Dorans–Holland (2000) RMSD and REMSD family — root-mean-square (or root-expected-mean-square) difference between subpopulation linking functions and the total-population function, *standardized by σ* and judged against Dorans & Feigenbaum's "differences that matter" (DTM) threshold. This is materially close to Plimsoll's m_b: both are root-or-median |Δ| of a standardized function across slices, judged against a practical threshold. Two real differences: (i) RMSD slices over examinee subpopulations on a fixed test pair; m_b slices over task-pair samples for a fixed model pair on a fixed benchmark; (ii) RMSD measures equating-function deviation; m_b measures Cohen's-d–style paired effect-size deviation. Same statistical genre, different unit of analysis.

**D. [0.30, 0.70] capability-margin band.** Already in the AI-benchmarking psychometrics literature as the "Mid-Range Difficulty Filter," explicitly justified by Fisher information / TIF. It is the applied default for Fisher-information item selection (item information peaks where p ≈ 0.5; 0.3–0.7 is one logit either side). The capability-margin band is *not novel* as a band; it is a sensible operational default with a long IRT pedigree. Plimsoll's contribution here is using it as a *pre-registered selection filter for a stability statistic*, not as a CAT item-selection rule.

**E. Non-compensatory MIRT as generative model for paired-effect-size instability.** Genuinely thin in the equating tradition. Multidimensionality is acknowledged as a *threat* to invariance (van der Linden and others); compensatory-vs-noncompensatory distinctions are well known in MIRT; but the agent did not find an equating-tradition paper that pre-registers non-compensatory MIRT as the *theoretical signature explaining paired-effect-size instability* on real benchmarks, then runs a power contrast against compensatory MIRT. **This is the strongest residual of novelty.**

**F. Adjacent threats.** The single closest non-K&B threat is Dorans & Holland (2000) plus Dorans (2004) "Equating, Concordance, and Expectation" — these together carry the conceptual load of the objection. Holland & Wainer (1993) *DIF* and Penfield & Camilli's *Educational Measurement* 4th-ed. DIF chapter are adjacent but more item-level. Within AI evaluation, Polo et al. and the Ai2 Fluid Benchmarking line are the closest contemporary work but cite *neither* Kolen & Brennan nor Dorans/Holland — so Plimsoll citing them is itself a contribution to the AI-eval literature's grounding.

## Specifically novel residuals (regardless of verdict)

1. **Unit of analysis:** per-pair-of-models, per-task-sample, on AI benchmarks, rather than per-pair-of-subpopulations on a fixed test-pair.
2. **m_b as a *median* (not RMS)** of paired |Δ Cohen's d|, paired with a pre-registered null-baseline z and TOST/Bayesian-equivalence discipline.
3. **Non-compensatory MIRT pre-registered as a power-contrast generative model** — compensatory power 0.000 is a real falsifiable commitment.
4. **The "subordinate-to-shift" applied audit** (11/13 reasoning-mode lift claims smaller than the benchmark's m_b) is a novel use of the equating-tradition machinery as a *decision rule for reading published claims*. No precedent located.

## Must-cite items (precise list)

- Kolen, M. J., & Brennan, R. L. (2014). *Test Equating, Scaling, and Linking* (3rd ed.). Springer. — Chapter 1 (linking categories) and Chapter 8 (concordance/linking).
- Holland, P. W., & Dorans, N. J. (2006). Linking and equating. In R. L. Brennan (Ed.), *Educational Measurement* (4th ed., Ch. 6). ACE/Praeger.
- Dorans, N. J., & Holland, P. W. (2000). Population invariance and the equatability of tests: Basic theory and the linear case. *Journal of Educational Measurement*, 37(4), 281–306. (Source of RMSD.)
- Dorans, N. J. (2004). Equating, concordance, and expectation. *Applied Psychological Measurement*, 28(4), 227–246.
- von Davier, A. A., Holland, P. W., & Thayer, D. T. (2004). *The Kernel Method of Test Equating*. Springer. (Subpopulation invariance treatment.)
- Holland, P. W., & Wainer, H. (Eds.) (1993). *Differential Item Functioning*. Erlbaum.
- Penfield, R. D., & Camilli, G. (2007). DIF and item bias. In *Educational Measurement* (4th ed.).
- For the capability-margin band: any IRT/TIF source (Lord 1980; Hambleton & Swaminathan) plus the AI-eval Mid-Range Difficulty Filter precedent.

## Drop-in lit-review paragraph (drop into manuscript as-is)

> The distinction between rank-preserving and magnitude-preserving comparisons has a long psychometric pedigree. Mislevy (1992), Linn (1993), and Kolen & Brennan (2014, Chs. 1, 8) treat equating, concordance, and prediction as graded forms of linkage with different invariance requirements; Holland & Dorans (2006) re-state the taxonomy. The diagnostic family closest to ours is the standardized root-mean-square difference of equating functions across subpopulations introduced by Dorans & Holland (2000), refined by Dorans (2004), and extended by von Davier, Holland & Thayer (2004), evaluated against the "differences that matter" threshold of Dorans & Feigenbaum (1994). We claim no novelty in observing that rank linkage and effect-size linkage are different objects. Our contribution is to import this distinction into AI benchmark evaluation, to define m_b as the median paired effect-size shift over capability-margin-filtered task samples (a per-model-pair analogue of Dorans–Holland RMSD), to anchor it in non-compensatory MIRT as a pre-registered generative signature, and to demonstrate that a substantial fraction of published reasoning-mode lift claims are subordinate to it.

## Web sources (agent retrieval)

- [Kolen & Brennan (2014) — Psychometrika review (Cambridge Core)](https://www.cambridge.org/core/journals/psychometrika/article/abs/m-j-kolen-r-l-brennan-2014-test-equating-scaling-and-linking-methods-and-practices-third-edition-new-york-springer-566-pages-us14900-isbn-9781493903160/261F76DE49AFE7D679717251A31EB38A)
- [Dorans & Holland (2000), Population invariance — JEM](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1745-3984.2000.tb01088.x)
- [Dorans (2004), Equating, Concordance, Expectation — APM](https://journals.sagepub.com/doi/abs/10.1177/0146621604265031)
- [von Davier (2006), Subpopulation invariance — ETS RR](https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/j.2333-8504.2006.tb02031.x)
- [SEAsic R package — RMSD/REMSD definitions](https://rdrr.io/cran/SEAsic/man/rmsd.html)
- [The Invariance of Latent and Observed Linking Functions (multidimensionality)](https://files.eric.ed.gov/fulltext/EJ1109307.pdf)
- [Dynamical Non-compensatory MIRT — Psychometrika](https://link.springer.com/article/10.1007/s11336-023-09903-y)
- [Mid-Range Difficulty Filter / IRT in AI benchmarking](https://arxiv.org/html/2603.23749)
- [Holland & Wainer (1993) Differential Item Functioning — Routledge](https://www.routledge.com/Differential-Item-Functioning/Holland-Wainer/p/book/9781138967694)
- [Dorans (2003), Population Invariance of Score Linking — ETS RR](https://onlinelibrary.wiley.com/doi/10.1002/j.2333-8504.2003.tb01919.x)
