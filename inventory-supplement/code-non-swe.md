---
project: Plimsoll
kind: gate-0.5-inventory-supplement
cluster: code-non-swe
status: complete
updated: 2026-04-26
---

# Gate 0.5 Inventory Supplement — Code (Non-SWE) Cluster

## Summary

Two strong qualifying secondaries exist outside SWE-bench-family. **LiveCodeBench** is the
top recommendation: an open `LiveCodeBench/submissions` repo (MIT) ships per-instance
`graded_list` booleans with `question_id` and `difficulty` for 73+ named model
submissions. **CRUXEval** is a clean fallback: `samples/evaluation_results.zip` in the
official repo holds per-task graded outputs for the leaderboard models on 800 problems.
EvalPlus (HumanEval+/MBPP+) is technically usable but flagged: HumanEval+ and MBPP+ are
named explicitly in Pine Curtain's validation protocol, so they are not cleanly held-out
for this user. BigCodeBench's HF "results" dataset is aggregate-only (202 rows); raw
per-task evals require running the eval pipeline against `sanitized_samples_calibrated.zip`
release artifacts (possible but not pre-cooked).

## Candidate verdicts

| Candidate | Per-instance data? | Models | Problems | License | Verdict |
|---|---|---|---|---|---|
| HumanEval / HumanEval+ (EvalPlus) | UNCERTAIN — datasets + per-model eval pipeline public, but no curated multi-model per-instance dump found | 80+ on leaderboard | 164 base / ~500 with extended tests | Apache-2.0 (code), CC (data) | DISQUALIFIED — overlaps Pine Curtain validation set |
| MBPP / MBPP+ (EvalPlus) | UNCERTAIN — same as above | 80+ on leaderboard | 378–974 | Apache-2.0 / CC | DISQUALIFIED — overlaps Pine Curtain validation set |
| BigCodeBench | PARTIAL — pre-generated samples zip in GH releases (163 models claimed Jan 2025); HF `bigcode/bigcodebench-results` is aggregate-only (202 rows) | ~163 in samples zip; 200+ aggregate | 1,140 (full) / 148 (Hard) | Apache-2.0 | QUALIFIES (partial — must run eval pipeline against released samples to get per-task booleans) |
| **LiveCodeBench** | **YES — `LiveCodeBench/submissions` repo holds `Scenario.codegeneration_*_eval_all.json` per submission with `question_id`, `difficulty`, `graded_list`** | **73 model dirs (incl. duplicates for thinking/non-thinking, temperature, prompt variants)** | **400+ Codeforces/LeetCode/AtCoder problems with timestamp; difficulty easy/medium/hard** | **MIT** | **QUALIFIES — strongest candidate** |
| ClassEval | YES — `output/result/detailed_result.json` (13 MB) and `output/model_output/` published in repo | Unspecified count in published file (multiple LLMs studied per paper) | 100 classes / 410 methods | MIT (code) + CC BY-NC 4.0 (data) | QUALIFIES (small N caveat — only 100 problems, may not satisfy ≥50 with non-trivial spread after filter; CC BY-NC limits commercial reuse) |
| **CRUXEval** | **YES — `samples/evaluation_results.zip` and `samples/model_generations.zip` in `facebookresearch/cruxeval`** | **Leaderboard-listed models (paper reported ~20)** | **800 (CRUXEval-I + CRUXEval-O, 400 each)** | **MIT (Meta/FAIR)** | **QUALIFIES — clean fallback** |
| DS-1000 | NO — `results/*-result.txt` files are pre-aggregated by library / perturbation_type; no per-problem booleans published | ~5 in repo | 1,000 | Apache-2.0 / CC BY-SA-4.0 | DISQUALIFIED — aggregate only |
| HumanEval-X / MultiPL-E | UNCERTAIN — datasets public on HF; no centralized multi-model per-instance dump located | N/A | 22 languages × 164 (HumanEval-X) | MIT / dataset-specific | DISQUALIFIED — likely re-runs of HumanEval; same overlap concern as EvalPlus |
| CodeContests (DeepMind) | NO — dataset published; no per-model leaderboard with per-problem booleans | N/A (dataset, not leaderboard) | ~13K | Apache-2.0 (data CC BY 4.0) | DISQUALIFIED — no published per-model results |
| APPS | NO — dataset public; no centralized per-model per-problem leaderboard dump | N/A | 10,000 | MIT | DISQUALIFIED — no published per-model results |
| RepoBench | NO — dataset published; per-model results not centrally collected | N/A | varies | MIT | DISQUALIFIED |
| RepairBench (bonus) | YES — `results/<model>/{defects4j,gitbugjava}/` per-bug patches + grading; ~40 model dirs at `ASSERT-KTH/repairbench/results` | ~40 | Defects4J + GitBug-Java bug counts (hundreds) | LICENSE not declared in repo top-level (UNCERTAIN) | QUALIFIES (with license caveat — overlaps SWE-bench premise of "patch real repos"; may not be sufficiently distinct from primary) |

## Per-candidate detail

### HumanEval / HumanEval+ (EvalPlus)

- **Data location:** `huggingface.co/datasets/evalplus/humanevalplus`; release files at `github.com/evalplus/humanevalplus_release`. Leaderboard at `evalplus.github.io/leaderboard.html`. EvalPlus runs eval locally and writes to `evalplus_results/humaneval/`; no centralized per-model curated dump for the 80+ leaderboard models was located in the time budget.
- **Coverage:** 164 base problems, ~500 extended tests per task.
- **Difficulty distribution:** Saturating — most frontier models above 80% pass@1, will not yield a meaningful [0.30, 0.70] band on most pairs.
- **License:** Apache-2.0 (code), CC (data).
- **User prior work:** **FLAG.** `Projects/Products/Pine Curtain/pine-curtain-validation-protocols.md` line 189 explicitly names HumanEval+ (164 tasks) as a validation set. Disqualifies as held-out.
- **Verdict & rationale:** DISQUALIFIED on user-prior-work constraint; saturation also reduces statistical leverage.

### MBPP / MBPP+ (EvalPlus)

- **Data location:** `huggingface.co/datasets/evalplus/mbppplus`; release files at `github.com/evalplus/mbppplus_release`.
- **Coverage:** 378 problems in MBPP+ (974 in original MBPP).
- **Difficulty distribution:** Easier than HumanEval+; substantial saturation at frontier.
- **License:** Apache-2.0 (code), CC (data).
- **User prior work:** **FLAG.** Same Pine Curtain protocols doc, line 190, names MBPP+ (399 tasks) explicitly. Disqualifies as held-out.
- **Verdict & rationale:** DISQUALIFIED on user-prior-work constraint.

### BigCodeBench

- **Data location:** Aggregate scoreboard at `huggingface.co/datasets/bigcode/bigcodebench-results` (202 rows, columns: model, complete, instruct, size, type, date — NO per-task fields). Per-task data must be reconstructed from `sanitized_samples_calibrated.zip` released as GH release assets (release notes claim "163 models evaluated" as of v0.2.2.dev2, Jan 2025). File-name convention: `[model]--bigcodebench-[instruct|complete]--[backend]-[temp]-[n]-sanitized_calibrated_eval_results.json`.
- **Coverage:** 1,140 tasks (full), 148 (BigCodeBench-Hard subset).
- **Difficulty distribution:** Hard subset is defined as <50% solve rate across evaluated models — useful, but already filtered, so the methodology's filter logic would need adjustment.
- **License:** Apache-2.0.
- **User prior work:** None located.
- **Verdict & rationale:** QUALIFIES with PARTIAL caveat. The HF leaderboard dataset is aggregate-only and would not satisfy criterion 1 by itself. Per-task booleans require fetching the calibrated samples zip and (likely) re-running the verifier, or hoping `_eval_results.json` files are bundled. Higher engineering cost than LiveCodeBench/CRUXEval; recommend only as tertiary backstop.

### LiveCodeBench

- **Data location:** `github.com/LiveCodeBench/submissions` (MIT). Each model submission lives in a top-level dir (e.g., `Claude-Opus-4/`, `GPT-4O-2024-08-06/`, `O3-Mini-2025-01-31 (High)/`, `DeepSeek-V3/`, `Gemini-2.5-Pro-06-05/`, `Kimi-k1.6-IOI/`). Each dir contains a `Scenario.codegeneration_1_0.2_eval_all.json` (~5 MB) holding a list of records with: `question_title`, `question_id`, `contest_id`, `contest_date`, `platform` (codeforces/leetcode/atcoder), `difficulty` ∈ {easy, medium, hard}, `output_list` (model output), `code_list` (extracted code), and **`graded_list` (boolean per problem — exactly the (model, question, success) triple Plimsoll needs)**.
- **Coverage:** 73 model directories at top level (some near-duplicates: thinking vs. non-thinking, temperature variants, prompt-old replays). Roughly 50+ distinct models after dedup. Problem set is the LiveCodeBench rolling window of Codeforces/LeetCode/AtCoder problems with timestamps — published rolling versions have several hundred problems each.
- **Difficulty distribution:** Three tiers (easy/medium/hard) and platform-stratified; broad spread known from the paper. Mean-pass-rate filter [0.30, 0.70] should yield a non-trivial population.
- **License:** MIT (submissions repo); LiveCodeBench framework also MIT.
- **User prior work:** None located in the vault.
- **Verdict & rationale:** **QUALIFIES — top recommendation.** Per-instance `graded_list` is exactly the Plimsoll input; sample size is comfortable; license is permissive; not in Ndzomga; cleanly held-out from user's prior work. The only caveat is that submissions span different LiveCodeBench versions (rolling problem set) — Plimsoll will need to filter to a common problem-id intersection across submissions before running paired stats. This is straightforward via `question_id` / `contest_id`.

### ClassEval

- **Data location:** `github.com/FudanSELab/ClassEval/output/result/detailed_result.json` (13 MB) and `output/model_output/`. Leaderboard at `fudanselab-classeval.github.io/leaderboard.html`.
- **Coverage:** 100 classes, 410 methods. Fewer models in published JSON than the leaderboard claims; needs sanity check.
- **Difficulty distribution:** Class-level (not function-level) — different task type from HumanEval. Pass-rate spread reasonable per paper.
- **License:** MIT for code; **CC BY-NC 4.0 for data** — re-analysis is fine, but commercial re-publication may be constrained.
- **User prior work:** None located.
- **Verdict & rationale:** QUALIFIES with caveats. Only 100 problems — borderline on the ≥50-with-spread criterion if mean-pass-rate filter halves it. CC BY-NC adds friction. Use only if multiple secondaries are needed.

### CRUXEval

- **Data location:** `github.com/facebookresearch/cruxeval/samples/evaluation_results.zip` (5.9 MB) and `samples/model_generations.zip` — both checked into git. Unzip to `samples/evaluation_results/` for per-task graded outputs.
- **Coverage:** 800 problems total (400 input-prediction CRUXEval-I + 400 output-prediction CRUXEval-O). Leaderboard at `crux-eval.github.io/leaderboard.html` lists ~20 models; sample zip holds matching per-task graded data.
- **Difficulty distribution:** Code-reasoning task (predict input/output of Python function) — not code generation per se, which makes it cleanly distinct from SWE-bench. Pass-rate spread documented in paper.
- **License:** MIT (Meta/FAIR repo).
- **User prior work:** None located.
- **Verdict & rationale:** QUALIFIES — clean fallback. Not in Ndzomga's 8; not overlapping Pine Curtain or Structure-Beats-Scale; per-task booleans pre-computed and version-controlled. Smaller model count than LiveCodeBench is the main weakness; on the ≥20-models criterion it's right at the edge. Note: CRUXEval is *code reasoning*, not code *generation* — fine for the methodology but worth disclosing in the paper.

### DS-1000

- **Data location:** `github.com/xlang-ai/DS-1000/results/*-result.txt`. Inspected: files are pandas-style aggregate breakdowns by library and perturbation_type only — no per-problem booleans.
- **Coverage:** 1,000 problems; only ~5 model results published in repo (codex002, gpt-3.5-turbo-0125, gpt-3.5-turbo-0613, gpt-4-0613, gpt-4-turbo).
- **License:** Apache-2.0 / CC BY-SA-4.0.
- **Verdict & rationale:** DISQUALIFIED — aggregate-only and only 5 models.

### HumanEval-X / MultiPL-E

- **Data location:** `huggingface.co/datasets/nuprl/MultiPL-E` (datasets only). No centralized multi-model per-instance dump located.
- **Verdict & rationale:** DISQUALIFIED on per-instance criterion AND substantially overlaps HumanEval (which is in user prior work).

### CodeContests (DeepMind)

- **Data location:** Dataset only at `github.com/google-deepmind/code_contests` and `huggingface.co/datasets/deepmind/code_contests`. No public per-model per-problem leaderboard.
- **Verdict & rationale:** DISQUALIFIED — no central per-model results.

### APPS

- **Data location:** Dataset at `github.com/hendrycks/apps` and `huggingface.co/datasets/codeparrot/apps`. No central per-model per-problem leaderboard.
- **Verdict & rationale:** DISQUALIFIED — no published per-model results.

### RepoBench

- **Data location:** `github.com/Leolty/repobench`; aggregate leaderboard at llm-stats.com.
- **Verdict & rationale:** DISQUALIFIED — no published per-instance per-model results.

### RepairBench (bonus)

- **Data location:** `github.com/ASSERT-KTH/repairbench/results/<model>/{defects4j,gitbugjava}/` — ~40 model dirs (claude-3-7-sonnet-20250219, deepseek-r1, gpt-4.1-2025-04-14, o3-mini, llama-4-maverick, gemini-2.5-pro-preview-03-25, etc.) holding per-bug patches + grading. `total.json` (12 KB) at results root.
- **Coverage:** Defects4J + GitBug-Java bugs (hundreds total).
- **License:** Top-level LICENSE not declared in repo metadata (UNCERTAIN — needs manual check).
- **Verdict & rationale:** QUALIFIES with caveats but DEPRIORITIZED. RepairBench is bug-fix on real Java repos — conceptually the closest neighbor to SWE-bench's "patch real repos" pattern. Including it as the secondary partly defeats the held-out goal of finding a *different kind* of code task. Recommend skipping unless LiveCodeBench and CRUXEval both fail.

## Recommendation

**Primary secondary: LiveCodeBench.** `LiveCodeBench/submissions` repo (MIT) is exactly the
shape Plimsoll needs — per-submission JSON with `question_id`, `difficulty`, and a boolean
`graded_list` for every model run. 73 submission directories (≥50 distinct models post-dedup),
hundreds of problems, three difficulty tiers, distinct from SWE-bench (competition problems
vs. real-repo patches), and not in Ndzomga's 8. Only handling note: filter to the
problem-id intersection across submissions before paired stats, since submissions ride a
rolling problem set.

**Fallback secondary: CRUXEval.** `facebookresearch/cruxeval/samples/evaluation_results.zip`
gives clean per-task booleans for ~20 models on 800 problems (MIT). Smaller model count
(right at the ≥20 threshold) and the task is code-reasoning rather than code-generation —
disclose this distinction if reporting.

**Avoid:** HumanEval+/MBPP+ (overlaps Pine Curtain validation protocol — not held-out for
this user). DS-1000 (aggregate-only). APPS, CodeContests, RepoBench (no published per-model
per-problem dumps).

**Tertiary if needed:** BigCodeBench via `sanitized_samples_calibrated.zip` GH release —
~163 models but engineering cost is real (must reconstruct per-task booleans from samples).
