---
title: Methodology paper — construct-validity positioning (draft)
status: draft, ready to merge into manuscript Discussion / Limitations
intended_section: §Discussion subsection on construct validity, plus §Limitations paragraph
date_compiled: 2026-04-26
verdict: VALIDITY-CABINED
provenance: Spawned-agent literature review against Cronbach-Meehl, Messick, Raji 2021, REFORMS, BetterBench, METR elicitation-gap, domain-specific CV work; web sources only
companion: equating-tradition-positioning.md (verdict NOVELTY-NARROWED — converges on same paper structure)
---

# Construct-validity positioning — verdict and drop-in paragraph

This file captures a structured review of one specific objection to Plimsoll's contribution claim, conducted against the construct-validity literature and AI-eval-specific construct-validity work.

## The objection (from the domain-specialist swarm + severity stack-rank)

> "Construct-validity gap. Cyber: 'solves a CTF ≠ executes a real intrusion.' Medical: 'MedQA accuracy ≠ patient outcomes.' SWE: 'leaderboard m_b ≠ deployed-traffic value.' Plimsoll makes benchmark claims more rigorous without making them more *valid*. You've built a more accurate ruler for measuring shadows. Plimsoll governs claim survival, not validity. The honest framing limits the paper's reach to 'within-benchmark discipline,' which is fine, but reduces the why-now urgency."

## Verdict

**VALIDITY-CABINED.** The construct-validity gap is real and acknowledged across the AI-eval methodology literature, but it does not sink Plimsoll. Standard practice in measurement-science methodology papers (REFORMS, Bowman & Dahl 2021, the medical-construct-validity literature, METR's elicitation-gap protocol) is to cabin construct validity as a separate accumulation of evidence. Plimsoll survives an explicit, technically-precise cabin paragraph plus a single re-framing move: positioning the audit-as-decision-rule as a *prerequisite filter* for downstream construct-validity work, not a competitor to it. Without that move, the paper sits closer to VALIDITY-DOOMED for applied-domain reviewers; with it, the objection actually strengthens the contribution.

## Evidence map

**A. Cronbach & Meehl 1955 / Messick 1989 requirements.** Cronbach & Meehl require that construct validity be evidenced through a "nomological network" — an ongoing accumulation linking the theoretical construct to observables; they treat any single study as one link in that net, not the whole net. Messick 1989 is even more permissive on scope but stricter on disclosure: validity is a "unified concept" with content, substantive, structural, generalizability, external, and consequential aspects, and "validity is an ongoing activity that relies on multiple evidence sources." Neither requires a single methodology paper to discharge construct validity end-to-end. They require that the paper *name what aspect it is contributing evidence on* and not overclaim transfer to other aspects. A scope-cabin of the form "m_b is structural/internal evidence; generalizability and consequential validity are separate work" is defensible under both frameworks — provided Plimsoll does not assert deployment-relevance.

**B. Scope-cabined construct validity is standard methodology-paper practice.** REFORMS (Kapoor, Narayanan et al., *Science Advances* 2024) explicitly distinguishes "outcome variable" from "theoretical construct" and requires authors to "describe precisely how their outcome variable is measured, and note any ways in which this outcome variable might not align with the associated construct." REFORMS itself does not solve construct validity — it cabins the disclosure obligation. BetterBench (Reuel et al., NeurIPS 2024 Spotlight) evaluates 24 benchmarks against 46 lifecycle criteria and treats construct validity as one *parallel* dimension among many, not a prerequisite that voids the rest of the framework. Bowman & Dahl 2021 lay out four NLU benchmark criteria of which construct validity is one; their paper is fundamentally a *methodology critique* and does not itself supply a full nomological net.

**C. AI-eval construct-validity literature treats CV as parallel, not gating.** Raji et al. 2021 ("AI and the Everything in the Whole Wide World Benchmark") attacks *generality claims*, not statistical-rigor claims. Their critique: benchmarks "cannot possibly capture anything representative of the claims to general applicability being made about them" and "do not measure what they claim to measure...especially troublesome when benchmarks promise to measure universal or general capabilities." The objection lands on papers that *over-claim*; it is silent on papers that explicitly cabin. The recent "Measuring what Matters" (NeurIPS 2025, building on Subramonian et al.) reviewed 445 articles and proposes an operational checklist for establishing construct validity in *new* benchmarks — again, a parallel infrastructure, not a deletion criterion for benchmark-internal methodology work.

**D. Domain-specific predictive-validity status.**

- *Cyber*: Singer et al. 2025 demonstrate the disconnect between CTF score and deployment risk with a concrete case where capability eval showed "~90% compliance and ~50% accuracy" yet the threat-modeled conclusion was "this method of misuse does not currently present a high-risk scenario," and explicitly write that "evaluating LLM cybersecurity risk requires more than just measuring model capabilities." This is a *gap finding*, not a methodology indictment of benchmark work.
- *Medical*: Hager-style position pieces report that "correctly answering benchmark questions does not strongly predict real-world clinical performance" with α ≈ 0.45 between MedQA and EHR outcomes. The paper *requires* benchmark-internal statistics to compute its α — i.e., construct-validity work depends on benchmark-internal rigor as input.
- *Safety/dangerous-capability*: METR's elicitation-gap work treats benchmark-internal scores as *lower bounds* requiring an explicit safety margin for post-training enhancement. The protocol assumes benchmark-internal stability and pushes validity work into a separate elicitation/safety-margin layer.

No retrieved source claims that benchmark-internal rigor *predicts* deployment outcomes. None claim that absence of construct-validity work *invalidates* benchmark-internal methodology contributions. The literature treats them as orthogonal axes.

**E. Strongest steelman of "this objection sinks the paper."** A more accurate ruler for measuring shadows is still a ruler for shadows. If the audit-as-decision-rule causes practitioners to *retain* lift claims that survive m_b filtering, those surviving claims still face an unaddressed deployment-validity gap. Practitioners may treat "passes Plimsoll audit" as a green light. Raji et al. 2021's critique of generality claims applies recursively: a more rigorous within-benchmark diagnostic could *amplify* the very over-claiming pattern Raji warns against, by laundering benchmark-internal stability as a proxy for real-world relevance. The strongest version of the objection is not "Plimsoll is wrong" but "Plimsoll's success could be misread as a validity certification."

**F. Does the audit defuse or worsen the CV problem?** It defuses, conditionally. Construct-validity work *requires* a stable signal as input — every empirical CV procedure (REFORMS-style outcome correlation, MedQA-vs-EHR α, METR safety-margin) takes benchmark scores as a measurement and asks whether they predict an external criterion. If the benchmark-internal signal is unstable across paired-effect comparisons (the Plimsoll finding on LiveCodeBench: 11 of 13 lift claims subordinate to shift), then any CV correlation is contaminated by within-benchmark noise. Plimsoll's audit removes that contamination upstream. This is methodologically analogous to reliability being a precondition for validity in classical test theory: you cannot validate what you cannot reliably measure. The risk in (E) is real but addressable with explicit framing.

## Specifically what Plimsoll must add to defuse this objection

1. **Abstract**: One sentence cabin-and-link. Not "limitation" tone; positioning tone. Place after the m_b definition and before audit results.
2. **§Discussion** (new short subsection, ~150 words): "Construct validity and the role of benchmark-internal stability." Names the cabin under Cronbach-Meehl/Messick; cites Raji 2021, REFORMS, BetterBench; positions m_b as reliability-class evidence that is a *precondition* for downstream validity work, not a substitute. Cites METR elicitation gap as the parallel safety-margin tradition.
3. **§Limitations**: Single paragraph explicitly disclaiming generalization to deployment outcomes in cyber, medical, safety domains; cites Singer et al. 2025 (cyber) and Hager-style medical CV work as exemplars of the parallel work the audit *enables* but does not *perform*.
4. **No change to results, methods, or claim structure.** The cabin is rhetorical and positional, not technical.

## Drop-in paragraph for the paper (drop into Discussion or Limitations as-is)

> Plimsoll governs claim survival on a benchmark, not the construct validity of that benchmark for any deployment domain. We adopt the standard scope-cabin used across measurement-science methodology papers (Cronbach & Meehl, 1955; Messick, 1989; Kapoor et al., 2024): m_b and the subordinate-to-shift audit constitute structural-validity evidence — they characterize whether a published paired-effect lift is stable against the benchmark's own capability-margin geometry. They do not, and are not designed to, certify that benchmark performance predicts real-world outcomes such as executed intrusions, patient-level diagnostic accuracy, or production code defects. We treat construct-validity work in those domains (e.g., the elicitation-gap and safety-margin tradition for dangerous-capability evaluation; benchmark-vs-EHR correlation studies in medical AI; threat-modeled risk assessment in cyber) as parallel and complementary. The audit's contribution to that downstream work is upstream noise reduction: a lift claim that fails m_b filtering should not be passed forward into a construct-validity argument, because its benchmark-internal signal is not stable enough to anchor an external criterion correlation.

## Cross-reference to equating-tradition positioning

The construct-validity verdict **reinforces** the K&B novelty-narrowed positioning. The equating tradition (Kolen & Brennan; Dorans & Holland) is itself an internal-rigor tradition whose outputs feed validity work downstream — exactly the relationship this verdict prescribes. Both reviews converge on the same paper structure: borrow the rigor-mathematics from a mature measurement tradition, foreground the two genuine residuals (non-compensatory MIRT signature; subordinate-to-shift audit), cabin construct validity as parallel, and position the audit as a precondition that *makes* construct-validity work tractable rather than competing with it. The two verdicts are mutually compatible and jointly suggest the paper's "why now" should be framed as *enabling* the applied-domain validity programs already in motion (METR, MedHELM, REFORMS), not displacing them.

## Web sources (agent retrieval)

- [Cronbach & Meehl 1955](https://psychclassics.yorku.ca/Cronbach/construct.htm)
- [Messick 1989 chapter summary, SAGE](https://uk.sagepub.com/sites/default/files/upm-assets/121284_book_item_121284.pdf)
- [Raji et al. 2021](https://arxiv.org/abs/2111.15366)
- [REFORMS, Science Advances 2024](https://www.science.org/doi/10.1126/sciadv.adk3452)
- [BetterBench, NeurIPS 2024](https://arxiv.org/abs/2411.12990)
- [Bowman & Dahl 2021](https://aclanthology.org/2021.naacl-main.385/)
- [Measuring what Matters, NeurIPS 2025](https://openreview.net/pdf?id=mdA5lVvNcU)
- [Medical LLM Construct Validity, arXiv 2503.10694](https://arxiv.org/html/2503.10694v1)
- [LLM Cyber Evals Don't Capture Real-World Risk, arXiv 2502.00072](https://arxiv.org/html/2502.00072v1)
- [METR elicitation gap](https://metr.github.io/autonomy-evals-guide/elicitation-gap/)
- [AISI capability elicitation protocol](https://www.aisi.gov.uk/blog/our-approach-to-ai-capability-elicitation)
- [Conjointly nomological network reference](https://conjointly.com/kb/nomological-network/)
