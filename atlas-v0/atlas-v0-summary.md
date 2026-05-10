---
title: Atlas v0 — empirical sketch of the Plimsoll doctor over six benchmarks
status: complete
date: 2026-05-10
parent: ../README.md (Plimsoll Applicability Atlas, post-Gate-2)
slate_locked: 2026-05-10 (option A in scoping; 6-benchmark cheap version pre-arXiv push)
---

# Atlas v0 — six-benchmark empirical sketch

This is a pre-Gate-2 sketch. The polished `plimsoll doctor` CLI is a Gate-2/3 deliverable; this run uses the existing `analyze.py` + `null-baseline.py` directly, plus one fractional-success-tolerant wrapper (`atlas-analyze.py`) for the METR HCAST seed-collapsed data.

## The question this sketch answers

Does the [0.30, 0.70] capability-margin band default work across the kinds of benchmarks the methodology paper expects practitioners to apply Plimsoll to, or does the methodology need a per-benchmark / per-domain rebanding rule before v1 ships?

## Selection rule (locked before pulling any data)

Six benchmarks, all LOW-complexity prep:

| Slot | Benchmark | Stress role |
|---|---|---|
| anchor 1 | SWE-bench Verified | already done; mid-range agentic-code |
| anchor 2 | LiveCodeBench | already done; mid-range competitive-programming |
| anchor 3 | MMLU-Pro | already done; mid-range multi-discipline-MC |
| stress 1 | HellaSwag | saturation test — frontier models near ceiling |
| stress 2 | GSM8K | math saturation test |
| diversity | METR HCAST | cleanest agentic dataset beyond SWE/LCB |

## Results

Per-benchmark verdicts from `atlas-v0.csv`:

| Benchmark | Domain | n_tasks | n_agents | n_pairs | in-band | m_b | null z | Stage 1 | Stage 2 | Atlas verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| swebench-verified | agentic-code | 500 | 134 | 8,911 | 33.8% | 0.126 | +230 | PASS | PRODUCES_SIGNAL | **FIT_FOR_PLIMSOLL** |
| livecodebench | competitive-programming | 1,055 | 72 | 2,556 | 37.5% | 0.156 | +375 | PASS | PRODUCES_SIGNAL | **FIT_FOR_PLIMSOLL** |
| mmlu-pro | multi-discipline-mc | 12,032 | 48 | 1,128 | 43.2% | 0.087 | +499 | PASS | PRODUCES_SIGNAL | **FIT_FOR_PLIMSOLL** |
| metr-hcast | agentic-task | 157 | 21 | 210 | 38.2% | 0.150 | +63 | PASS | PRODUCES_SIGNAL | **FIT_FOR_PLIMSOLL** |
| gsm8k | math | 1,319 | 27 | 351 | 50.0% | 0.082 | +94 | PASS | PRODUCES_SIGNAL | **FIT_FOR_PLIMSOLL** |
| hellaswag | multi-discipline-mc | 10,042 | 24 | 253 | **14.4%** | 0.164 | +864 | **FAIL** | (gated) | **STRUCTURALLY_UNFIT** |

5 of 6 benchmarks PASS Stage 1 and PRODUCES_SIGNAL on Stage 2. HellaSwag fails Stage 1 by a hair (14.4% < 15% threshold) despite producing very large m_b (0.164) and very high null z (+864) on the surviving 14.4% in-band pairs.

## The four decision criteria

### 1. In-band fraction distribution

Range: **14.4% (HellaSwag) to 50.0% (GSM8K)**. Five of six benchmarks above 33%; one just below the 15% floor.

The 5/6 above-threshold cluster sits in a tight 33–50% band. The threshold catches exactly the kind of benchmark it was designed to catch — a saturated multi-discipline-MC benchmark where ~half the items are at the ceiling. **Defaults work for 5 of 6 benchmarks; the saturated outlier is correctly flagged.**

### 2. m_b distribution

Range: **0.082 (GSM8K) to 0.164 (HellaSwag)**. Ratio max/min: **2.0×**.

Five of six fall in the narrow 0.082–0.156 band — within the "2× cluster" criterion locked at scoping time. HellaSwag's m_b = 0.164 is the largest in the set despite (or because of) Stage 1 fail: the few items that ARE in-band are the discriminating items, and discriminating items have higher pairwise variance.

The 2× clustering is the result we hoped for. **The methodology paper can defensibly cite "typical m_b on general-capability benchmarks ranges 0.08–0.16."** A vendor announcement of paired lift smaller than that range is plausibly subordinate-to-shift on most benchmarks the field cares about.

### 3. Domain clustering

Per-domain m_b clusters:

- **Agentic / code (SWE-bench, LCB, METR HCAST):** m_b 0.126–0.156. Tight cluster near the upper end.
- **Multi-discipline-MC (MMLU-Pro, HellaSwag):** MMLU-Pro 0.087, HellaSwag 0.164 (saturation-driven outlier). MMLU-Pro alone clusters at the lower end.
- **Math (GSM8K):** m_b 0.082. Same cluster as MMLU-Pro.

There IS a weak domain effect — code/agentic benchmarks have systematically larger m_b (~0.13–0.16) than math/MC benchmarks (~0.08–0.09). But the difference is within the 2× clustering threshold and likely reflects task-pool size + discrimination-spread differences, not a need for per-domain rebanding.

**Per-domain bands not strongly indicated by v0.** The Stage 1 in-band-fraction filter already handles the saturated edge case (HellaSwag).

### 4. STRUCTURALLY_UNFIT fraction

**1 of 6 = 17%.** HellaSwag is the only fail, and it fails for the right reason (saturation hollowed out the discriminating middle band).

Below the 25% threshold I locked at scoping ("if >25% of benchmarks are STRUCTURALLY UNFIT, rebanding is load-bearing for v1"). The doctor's defaults are mostly applicable across the kinds of benchmarks practitioners care about.

## Verdict on per-benchmark band rule

**v1 doesn't need a per-benchmark band rule.** All four decision criteria support deferring per-domain rebanding to Gate 1 future-work:

1. In-band fractions cluster above the 15% floor for 5/6 benchmarks ✓
2. m_b clusters within 2× across domains ✓
3. Domain effects exist but stay inside the cluster ✓
4. Structurally-unfit fraction is 17%, below the 25% intervention threshold ✓

The Stage 1 filter does the work of catching saturated benchmarks (HellaSwag's 14.4% < 15% floor catches the right benchmark for the right reason). Per-domain rebanding becomes a real concern only when:

- Atlas v1 surfaces a tail of benchmarks where Stage 1 fails for non-saturation reasons (sample-size cliffs, continuous metrics)
- Safety-tail evals (CBRN, autonomous-replication) are added to the Atlas — these operate at [0.01, 0.30] per Limitation 11 and the default band genuinely doesn't apply
- A specific high-profile benchmark sits at the boundary (e.g., 14.4% HellaSwag is the boundary case here; if the next benchmark sits at 12% but the field cares about its claims, the rule needs revision)

None of those conditions trigger at v1 ship time. **Recommendation: leave Limitation 11 as written; cite Atlas v0 as evidence-in-hand that defaults are broadly applicable; defer the per-domain rebanding deliverable to Gate 1.**

## Methodology paper Future Work language (proposed)

A short paragraph the paper's §11 / §Future Work can adopt:

> A six-benchmark empirical sketch (Atlas v0, Ledbetter 2026, code at github.com/smledbetter/plimsoll-gate-0.5) ran the doctor diagnostic across SWE-bench Verified, LiveCodeBench, MMLU-Pro, METR HCAST, GSM8K, and HellaSwag. Five of six benchmarks PASSED Stage 1 (in-band fraction in [0.338, 0.500]) and PRODUCES_SIGNAL on Stage 2 (m_b in [0.082, 0.156], null z in [+63, +499]); the sixth (HellaSwag) was correctly flagged STRUCTURALLY_UNFIT because saturation hollowed out the discriminating middle band (in-band 14.4%, below the 15% floor). The 2× clustering of m_b across domains and the 17% structurally-unfit rate justify shipping v1 with the [0.30, 0.70] default and deferring per-domain rebanding (necessary for safety-tail and saturated-mass evaluations) to Atlas v1.

## A surfaced design question for the doctor

Stage 1 is currently a hard gate (fail → skip Stage 2). HellaSwag is the case where Stage 1 fails but Stage 2 (run for completeness here) shows a very large signal — m_b 0.164, z +864. Two possible interpretations:

- **Current rule (hard gate):** STRUCTURALLY_UNFIT — too saturated to reliably apply Plimsoll. Rationale: the 14% of items in-band may not be representative of typical claim populations on the benchmark.
- **Alternative rule (warning instead of gate):** STRUCTURALLY_MARGINAL — passes Stage 2 strongly, but the small in-band fraction means audited pair claims should be interpreted as covering only the discriminating subset of items.

The first rule is simpler and conservative. The second rule preserves usable signal at the cost of more nuance in the report. Worth surfacing for the Gate 2 `plimsoll doctor` CLI design — not a v1 paper revision item.

## Caveats and what this sketch does not claim

- This is a six-benchmark sketch, not the full Atlas. The methodology paper should cite this as evidence-in-hand, not as definitive.
- The Open LLM Leaderboard v1 archive used for HellaSwag and GSM8K contains open-weights models from 2023–2024. Frontier closed models (Claude, GPT-4) are not represented. Saturation patterns may differ on a frontier-only model corpus.
- METR HCAST uses 21 agents, just above the ≥8-agent Stage 1 floor. Larger n would increase null-baseline z-score sharpness.
- Stage 3 simulation was NOT run for any benchmark — Stage 2 produced clear verdicts (PRODUCES_SIGNAL or, in HellaSwag's case, gated by Stage 1) without ambiguity.
- Safety-tail benchmarks (HarmBench, AdvBench) were intentionally excluded from v0 because Limitation 11 already cabins their treatment; their inclusion in v1 will surface the per-domain rebanding question explicitly.
- METR HCAST's seed-rerun collapse (mean of binary score_binarized across multiple seeds per agent-task) is a methodological choice; an alternative would be to take the first seed only or apply a majority-vote rule. Sensitivity check deferred.

## Reproducibility

- **Inventory:** `data-source-inventory.csv` (56 benchmarks surveyed by general-purpose research agent 2026-05-10).
- **Analyses:** `atlas-analyze.py` (fractional-success-tolerant wrapper around `gate-0.5/analyze.py`); 200-permutation null-baseline; seed=42.
- **Per-benchmark prep:** `prep-metr-hcast.py`, `prep-hf-lm-eval.py`.
- **Per-benchmark outputs:** `<benchmark>-triples.csv`, `<benchmark>-pairs.csv`, `<benchmark>-summary.csv`.
- **Atlas synthesis:** `atlas-v0.csv`.
- **Locked model list for HF lm-eval prep:** see `prep-hf-lm-eval.py` LOCKED_MODELS constant (30 frontier open-weights models, 7 orgs × 4 size buckets).
- **METR data source:** GitHub METR/eval-analysis-public, `reports/time-horizon-1-1/data/raw/runs.jsonl`, filtered to task_source == HCAST.
- **HF data source:** `open-llm-leaderboard-old/details_<model>` repos, parquet config `harness|hellaswag|10` and `harness|gsm8k|5`.

## Gate-1 follow-ups surfaced by v0

1. **Stage 1 hard-gate vs warning** — see "surfaced design question" above.
2. **Per-domain rebanding deliverable** — explicit per-domain band-selection rules for safety-tail (CBRN, autonomous-replication), saturated-mass (clinical decision-making), chain-composable (multi-step cyber). Limitation 11 names the cabin; Gate 1 should produce the rules.
3. **Larger-corpus replication** — extend to 20–30 benchmarks for Atlas v1, including safety domain (HarmBench, AILuminate via re-scoring), multimodal (MMMU), and long-context (RULER).
4. **Difficulty-stratified random-subset null** — also a surfaced gap from the methodology paper's §6.1; should run on the Atlas corpus once a v1 doctor CLI exists.
5. **plimsoll doctor CLI build** — the Gate 2 deliverable. The atlas-v0 wrapper logic is the prototype; promote to a proper CLI with the Stage-1/2/3 decision tree codified.
