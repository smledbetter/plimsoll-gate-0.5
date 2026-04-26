---
project: Plimsoll
kind: gate-0.5-inventory-supplement
cluster: math-reasoning
status: complete
updated: 2026-04-26
---

# Gate 0.5 Inventory Supplement — Math / Reasoning Cluster

## Summary

**MMLU-Pro qualifies as a strong secondary** to replace METR Time Horizon: 48 distinct model-output ZIPs cached in `TIGER-AI-Lab/MMLU-Pro/eval_results/` over 12,032 multiple-choice questions across 14 disciplines, repo and dataset both Apache-2.0 / MIT licensed, and not in Ndzomga's set. Per-question pass/fail is reconstructable directly from `pred == answer`. Every other math/reasoning candidate either publishes only aggregate accuracy on a leaderboard webpage (GPQA, MMLU, AIME on Vals.ai/llm-stats, FrontierMath, ARC-AGI, OlympiadBench) or publishes per-instance data for only one model (BIG-Bench Hard's `code-davinci-002-outputs/`).

## Candidate verdicts

| Candidate | Per-instance data? | Models | Questions | License | Verdict |
|---|---|---|---|---|---|
| MATH (Hendrycks) | no — dataset only, no per-model dump | n/a | 12,500 | MIT (dataset) | DISQUALIFIED |
| GSM8K | no — dataset only | n/a | 8,500 | MIT (dataset) | DISQUALIFIED |
| AIME 2024 (GAIR-NLP/AIME-Preview) | UNCERTAIN — paper reports per-question pass@k for a small set; full dump not located | ~12 | 30 | UNCERTAIN | UNCERTAIN, and 30 questions is below the ≥50 threshold |
| OlympiadBench | no — papers report aggregate scores; no per-instance multi-model dump located | unknown | 8,476 | UNCERTAIN | DISQUALIFIED on per-instance criterion |
| BIG-Bench Hard (BBH) | partial — only `code-davinci-002-outputs/` published | 1 | 23 tasks × ~250 each | MIT | DISQUALIFIED (single model) |
| BIG-Bench Extra Hard (BBEH) | UNCERTAIN — could not locate per-model results dump | unknown | unknown | Apache-2.0 (likely) | UNCERTAIN |
| **MMLU-Pro (TIGER-AI-Lab)** | **yes — `eval_results/model_outputs_*.zip`, JSON with `pred`/`answer` fields** | **48** | **12,032** | **Apache-2.0 (code) / MIT (dataset)** | **QUALIFIES** |
| ARC-AGI-1 / ARC-AGI-2 (arcprize) | no — `arcprize/model_baseline` and `arc-agi-benchmarking` are frameworks; only sample/baseline results in repo | unknown | 400+ | MIT (code) | DISQUALIFIED on data availability |
| GPQA / GPQA Diamond | no — leaderboards (Artificial Analysis, Epoch AI, llm-stats) publish aggregate scores only; `idavidrein/gpqa` ships dataset + baseline scripts | n/a | 448 (198 Diamond) | MIT (dataset, password-protected canary) | DISQUALIFIED on per-instance criterion |
| FrontierMath | no — only sample-question transcripts published; full dataset is held-out by Epoch AI | n/a | ~300 | held-out | DISQUALIFIED |

## Per-candidate detail

### MATH (Hendrycks et al. 2021)

- **Data location:** `https://github.com/hendrycks/math` publishes the dataset (12,500 problems) and evaluation code, not per-model prediction dumps. Per-model accuracies are reported in individual papers (aggregate only).
- **Coverage:** 12,500 problems across 7 subjects × 5 difficulty levels.
- **License:** MIT (dataset).
- **User prior work:** no.
- **Verdict & rationale:** DISQUALIFIED — fails per-instance criterion. Reconstructing a multi-model per-question matrix would require running ≥20 models on all 12,500 problems ourselves (out of scope for held-out replication).

### GSM8K (Cobbe et al. 2021)

- **Data location:** dataset on `openai/grade-school-math` and HuggingFace. No central per-model prediction dump for many submissions.
- **Coverage:** 8,500 grade-school problems (test split: 1,319).
- **License:** MIT (dataset).
- **User prior work:** no.
- **Verdict & rationale:** DISQUALIFIED — same as MATH. Saturated by frontier models, so the [0.30, 0.70] band would require including older / smaller models, but no consolidated dump exists.

### AIME 2024 / 2025

- **Data location:** `GAIR-NLP/AIME-Preview` covers AIME with detailed hyperparameters and multiple model evaluations (DeepSeek-R1 variants, o-series, Gemini, etc.). Could not confirm a single downloadable per-question per-model JSON in the repo within the time budget. Vals.ai and llm-stats AIME 2024 leaderboards (52 and ~30+ models respectively) are aggregate-only on the public webpage. MathArena posts per-model results but per-question dumps weren't located.
- **Coverage:** ~30 problems per year (well below ≥50 threshold for one year; pooling 2024+2025 gets ~60).
- **License:** UNCERTAIN.
- **User prior work:** no.
- **Verdict & rationale:** UNCERTAIN, and even if per-question data were located, the question count is borderline. Not recommended.

### OlympiadBench (He et al. 2024)

- **Data location:** `OpenBMB/OlympiadBench` publishes the dataset and evaluation code. The companion paper reports aggregate accuracy per model (e.g., GPT-4V 17.97% average). No per-instance multi-model dump located.
- **Coverage:** 8,476 problems (math + physics, bilingual, multimodal).
- **License:** UNCERTAIN.
- **User prior work:** no.
- **Verdict & rationale:** DISQUALIFIED on per-instance criterion. Multimodal complicates re-analysis even if data were available.

### BIG-Bench Hard (Suzgun et al. 2022)

- **Data location:** `suzgunmirac/BIG-Bench-Hard` ships per-instance outputs only for `code-davinci-002` (`/code-davinci-002-outputs/`). No multi-model per-instance dump in the repo.
- **Coverage:** 23 tasks × ~250 examples each, but only one model's outputs published.
- **License:** MIT.
- **User prior work:** no.
- **Verdict & rationale:** DISQUALIFIED — single-model coverage fails ≥20 model requirement.

### BIG-Bench Extra Hard / BBEH (2025)

- **Data location:** `google-deepmind/bbeh` repo exists; per-model results dump structure not confirmed in time-box.
- **Verdict & rationale:** UNCERTAIN — could not locate per-instance data file. Probably worth ~10 minutes of follow-up if MMLU-Pro is rejected for any reason.

### MMLU-Pro (Wang et al. 2024) — TIGER-AI-Lab/MMLU-Pro

- **Data location:** `https://github.com/TIGER-AI-Lab/MMLU-Pro/tree/main/eval_results`. 48 ZIP archives named `model_outputs_<MODEL>_<SHOTS>.zip` (and a few `.json.zip` variants). Each ZIP contains JSON with per-question records. Per the `evaluate_from_local.py` source, each record includes `pred` (extracted prediction A-J), `answer` (correct label), `answer_index`, `options`, `model_outputs` (raw generation), plus the original `question`, `category`, `cot_content`. Per-question pass/fail = `pred == answer`.
- **Coverage:** 48 model-output dumps; 12,032 questions across 14 categories (Math 1351, Physics 1299, Chemistry 1132, Law 1101, Engineering 969, Other 924, Economics 844, Health 818, Psychology 798, Business 789, Biology 717, Philosophy 499, CS 410, History 381). Models span Llama-2/3/3.1 (multiple sizes), Mistral 7B variants, Mixtral 8x7B, Qwen 1.5 (7B–110B), Yi-6B/34B, Phi-3-mini, Gemma-7B, DeepSeek (V2, V2.5, chat), Claude 3.5 Haiku/Sonnet, GPT-4o (multiple dates) + GPT-4o-mini, Gemini 1.5 Flash/Pro + Gemini 3.1 Pro, Mathstral-7B, Jamba-1.5-large, Command-R, plus a few unlabelled `arx`/`opus`/`sonnet`/`flash` dumps. Wide capability spread (Llama-2-7b ~10–20% on hard categories vs Gemini-3.1-Pro ~80%+ aggregate) guarantees [0.30, 0.70] band has support.
- **Difficulty distribution:** 14 disciplines with very uneven question counts. Math/STEM categories have ~1000+ questions; History/CS/Philosophy in the 380–500 range. The leaderboard average across 116 models on the HF Space is ~0.706 (TIGER-Lab leaderboard), with state-of-the-art at ~0.885 — implying a long left tail of 7B-scale models in the 0.30–0.55 band on most categories.
- **License:** Repository code Apache-2.0 (confirmed via `LICENSE` file fetch). Dataset MIT (per HF dataset card). Both permit re-analysis with attribution. **Cleanest license posture of any held-out source we've found, including the SWE-bench primary.**
- **User prior work:** no — user has not done multi-model paired-effect-size analysis on MMLU-Pro.
- **Overlap with Ndzomga:** none — MMLU-Pro is not among Ndzomga's 8 benchmarks (swebench_verified_mini, corebench_hard, usaco, gaia, online_mind2web, taubench_airline, assistantbench, scicode).
- **Notes / caveats:**
  - The 48 model dumps are a subset of the 116 models that appear on the HF Space leaderboard (which presumably runs models without uploading the JSON). The 48 with public per-question JSON is what we have to work with — still well above the ≥20 threshold.
  - Five-shot is the dominant config; a few entries are 0-shot or 2-shot. Pre-register either (a) restrict to 5-shot for cleanest comparison (drops ~5 entries) or (b) treat shot-count as a covariate. Default: restrict to 5-shot.
  - Some filenames (`arx_0314`, `opus_2shots`, `sonnet_0shots_*`, `flash_0shots_*`) lack clear model versioning. Pre-register inclusion/exclusion of ambiguous-name dumps. Default: exclude.
  - MMLU-Pro is multiple-choice (10 options), not generative — so "pass/fail" is well-defined and not subject to grader noise. This is actually a methodological advantage over SWE-bench (where `no_logs` ambiguity exists).
  - Domain skew is STEM-heavy (Math + Physics + Chemistry + Engineering + Bio = 5468 / 12032 = 45%), so it's reasoning-heavy but not pure math. This makes it a stronger generalization test than a pure-math benchmark would be.
- **Verdict & rationale:** **QUALIFIES.** Strongest math/reasoning candidate by every selection criterion. Recommended as **secondary to replace METR Time Horizon**.

### ARC-AGI-1 / ARC-AGI-2

- **Data location:** `arcprize/arc-agi-benchmarking` is the benchmarking framework. `results/` only contains `random-baseline-sample/` and per-config dirs you populate yourself. `arcprize/model_baseline` is similarly framework-only. ARC Prize Leaderboard at arcprize.org/leaderboard publishes scores but per-task pass/fail per model not located. Kaggle ARC Prize 2025 final solutions often private.
- **Coverage:** 400 public eval tasks (ARC-AGI-1) + 1000 ARC-AGI-2 tasks; many submissions, but consolidated per-task data not published.
- **License:** MIT (code).
- **User prior work:** user has a separate ARC-AGI-3 dossier (different evaluation, Stage 0 probe pending). ARC-AGI-1 / -2 not previously analyzed.
- **Verdict & rationale:** DISQUALIFIED on per-instance criterion. The ARC Prize team holds the per-task per-model data privately; only aggregate scores are posted.

### GPQA / GPQA Diamond (Rein et al. 2024)

- **Data location:** `idavidrein/gpqa` ships the dataset (password-protected zip to prevent training contamination), `baselines/` evaluation scripts, and `baseline_results/` for GPT-3.5-turbo and GPT-4 only. Public leaderboards (Artificial Analysis, Epoch AI, llm-stats with 209 model entries, Vellum, intuitionlabs, AI Stats) all publish aggregate scores only on their webpages — no per-instance JSON download.
- **Coverage:** 448 questions total, 198 in Diamond subset.
- **License:** MIT for code; dataset has canary string + password lock.
- **User prior work:** no.
- **Verdict & rationale:** DISQUALIFIED on per-instance criterion. Despite 200+ models on llm-stats, the per-question dump is not public for any aggregator. Worth noting for paper discussion: GPQA is the most-cited reasoning benchmark with this data-release problem, and the Plimsoll methodology genuinely cannot be applied to it from public sources alone.

### FrontierMath (Epoch AI)

- **Data location:** Held-out by Epoch AI (only `sample_question_transcripts.zip` is public). Full dataset and per-model evaluations are private.
- **Coverage:** ~300 problems (Tiers 1-4), but inaccessible to public re-analysis.
- **License:** held-out.
- **Verdict & rationale:** DISQUALIFIED — data not public.

## Recommendation

**Recommended secondary (replace METR Time Horizon): MMLU-Pro via `TIGER-AI-Lab/MMLU-Pro/eval_results/`.**

Data fetch:

```bash
git clone https://github.com/TIGER-AI-Lab/MMLU-Pro.git
cd MMLU-Pro/eval_results
# 48 ZIPs total; restrict to *_5shots.zip for clean comparison (~40 dumps)
for z in *_5shots*.zip; do unzip -o "$z" -d "${z%.zip}/"; done
# Each unzipped JSON: list of records with fields {question_id, pred, answer, answer_index, options, model_outputs, question, category, cot_content}
# Per-question pass/fail: success = (record["pred"] == record["answer"])
# Build (model, question_id, success) triples by joining filename-derived model name with each record's question_id.
```

Preprocessing notes:
1. Restrict to 5-shot dumps for clean cross-model comparison (drops ~5 ambiguous 0-shot/2-shot entries). Pre-register the rule.
2. Exclude ambiguously-named dumps (`arx_0314`, `opus_2shots_*`, `sonnet_0shots_*`, `flash_0shots_*`) unless model+date can be unambiguously resolved. Pre-register the rule.
3. License posture is the cleanest of any candidate (Apache-2.0 code + MIT dataset). No outreach email needed before OSF registration.
4. The benchmark is multiple-choice — `pred == answer` is unambiguous, no `no_logs`-style ambiguity.

**Why this beats METR Time Horizon for the secondary slot:**

- Models: 48 dumps (≥40 after 5-shot filter) vs. 21 — much stronger statistical power.
- Questions: 12,032 vs. 228 — much wider [0.30, 0.70] band support, plus ability to do per-discipline subgroup analyses if desired.
- License: Apache-2.0 + MIT vs. unlicensed. Removes the "email METR for permission" step.
- Domain: pure reasoning / multiple-choice knowledge vs. agentic research engineering. Wider domain gap from SWE-bench primary = stronger generalization claim if both clear.
- Politics: zero. METR Time Horizon is a politically sensitive line of work; MMLU-Pro is plain-vanilla LLM evaluation.
- Not previously analyzed by the user, not in Ndzomga's 8.

**Two-source replication framing if both clear:** "ranks preserved, effects collapse on Ndzomga aggregate; effect-collapse pattern reproduces on the full SWE-bench Verified leaderboard (134 agents × 500 instances, agentic code-patching) and on the MMLU-Pro per-question dump (48 models × 12,032 multiple-choice reasoning questions)." Two sources, two distinct task families, two distinct evaluation paradigms (agentic vs. multiple-choice), two clean licenses.
