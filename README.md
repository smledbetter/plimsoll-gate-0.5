---
project: Plimsoll
kind: gate-artifact
status: design
gate: 0.5
verdict: pending
updated: 2026-04-26
---

# Plimsoll Gate 0.5 — Independent Replication & Prospective Power Analysis

**OSF pre-registration: [10.17605/OSF.IO/G9WFY](https://doi.org/10.17605/OSF.IO/G9WFY)** (registered 2026-04-26T18:18:39Z UTC).
- Registration: https://osf.io/g9wfy/
- Project (16 frozen artifacts): https://osf.io/e264j/
- Schema: OSF Preregistration v4

## Purpose

Gate 0 cleared on a post-hoc analysis of Ndzomga's published heatmap — a single dataset the analyst had already seen. The 2026-04-25 Study Gate review surfaced this as a recursive-consistency failure: Gate 0 violates Plimsoll protocol elements 3 (pre-registration) and 5 (power analysis). The original Study Gate Change 2 (post-hoc OSF re-registration of Gate 0) addressed element 3 weakly and didn't fix element 5 or the single-dataset risk at all.

Gate 0.5 replaces Change 2. It converts the Plimsoll headline from *exploratory motivation on a single dataset* into *prospectively pre-registered, independently confirmed on held-out data, with a power analysis that satisfies element 5 the orthodox way*. After Gate 0.5 clears, the methodology paper rests on Gate 0.5 — Gate 0 stays in the paper as the analysis that surfaced the headline, explicitly labeled as exploratory.

## Decision rule (kill criterion)

Three sources, layered decision rule. The clearance criterion per source is the same: **median |Δ| ≥ 0.05 AND null-baseline z ≥ 3** (one-sided, observed ≥ null). Failure is the inverse: median |Δ| < 0.05 OR null-baseline z < 3.

| Source | Role | Effect of failure |
|---|---|---|
| Full SWE-bench Verified (`swe-bench/experiments`) | **Primary** — closest structural analog to Gate 0's design | Hard kill. If the primary fails, Gate 0.5 fails outright; paper does not ship as currently framed. |
| LiveCodeBench (`LiveCodeBench/submissions`) | **Confirmatory secondary — code domain** | Soft. If primary clears but LiveCodeBench fails, narrate honestly: instability is real on agentic code but does not generalize to competitive programming. Paper retains the agentic-code claim but loses the within-code-generalization story. |
| MMLU-Pro (`TIGER-AI-Lab/MMLU-Pro/eval_results`) | **Confirmatory secondary — scope expansion** | Soft. If primary + LiveCodeBench clear but MMLU-Pro fails, retreat to "Plimsoll for code-eval" framing with MMLU-Pro reported as an honest non-replication and discussion of domain specificity. The two-code-source result still establishes the existential claim with prospective discipline. |

**Dominant outcome paths:**
1. All three clear → headline: "instability replicates on three independent held-out sources spanning agentic code, competitive programming, and multiple-choice multi-discipline knowledge." Plimsoll proceeds with maximum scope.
2. Primary + LiveCodeBench clear; MMLU-Pro fails → headline: "instability replicates across two independent code-eval sources; behavior on multiple-choice multi-discipline knowledge differs, suggesting domain specificity worth investigating in future work." Plimsoll proceeds as code-eval methodology with honest scope qualifier.
3. Primary clears alone → headline: "instability confirmed on SWE-bench Verified prospectively; secondary replications did not clear." Plimsoll proceeds with single-source prospective confirmation; two non-replications discussed as future-work questions.
4. Primary fails → Gate 0.5 fails. Paper does not ship as currently framed.

Per-benchmark texture and per-source statistics are always reported, regardless of outcome path.

## Three components

Components A and B can run in parallel; both block C.

### Component A — Simulation-based power analysis

**Goal.** Compute the minimum detectable effect (MDE) for median |Δ| as a function of (N pairs, M tasks, signal strength, generative-model assumption). Pre-register parameters before running.

**Generative models to sweep.**
1. **Rasch / 1PL IRT** — single ability θ, single difficulty β; P(success) = σ(θ − β). Predicts median |Δ| ≈ 0 under capability-margin filtering. Acts as the null model.
2. **Compensatory MIRT (d = 2, 3, 5)** — agents have skill vectors θ ∈ R^d; tasks have skill loadings α; P(success) = σ(θ · α − β). Skills can substitute.
3. **Non-compensatory MIRT (d = 2, 3, 5)** — P(success) = ∏_k σ(θ_k − β_k). Every demanded skill must independently clear its bar. Plausibly closer to multi-step agent benchmarks where any required sub-capability failing collapses the task.

**Outputs.**
- MDE table: rows = (N, M); columns = (model, signal strength); cells = median |Δ| under H1 needed for 80% power at α = 0.001.
- Plot: simulated median |Δ| vs. signal strength, faceted by generative family.
- Statement: *given the chosen held-out source's actual N and M, what observed median |Δ| corresponds to which true effect size under each generative model?*

**Theoretical-anchor opportunity.** If MIRT generatively reproduces the observed median |Δ| ≈ 0.09 with realistic parameters (e.g. d = 3, moderate skill heterogeneity), Plimsoll has a theoretical claim: effect-size instability under capability-margin filtering is structural, not contingent — any multi-skill benchmark exhibits it. That upgrades the paper from "we found this on Ndzomga's data" to "this is what falls out of multidimensional skill structure under scalar-difficulty filtering." Stronger claim; pushes Plimsoll closer to Habba 2026's IRT line of work.

**Frozen artifacts.** `gate-0.5/simulation.py` with hardcoded numpy seed; outputs as CSVs. Source pinned at OSF registration time.

### Component B — Held-out leaderboard inventory ✅ COMPLETE

**Status:** Complete 2026-04-26. Initial inventory in `gate-0.5/inventory.md` covered seven candidate clusters; supplemental fan-out in `gate-0.5/inventory-supplement/` (NL2SQL, math/reasoning, code-non-SWE, UNCERTAIN resolution) confirmed two strong replacements for the originally-recommended METR Time Horizon secondary.

**Three sources selected:**

1. **Primary — Full SWE-bench Verified** via `swe-bench/experiments` (134 submissions × 500 instances, per-instance pass/fail in each submission's `results/results.json`). Ndzomga's mini covered only ~2% of cells, so ~98% is held-out. License: no LICENSE file (mitigation: confirmation email to Princeton NLP / John Yang before OSF registration).
2. **Confirmatory secondary (code) — LiveCodeBench** via `LiveCodeBench/submissions` (73 model directories, ≥50 distinct after dedup, 1055 questions across Codeforces / LeetCode / AtCoder, per-submission `Scenario.codegeneration_*_eval_all.json` with `graded_list[bool]`). Built-in difficulty labels (easy/medium/hard) enable a sensitivity analysis against the data-driven [0.30, 0.70] band. License: MIT — clean. Double-confirmed by independent agent runs.
3. **Confirmatory secondary (scope) — MMLU-Pro** via `TIGER-AI-Lab/MMLU-Pro/eval_results` (48 model-output ZIPs, 12,032 questions across 14 disciplines, per-question `pred` / `answer` fields → pass/fail = `pred == answer`). License: Apache-2.0 (code) + MIT (dataset) — clean. Multiple-choice grading is unambiguous, no `no_logs` edge case. 14 disciplines naturally support the MIRT theoretical anchor in Component A.

**Why these three:**
- Maximum independent-source diversity: agentic code-patching → competitive programming → multiple-choice multi-discipline knowledge. If the headline replicates across all three, Plimsoll's claim is dramatically stronger than single-source.
- Asymmetric fallback per the layered decision rule above: a code-only outcome (SWE-bench + LiveCodeBench) is still a publishable two-source replication if MMLU-Pro fails.
- All three pass the "not previously analyzed by the analyst" check (Pine Curtain validation sets HumanEval+/MBPP+ surfaced in supplemental inventory and were excluded; BIRD-SQL excluded; Aider polyglot excluded as Scoop Sprint 8 anchor).

**Sources rejected:**
- METR Time Horizon: superseded by MMLU-Pro and LiveCodeBench (strictly dominated on power, license, and political position).
- BFCL: narrow domain works against MIRT theoretical anchor; held as tertiary fallback.
- HELM Capabilities: 22 models with engineering cost to join predictions + gold; held as secondary fallback if either MMLU-Pro or LiveCodeBench data fetch hits unforeseen blockers.
- All NL2SQL candidates: structurally disqualified — NL2SQL leaderboards in 2026 universally treat per-question pass/fail as private submission artifacts.
- HELM Agents: confirmed not to exist as a separable artifact.
- WebArena, AgentBench: no per-instance data.
- OSWorld: still UNCERTAIN; not pursued.

### Component C — Prospective replication

**Three replications, shared analysis pipeline.** One pipeline applied to three sources independently. Per-source preprocessing differs (see notes below); per-source analysis is identical.

**Frozen analysis plan (per source).** Same statistic, exclusions, decision rule as Gate 0:
- Pairwise effect = mean per-task score difference between agents/models A and B over qualifying tasks.
- Margin band: difficulty ∈ [0.30, 0.70] (difficulty = mean Success across all agents/models on the task).
- Min thresholds: 20 shared tasks (full), 8 shared tasks (margin).
- Headline statistics: Spearman ρ, median |Δ|, p95 |Δ|, sign-flip rate, per-benchmark texture.
- Null-baseline: 1000 within-pair label-swap permutations, fixed seed.

**Per-source preprocessing.**
- *SWE-bench Verified.* Build (agent, instance_id, success) triples from each submission's `results/results.json`. Pre-register the rule for `no_logs` instance IDs (default: treat as failure, sensitivity-check by exclusion). Pre-register whether the 134 submissions are treated as 134 distinct agents or deduplicated by scaffold (default: 134 distinct).
- *LiveCodeBench.* Build (model, question_id, success) triples from each submission's `Scenario.codegeneration_*_eval_all.json` `graded_list`. Pre-register dedup rule across thinking/temperature/prompt variants (default: keep one canonical variant per model family, choose latest). Difficulty available two ways: data-driven (mean pass rate across models) and human-labeled (easy/medium/hard from contest source). Run analysis with both definitions; pre-register data-driven as primary, human-labeled as sensitivity check.
- *MMLU-Pro.* Build (model, question_id, success) triples from each `eval_results/<model>.zip` per-question record (`success = pred == answer`). 14 disciplines available; pre-register whether to pool or report per-discipline (default: pooled primary, per-discipline texture in supplementary).

**Pre-registration.** Single OSF Pre-Data Collection Registration covering all three sources, submitted *before* any of the held-out data is pulled. Orthodox template (the analyst has not seen any of the three datasets in the per-instance multi-model paired form Plimsoll requires). Registration enumerates the per-source preprocessing decisions above as pre-committed choices.

**Power statement.** Per-source MDE derived from Component A. Pre-registration includes a separate MDE statement for each source: "given source X's N pairs and M tasks, under [chosen generative model] with [chosen signal strength assumption], we have 80% power to detect observed median |Δ| ≥ Y at α = 0.001."

**Frozen scripts.** Single `analyze.py` and `null-baseline.py` parametrized over data source. Frozen at git commit SHA at OSF registration time. One run per source produces three result CSVs and three null-baseline CSVs.

**Data provenance.** Re-analysis of public leaderboard data does not require explicit re-licensing — facts are not copyrightable (Feist v. Rural 1991; pass/fail outcomes from automated test runs are particularly thin on creative authorship). The OSF pre-registration's data-provenance section will cite (a) public availability, (b) fact-doctrine, and (c) for SWE-bench: the `swe-bench/experiments` repo's stated reproducibility intent ("publicly accessible and meant to enable greater reproducibility and transparency"). Post-publication courtesy emails to Princeton NLP / John Yang and to METR are appropriate academic norm but are not blocking dependencies for Gate 0.5.

## Sequencing & dependencies

```
Component A ─┐
             ├──▶ Component C ──▶ Gate 0.5 verdict ──▶ Gate 1
Component B ─┘
```

- A and B run in parallel; both block C.
- C blocks Gate 1 (protocol formalization).
- Gate 0.5 outcome blocks Gates 4–5 (Phase 1 re-analyses): no point re-analyzing Madaan/Du through a methodology that hasn't been independently confirmed.
- Optional Gate 1.5 (Ndzomga email) reasonably waits until Gate 0.5 clears so the email can include the prospective replication result.

## Why this gate exists (review-defense framing)

Two convergent specialist findings from the 2026-04-25 Study Gate were not retired by Change 1 (null-baseline permutation):
1. **Recursive consistency failure.** Gate 0 doesn't satisfy Plimsoll elements 3 + 5 — and Plimsoll is the methodology demanding both.
2. **Single-dataset risk.** The headline rests on Ndzomga's aggregation. A reviewer can dismiss with "interesting on this one dataset, unclear if it generalizes."

Change 2 (post-hoc OSF re-registration) addressed (1) weakly and didn't address (2) at all. Gate 0.5 retires both: elements 3 and 5 satisfied prospectively (registration before data access; power analysis from Component A), single-dataset risk retired by independent replication on a held-out source.

The paper's load-bearing empirical claim shifts from Gate 0 to Gate 0.5. Gate 0 stays as motivating context, explicitly labeled.

## Budget

- Component A: $0 (simulation runs locally).
- Component B: $0 (inventory is analyst time only).
- Component C: $0 if held-out data is published per-instance. Contingency ≤ $50 if any agent re-runs are required (well within the $500 Plimsoll cap).

Estimated remaining Plimsoll budget after Gate 0.5: ≥ $450.

## Artifacts (in `gate-0.5/`)

- `README.md` — this document
- `inventory.md` — original Component B inventory output (initial pass; SWE-bench primary + METR secondary recommendation now superseded by supplemental fan-out)
- `inventory-supplement/` — supplemental cluster inventories that confirmed MMLU-Pro and LiveCodeBench:
  - `nl2sql.md` — NL2SQL cluster (no qualifying candidates; structural finding about the field)
  - `math-reasoning.md` — math/reasoning cluster (MMLU-Pro qualifies)
  - `code-non-swe.md` — code-non-SWE cluster (LiveCodeBench qualifies, double-confirmed)
  - `agent-uncertain.md` — UNCERTAIN resolution from initial inventory (LiveCodeBench confirmed; HELM Capabilities as fallback; HELM Agents / WebArena / AgentBench definitively disqualified)
- `simulation.py` — Component A frozen script (to be created)
- `simulation-results/` — MDE tables and plots (populated after Component A runs)
- `analyze.py` — analysis pipeline parametrized over data source (extends `gate-0/analyze.py`)
- `null-baseline.py` — null-baseline parametrized over data source (extends `gate-0/null-baseline.py`)
- `prep-swebench.py` — preprocessing for SWE-bench `experiments/` repo to (agent, instance, success) triples
- `prep-livecodebench.py` — preprocessing for LiveCodeBench `submissions/` repo (extract `graded_list`, dedup variants)
- `prep-mmlu-pro.py` — preprocessing for MMLU-Pro `eval_results/` ZIPs (`pred == answer`)
- `pre-registration.md` — OSF registration document (single document covering all three sources), drafted *before* pulling held-out data
- `results/` — populated after Component C runs (one subdirectory per source)

## Open questions

- **Does Component A's simulation result deserve its own paper section?** If MIRT generatively reproduces the observed instability with realistic parameters, that's a Plimsoll-paper section, not a side artifact — and it's relevant to the project's name (the Plimsoll-line metaphor is one-dimensional; multidimensional skill structure is a manifold). Decide after running; naming decision parked until then.
- **Should the [0.30, 0.70] band be tuned per held-out source?** Gate 0 used Ndzomga's default uniformly. The three Gate 0.5 sources have different difficulty distributions: SWE-bench Verified is mid-skewed, LiveCodeBench has explicit easy/medium/hard categories, MMLU-Pro spans 14 disciplines with varied difficulty. Pre-register the rule for tuning before seeing the data — default: same band uniformly across all three, per-source band tuning as sensitivity analysis only.
- **LiveCodeBench dedup convention.** The 73 submissions include multiple variants per model (thinking on/off, temperature sweeps, prompt variants). Pre-register the dedup rule before pulling data; default keep one canonical variant per model family, latest dated. Decision must be in the OSF registration.
- **MMLU-Pro pooling vs per-discipline.** 14 disciplines could be analyzed pooled (single decision rule application) or per-discipline (14 sub-decisions). Pooled is cleaner for the headline; per-discipline is informative for the MIRT theoretical anchor. Pre-register pooled as primary, per-discipline as supplementary.

## Closed questions (resolved 2026-04-26)

- ~~Single held-out source vs. multiple?~~ Three sources selected (SWE-bench primary + LiveCodeBench + MMLU-Pro), with layered decision rule.
- ~~What if no public agent leaderboard publishes per-instance data outside Ndzomga's set?~~ Moot; three qualifying sources confirmed by inventory.

## Connections

- [[Projects/Research/Plimsoll/README|Plimsoll project README]] — parent
- [[Projects/Research/Plimsoll/gate-0/README|Gate 0]] — exploratory motivation that surfaced the headline
- [[Projects/Research/Plimsoll/literature-review|literature-review.md]] — prior art (Ndzomga 2026, Habba 2026, Hofmann 2025)
