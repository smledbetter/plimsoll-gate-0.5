---
project: Plimsoll
kind: gate-0.5-inventory-supplement
cluster: agent-uncertain-resolution
status: complete
updated: 2026-04-26
---

# Gate 0.5 Inventory Supplement — Agent UNCERTAIN Resolution

## Summary

Two prior-UNCERTAINs resolve to **QUALIFIES**: **LiveCodeBench** (per-instance `graded_list` boolean per attempt across 73 model dirs × 1055 questions, MIT) and **HELM Capabilities** (per-instance `display_predictions.json` paired with `instances.json` gold answers across ~22 models × 5 scenarios totalling several thousand instances, Apache-2.0). HELM Agents does not appear to be a separately exposed track; HELM Lite exists in the same bucket family as a fallback. WebArena, VisualWebArena, OSWorld, and AgentBench remain UNCERTAIN-leaning-DISQUALIFIED for Gate 0.5 because their public artifacts are scenario definitions and aggregate leaderboards rather than joinable model-by-task pass/fail matrices.

## Resolved verdicts

| Candidate | Resolution | Per-instance data? | Models | Tasks | License | New verdict |
|---|---|---|---|---|---|---|
| HELM Agents | No separate "Agents" track found in `crfm-helm-public` bucket listing or read-the-docs project list. Closest fit is HELM Capabilities. | n/a | n/a | n/a | n/a | DISQUALIFIED (track does not exist as a separable artifact) |
| HELM Capabilities | GCS bucket `gs://crfm-helm-public/capabilities/benchmark_output/runs/v1.0.0/<scenario>:...,model=<model>/` confirmed. Each run contains `display_predictions.json` (1000 instances for mmlu_pro, 2280 for bigcodebench) + `instances.json` (gold) + `per_instance_stats.json`. Per-instance pass/fail is **derivable** by joining predicted_text to gold answer (HELM does this on its own pages but doesn't expose a single boolean column). | YES (derivable; predicted_text + gold per instance) | ~22 (groups.json `# models = 22`) | 5 confirmed scenarios in v1.0.0: bigcodebench, gpqa, ifeval, mmlu_pro, omni_math (mean 797 instances/scenario) | Apache-2.0 (HELM framework) | **QUALIFIES** with caveat that scoring requires re-running HELM's metric extractors or string-matching gold |
| HELM Lite | Same bucket family, `gs://crfm-helm-public/lite/benchmark_output`, documented in HELM read-the-docs "Downloading Raw Results" page. | YES (same structure as Capabilities by documentation) | Documented as cross-model lite leaderboard | Multi-domain (medicine MedQA, law LegalBench, MT WMT14 etc.) | Apache-2.0 | **QUALIFIES (fallback)** — same caveat as Capabilities |
| OSWorld | HF `xlangai/ubuntu_osworld_verified_trajs` and `xlangai/ubuntu_osworld` exist; blog confirms verified trajectories migrated to HF. Dataset description claims "1000+ episodes across 15+ model variants" but HF dataset viewer is broken (schema validation error per dataset card), and per-task pass/fail matrix is not enumerated in a structured-column form. Trajectories are in zip files, parsing required. | PARTIAL — trajectories exist but per-task per-agent boolean matrix is not directly indexed | ~15 model variants claimed | 369 task definitions in repo; verified subset smaller | MIT (HF dataset card) | STILL UNCERTAIN — data plausibly there but extraction effort is non-trivial; weaker than LiveCodeBench/HELM |
| WebArena / VisualWebArena | `web-arena-x` org has 5 repos (webarena, visualwebarena, web-arena-x.github.io, synatra, webarena-infinity). Leaderboard is a Google Sheet (`docs.google.com/spreadsheets/d/1M801lEpBbKSNwP-vDBkC_pF7LdyGU1f_ufZb_NWNBZQ`) with **aggregate success rates only** (no per-task columns) across ~45 entries. WebArena code repo is Apache-2.0 with no `results/` directory. Companion `extra/webarena-zeno.ipynb` is a single-trajectory analysis notebook, not a result dump. | NO (leaderboard is aggregate; no per-task per-agent dump found) | ~45 (leaderboard rows) | 812 examples (WebArena) / 910 (VisualWebArena) | Apache-2.0 (code) | DISQUALIFIED |
| AgentBench (THUDM) | Repo Apache-2.0. Subdirs: `data/` holds task definitions (alfworld, dbbench, knowledgegraph, mind2web, os_interaction, etc.); `extra/` is docker config; no `results/`, `evaluations/`, or per-instance result dump found. Project page references a leaderboard with aggregate scores. | NO (per-task per-model pass/fail not published) | n/a (only project-level aggregate counts) | 8 environments | Apache-2.0 | DISQUALIFIED |
| LiveCodeBench | `LiveCodeBench/submissions` repo (MIT) contains **73 model directories**, each with `Scenario.codegeneration_<N>_<temp>_eval_all.json` (~30 MB). File contains 1055 questions, each entry exposing `output_list`, `code_list`, **`graded_list` (List[bool] of length N attempts)**, and `pass@1`. This is exactly the (model, task, success) triple Plimsoll's pipeline needs. | YES (explicit per-question boolean per attempt + pass@1) | 73 | 1055 questions (Codeforces / LeetCode / AtCoder competition problems with difficulty labels easy/medium/hard) | MIT | **QUALIFIES** |

## Per-candidate detail

### HELM Agents (and HELM Lite / HELM Capabilities as fallback)

- **Resolution effort:** Fetched read-the-docs `/get_helm_rank/` (404 on direct path) and `/downloading_raw_results/`; web-searched the bucket prefix; enumerated `gs://crfm-helm-public/capabilities/benchmark_output/` via the public GCS JSON API. Inspected `groups.json`, `per_instance_stats.json`, and `display_predictions.json` for both bigcodebench and mmlu_pro runs.
- **Data location:**
  - HELM Capabilities: `gs://crfm-helm-public/capabilities/benchmark_output/runs/v1.0.0/<scenario>:<config>,model=<model>/{display_predictions,instances,per_instance_stats,run_spec,scenario,scenario_state,stats}.json`
  - HELM Lite: `gs://crfm-helm-public/lite/benchmark_output` (documented in same read-the-docs page; structure parallel to Capabilities)
  - HELM Safety: `gs://crfm-helm-public/safety/benchmark_output`
  - HELM Agents: **not present** as a separate path in the documented project list (HEIM, Instruct, MedHELM, Lite, Capabilities, Safety listed; no Agents track)
- **Coverage (Capabilities v1.0.0):** 22 models per `groups.json`, 5 scenarios sampled in first GCS page (bigcodebench, gpqa, ifeval, mmlu_pro, omni_math). Mean 797 instances/scenario per `groups.json`. ~24 models surface in first 100 run-prefixes; pagination indicates more.
- **License:** Apache-2.0 (HELM framework). Per-instance JSONs are public artifacts of the framework; no separate dataset license signal found.
- **Verdict:** HELM Capabilities **QUALIFIES**. Caveat: `per_instance_stats.json` contains only operational stats (tokens, logprob, batch_size, finish_reason) and **not** correctness flags. Pass/fail must be derived by joining `display_predictions.json[*].predicted_text` with `instances.json` gold answers using HELM's metric extractors (mostly straightforward — exact match for MCQ, code-execution for bigcodebench). HELM Lite is a clean fallback with the same structure but more diverse domains.

### OSWorld

- **Resolution effort:** WebFetched repo, `os-world.github.io`, the `xlang.ai/blog/osworld-verified` post, and HF dataset `xlangai/ubuntu_osworld_verified_trajs`. Web-searched for the trajectory dataset.
- **Data location:** `huggingface.co/datasets/xlangai/ubuntu_osworld_verified_trajs` (and `windows_osworld`, `ubuntu_osworld`). Distributed as zip files of trajectory bundles.
- **Coverage:** ~15 model variants (Operator, Claude, UI-TARS, Qwen2.5-VL, Seed-1.5-VL, OpenCUA, Agent S, Jedi, GTA1, others) × ~369 OSWorld task definitions (verified subset smaller). 1000+ episodes total claimed.
- **License:** MIT (HF dataset card).
- **Verdict:** STILL UNCERTAIN. HF dataset viewer is broken; per-task per-agent boolean matrix is not surfaced as a structured column. Reconstructing it requires unzipping per-model trajectory bundles and parsing each episode's terminal evaluation. Possible but substantially more effort than LiveCodeBench (~30 MB pre-graded JSON).

### WebArena / VisualWebArena

- **Resolution effort:** Listed `web-arena-x` org (5 repos), inspected `webarena` root + `extra/`/`scripts/` subdirs, fetched the public Google Sheets leaderboard linked from the project README.
- **Data location:** Aggregate-only Google Sheet (`docs.google.com/spreadsheets/d/1M801lEpBbKSNwP-vDBkC_pF7LdyGU1f_ufZb_NWNBZQ`). No `results/` or per-instance dump in any of the 5 web-arena-x repos. Companion repo `webarena-infinity` is a task-generation tool, not a result archive.
- **Coverage:** ~45 leaderboard rows; 812 WebArena tasks / 910 VisualWebArena tasks; per-task pass/fail not exposed.
- **License:** Apache-2.0 (code).
- **Verdict:** DISQUALIFIED for Gate 0.5 (criterion 1 fails — aggregate-only).

### AgentBench (THUDM)

- **Resolution effort:** Listed root and probed `data/`, `extra/` subdirs via GitHub API.
- **Data location:** `data/` holds task definitions; `extra/` is docker config. No `results/`, `evaluations/`, or `submissions/` directory exists.
- **Coverage:** 8 environments (alfworld, dbbench, knowledgegraph, mind2web, os_interaction, lateralthinkingpuzzle, avalon).
- **License:** Apache-2.0.
- **Verdict:** DISQUALIFIED (criterion 1 fails — no per-instance dump).

### LiveCodeBench

- **Resolution effort:** Located `LiveCodeBench/submissions` repo, enumerated 73 model dirs via GitHub API, downloaded a 30 MB `Scenario.codegeneration_10_0.2_eval_all.json` for `Claude-3.5-Sonnet-20241022` and inspected schema directly.
- **Data location:** `https://raw.githubusercontent.com/LiveCodeBench/submissions/main/<MODEL>/Scenario.codegeneration_<N>_<temp>_eval_all.json`
- **Coverage:** 73 model dirs (Claude 3/3.5/3.7/Opus-4/Sonnet-4, GPT-4/4O/O1/O3/O4-Mini, DeepSeek-V3/R1, Gemini-2.5-Pro/Flash, Qwen2.5/3, Llama-3.x, plus ~30 more variants). 1055 questions sourced from Codeforces/LeetCode/AtCoder, with `difficulty` labels (easy/medium/hard) — non-trivial spread.
- **Per-instance schema (verified):**
  ```
  {question_id, contest_id, contest_date, difficulty,
   output_list, code_list,
   graded_list: List[bool],   # per-attempt pass/fail (length N)
   pass@1: float,             # 0.0..1.0
   metadata}
  ```
  This is exactly the (model, task, success) triple shape Plimsoll's paired-effect-size pipeline consumes.
- **License:** MIT.
- **Verdict:** **QUALIFIES**. Cleanest fit of all candidates. Domain is coding (different from SWE-bench Verified's repo-fix domain — competitive-programming problems vs. real-world bug fixes), so it's a genuine secondary held-out source rather than a near-duplicate.

## Recommendation

**LiveCodeBench is the strongest replacement for METR as Gate 0.5 confirmatory secondary**, and **HELM Capabilities** is a viable additional or alternative secondary. Rationale:

1. **LiveCodeBench (primary recommendation):** 73 models × 1055 tasks × explicit `graded_list` boolean is the cleanest joinable matrix found in this sweep — strictly more models than the SWE-bench Verified primary's 134 *submissions* (some sharing model bases) and a fully different task domain (competitive programming vs. repo bug fixes). MIT license. Zero-friction parse: each model dir has a single ~30 MB JSON. Difficulty labels (easy/medium/hard) are pre-supplied so the [0.30, 0.70] mean-pass-rate band can be computed immediately and cross-checked against the difficulty label as a sanity check.
2. **HELM Capabilities (secondary recommendation if a non-coding domain is wanted):** 22 models × 5 scenarios (~797 instances each) covering MCQ knowledge (mmlu_pro, gpqa), instruction-following (ifeval), math (omni_math), and code (bigcodebench). Adds domain breadth at the cost of needing a small metric-extraction pass to convert `predicted_text` → boolean correct/incorrect.
3. **METR can be deprioritized** as a Gate 0.5 secondary given LiveCodeBench's cleaner per-instance availability. (METR remains relevant if Plimsoll wants long-horizon agentic-task coverage, which LiveCodeBench does not provide.)
4. OSWorld stays on the watch list — if its HF dataset viewer is fixed and a structured per-task per-agent matrix surfaces, it would add a third domain (computer-use/desktop) for free.
5. WebArena/VisualWebArena and AgentBench should be removed from the Gate 0.5 candidate pool for this round.
