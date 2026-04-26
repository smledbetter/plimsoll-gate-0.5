---
project: Plimsoll
kind: gate-0.5-component-b
status: superseded-secondary (primary still current)
updated: 2026-04-26
---

# Gate 0.5 Component B — Held-Out Leaderboard Inventory

> **Status note (2026-04-26):** This inventory's **primary recommendation (full SWE-bench Verified) stands.** The **secondary recommendation (METR Time Horizon) was superseded** later the same day by a four-cluster supplemental fan-out (`gate-0.5/inventory-supplement/`) that surfaced two stronger candidates: **LiveCodeBench** (MIT-licensed, 73 submissions, 1055 questions, double-confirmed) and **MMLU-Pro** (Apache + MIT licenses, 48 models, 12,032 questions, 14 disciplines). The current Gate 0.5 design uses three sources — SWE-bench primary + LiveCodeBench (code) + MMLU-Pro (scope) — with a layered decision rule per `gate-0.5/README.md`. METR is retained only as fourth-source insurance.

## Selection summary

**Recommended primary:** `swe-bench/experiments` (full SWE-bench Verified leaderboard, 134 submissions × 500 instances). It publishes per-instance pass/fail (`results/results.json` listing `resolved` / `no_generation` / `no_logs` instance IDs per submission) and is genuinely held-out from Ndzomga's set — Ndzomga has only `swebench_verified_mini` (50 of the 500 instances, 28 of the 134 agents). License is the only blemish: the repo has no LICENSE file (default copyright; permission to re-analyze the *list of resolved IDs* is plausibly fair-use as facts about a public leaderboard, but worth flagging in the OSF registration).

**Confirmatory secondary:** METR `eval-analysis-public` Time Horizon 1.1 (`reports/time-horizon-1-1/data/raw/runs.jsonl`, 21 agents × 228 tasks, score_binarized field). Different domain (research-engineering / HCAST / SWAA), different agent population, different scoring methodology — strong independent confirmation if the primary clears, and immune to any SWE-bench-specific concerns.

If both clear, the headline goes from "ranks preserved, effects collapse on Ndzomga" to "...and on two independent held-out sources spanning two distinct task families." If either fails, the verdict is honestly reported per the gate-0.5 decision rule.

## Candidate verdicts

| Candidate | Per-instance data? | Agents | Tasks | License | In Ndzomga's set? | Verdict |
|---|---|---|---|---|---|---|
| HELM Agents | UNCERTAIN — could not confirm direct download URL | unknown | unknown | unclear | no | UNCERTAIN |
| Full SWE-bench Verified (`swe-bench/experiments`) | yes — `results/results.json` per submission | 134 | 500 | none / unlicensed | partial (Ndzomga has 50-task mini × 28 agents) | QUALIFIES |
| OSWorld leaderboard | UNCERTAIN — repo has 369 task definitions but no per-agent results dump confirmed | unknown | 369 | Apache-2.0 (code repo) | no | UNCERTAIN |
| WebArena / VisualWebArena | UNCERTAIN — code repo Apache-2.0, no `results/` directory found | unknown | unknown | Apache-2.0 (code) | no | UNCERTAIN |
| METR RE-Bench / Time Horizon 1.1 (`eval-analysis-public`) | yes — `runs.jsonl` per task per model with `score_binarized` | 21 | 228 (incl. RE-Bench, HCAST, SWAA) | none / unlicensed | no | QUALIFIES |
| Ndzomga sources, current snapshot | yes per source, but adds only ~4 SWE-bench agents post-cut | small delta | same | source-dependent | yes (by definition) | DISQUALIFIED as primary; available as fallback |
| BFCL (`BFCL-Result`) | yes — per-test-case JSON with `valid` field | 115 (latest dated dir) | thousands of test cases (multiple subcategories) | none / unlicensed | no | QUALIFIES (with caveats on domain + license) |
| Aider polyglot | UNCERTAIN — webpage shows aggregate only, raw per-task data not surfaced | ~60+ | 225 | unclear | no | UNCERTAIN |
| LiveCodeBench | UNCERTAIN — leaderboard JS-rendered, repo has scaffold but per-instance result dumps not located | unknown | unknown | unclear | no | UNCERTAIN |
| AgentBench (THUDM) | UNCERTAIN — Apache-2.0 repo but no per-instance result dump located | unknown | unknown | Apache-2.0 (code) | no | UNCERTAIN |

## Per-candidate detail

### HELM Agents (Stanford CRFM)

- **Data location:** UNCERTAIN. Documentation references `storage.googleapis.com/crfm-helm-public/benchmark_output/...` (per `crfm-helm.readthedocs.io/en/latest/get_helm_rank/`), but direct probes of plausible paths (`/lite/benchmark_output/runs/v1.0.0/`, `/benchmark_output/archives/`) returned 404. The HELM website lists tracks (lite, capabilities, etc.) but the read-the-docs page that documents the bucket layout returned 404 on this fetch. A working URL pattern probably exists but wasn't pinned down within the time-box. Could not confirm a HELM "Agents" track separate from core capabilities.
- **Coverage:** unknown without resolving the data location.
- **Difficulty distribution:** not assessed.
- **License:** HELM code is Apache-2.0; data licensing per scenario varies (each underlying benchmark has its own license).
- **Overlap with Ndzomga:** no — Ndzomga's 8 benchmarks (swebench_verified_mini, corebench_hard, usaco, gaia, online_mind2web, taubench_airline, assistantbench, scicode) do not appear on the HELM Lite/Capabilities tracks.
- **Verdict & rationale:** UNCERTAIN — could not locate per-instance data file in budget. If pursued as fallback, the read-the-docs page on HELM rank reproduction is the doorway; a 5-minute follow-up should resolve the bucket path. Not recommended as primary because the time cost is unknown and the SWE-bench primary is already strong.

### Full SWE-Bench Verified leaderboard — `swe-bench/experiments`

- **Data location:** `https://github.com/swe-bench/experiments/tree/main/evaluation/verified/<date>_<model>/results/results.json`. Each submission's `results.json` is a JSON object with three keys: `resolved` (list of instance_ids the agent passed), `no_generation` (list of instance_ids the agent failed by producing no patch), `no_logs` (list of instance_ids with execution issues). Reconstruction of the full (agent, task, success) triple matrix is straightforward: enumerate the 500 SWE-bench Verified instance IDs, mark each as 1 if in `resolved`, else 0.
- **Coverage:** 134 submissions in `evaluation/verified/` (verified by GitHub API contents listing on 2026-04-26), spanning 2023-10 through 2025-12-15 (latest: `20251215_livesweagent_claude-opus-4-5`). SWE-bench Verified has 500 task instances. Spot-check on `20251215_livesweagent_claude-opus-4-5/results/results.json`: 318 resolved, 4 no_generation, 1 no_logs (so 318 / ~500 resolved, ~64% pass rate — high but not ceiling). Spot-check on older `20241022_tools_claude-3-5-sonnet-updated`: 14 no_generation IDs visible. Plenty of difficulty spread across the 134-agent population.
- **Difficulty distribution:** not directly computed in this inventory, but task-level pass-rate variance across 134 submissions ranging from rag_swellama7b (very low) to opus-4-5 (~64%) guarantees a non-trivial fraction of tasks land in the [0.30, 0.70] capability-margin band. The "subset of 50 mid-range tasks preserves rank" finding from Ndzomga's mini variant is direct evidence the band has support.
- **License:** **none** (no LICENSE file in repo). The data is publicly hosted on GitHub by the SWE-bench team (Princeton NLP / John Yang et al.), and the repo's purpose is to enable third-party reproducibility ("These logs are publicly accessible and meant to enable greater reproducibility and transparency"). Re-analysis of the lists of resolved instance IDs is plausibly fair-use of factual data, but a defensive move would be to email maintainers (or open an issue) for explicit re-analysis permission before OSF registration. Note: as of 2025-11-18 SWE-bench restricted *new submissions* to academic/research labs, but this does not affect re-analysis of existing public results.
- **Overlap with Ndzomga:** **partial.** Ndzomga's `swebench_verified_mini` is 50 instances × 28 agents (per the heatmap CSV). The full Verified leaderboard is 500 instances × 134 agents. The held-out portion is the **450 Verified instances Ndzomga did not include × all 134 agents**, plus the **50 mini instances × 106 agents Ndzomga did not include**. Overall, Ndzomga touched `50 × 28 = 1,400` cells of a `500 × 134 = 67,000`-cell matrix — i.e. ~98% held-out by cell count. Ndzomga's data has download_timestamp 2025-11-17; SWE-bench experiments has continued accruing through 2025-12-15 (4-5 new agents post-cut).
- **Verdict & rationale:** **QUALIFIES.** Best-in-class candidate by every selection criterion except license (and the license issue is mitigable with an email or fair-use argument). Per-instance data is unambiguously published, agent count and task count both clear the thresholds by a large margin, the data is genuinely held-out from Ndzomga's analysis, and there's enough difficulty spread to populate the [0.30, 0.70] band. Recommended as **primary**.

### OSWorld leaderboard

- **Data location:** Repo `xlang-ai/OSWorld` has `evaluation_examples/` with 369 task definitions (`test_all.json`, `test_small.json`, etc.), but a sweep of the repo top-level did not surface a `results/` or `leaderboard/` directory with per-agent per-task pass/fail. Trajectories are referenced as "hosted on Hugging Face" but the structure of those (whether they include success labels per task per agent) wasn't verified in this pass.
- **Coverage:** 369 tasks confirmed (361 if the 8 Google Drive tasks are excluded). Agent count from the leaderboard webpage was not extractable in the time-box.
- **License:** Apache-2.0 (code repo). Data license per HF dataset would need separate check.
- **Overlap with Ndzomga:** no (not in his 8 benchmarks).
- **Verdict & rationale:** UNCERTAIN — could not confirm a per-agent per-task pass/fail dump within budget. Worth ~10 more minutes of follow-up if the SWE-bench primary plus METR secondary aren't enough. The HF trajectories may contain the data but require download + parsing.

### WebArena / VisualWebArena

- **Data location:** Repo `web-arena-x/webarena` is the agent code repo; no `results/` directory at top level. The companion leaderboard webpage (webarena.dev) lists projects but doesn't expose per-instance data via a CSV/JSON. Individual papers report per-template aggregate metrics, not per-task per-agent.
- **Coverage:** not confirmed.
- **License:** Apache-2.0 (code repo).
- **Overlap with Ndzomga:** no.
- **Verdict & rationale:** UNCERTAIN — could not locate a per-instance per-agent dump. WebArena's evaluation publishes aggregate scores in papers; a per-instance dataset across many agents would need to be reconstructed from individual paper releases. Not recommended for Gate 0.5 primary or secondary.

### METR RE-Bench / Time Horizon — `METR/eval-analysis-public`

- **Data location:** `https://github.com/METR/eval-analysis-public/blob/main/reports/time-horizon-1-1/data/raw/runs.jsonl` (24,008 lines) and `reports/time-horizon-1-0/data/raw/runs.jsonl`. Each line is a JSON object with `task_id`, `task_family`, `alias` (model name), `score_binarized` (0/1), `score_cont`, `human_minutes`, etc.
- **Coverage:** 21 unique agent aliases × 228 unique task IDs (across 79 task families) in Time Horizon 1.1. Task suite includes RE-Bench (7 ML research-engineering environments), a subset of HCAST, and SWAA short tasks. Multiple runs per (agent, task) cell are present (24,008 rows / 21×228 ≈ 5 runs per cell), which means per-task pass rates are stable estimates rather than single observations.
- **Difficulty distribution:** not directly computed here, but the suite spans tasks from "few seconds" (SWAA) to "8 hours of human expert time" (RE-Bench), so the difficulty range is much wider than Ndzomga's typical benchmark — strong support for a [0.30, 0.70] band.
- **License:** **none** (no LICENSE file detected; GitHub API license endpoint returned None). METR has historically published research artifacts under permissive terms but this specific repo lacks an explicit LICENSE file. Worth flagging in OSF registration; an email to METR (`info@metr.org`) for re-analysis confirmation is cheap.
- **Overlap with Ndzomga:** no — METR's HCAST/SWAA/RE-Bench suite is entirely separate from Ndzomga's 8 benchmarks.
- **Verdict & rationale:** **QUALIFIES.** Excellent secondary because (a) it's a totally different agent benchmark family from SWE-bench (research engineering and general agentic tasks rather than code patching), (b) the data format is cleaner than SWE-bench experiments (one row per run rather than sparse instance-ID lists), (c) the multi-run-per-cell design gives more stable per-task pass-rate estimates than a single attempt, and (d) it intersects with the active METR Time Horizon line of work, which gives Plimsoll a real adjacency to a current research conversation. Agent count (21) is just at the threshold; not strong enough alone but excellent as confirmatory.

### Ndzomga sources, current snapshots

- **Data location:** Same as Ndzomga's repo, but pulled fresh from each upstream leaderboard.
- **Coverage:** Ndzomga's cut date is **2025-11-17** (uniform `download_timestamp` across all 22,303 rows of `all_benchmarks_task_heatmap_data.csv`). Spot-checking SWE-bench Verified: only ~4-5 new agents added between 2025-11-17 and 2025-12-15. Other benchmarks (USACO, GAIA, etc.) likely accrue at similar low rates. The post-cut delta is too small to be a primary held-out set.
- **License:** source-dependent (Ndzomga's MIT applies to the aggregation, not the upstream data).
- **Overlap with Ndzomga:** by definition — these are his sources.
- **Verdict & rationale:** **DISQUALIFIED** as primary because the post-cut delta is too small (≤ ~5 new agents per benchmark) to give power for the median-|Δ| statistic. Available as a fallback per the gate-0.5 README open question, but the SWE-bench Verified primary recommendation is cleaner since the held-out portion (450 instances × 106 agents not in Ndzomga's mini) is enormous.

### BFCL — Berkeley Function Calling Leaderboard (`HuanzhiMao/BFCL-Result`)

- **Data location:** `https://github.com/HuanzhiMao/BFCL-Result/tree/main/2025-12-16/score/<model>/<category>/BFCL_v4_<test_category>_score.json`. Each line in a score JSON is one test case with `id`, `model_name`, `test_category`, `valid` (true/false), error details, prompt, and answer. The first line of each file is an aggregate summary (`accuracy`, `correct_count`, `total_count`).
- **Coverage:** 115 model directories in the latest dated snapshot (`2025-12-16/score/`). Categories: `agentic`, `format_sensitivity`, `live`, `multi_turn`, `non_live`. Spot-check on Claude Opus 4.5 `non_live`: 7 sub-files (simple_python, simple_java, simple_javascript, multiple, parallel, parallel_multiple, irrelevance) totaling ~400 test cases for `simple_python` alone. Total test cases across all categories likely in the low thousands.
- **Difficulty distribution:** not directly assessed, but spot-check on Claude Opus 4.5 simple_python shows 375/400 pass (93.75%), which is at the high end. Lower-capability models (e.g. small open-weight models) on harder categories like `multi_turn` will populate the [0.30, 0.70] band. Worth a difficulty-distribution sanity check before committing.
- **License:** **none** (no LICENSE file). Parent repo `ShishirPatil/gorilla` is Apache-2.0; whether that umbrella applies to the daughter results repo is unclear.
- **Overlap with Ndzomga:** no.
- **Verdict & rationale:** **QUALIFIES** with caveats. Strengths: huge agent count (115 models), per-instance data unambiguously published, very different domain from SWE-bench. Weaknesses: (a) the gate-0.5 README itself flags BFCL as "narrow domain; may not generalize" — function-calling correctness is a single skill axis, which works against the "multidimensional skill structure" theoretical anchor in Component A; (b) license unclear; (c) pass rates are skewed high on the populated subcategories, so [0.30, 0.70] support depends on category mix. Recommended as a **tertiary** option if the SWE-bench primary or METR secondary are blocked.

### Bonus candidates checked

- **AgentBench (THUDM):** Apache-2.0 code repo, but a sweep of `THUDM/AgentBench` top-level did not surface a per-instance per-model results dump. UNCERTAIN.
- **LiveCodeBench:** Repo `LiveCodeBench/LiveCodeBench` has runner code but the leaderboard webpage is JS-rendered; per-instance per-model results not located in budget. UNCERTAIN.
- **Aider polyglot:** Aggregate-only on the public leaderboard page; raw per-task results not located. UNCERTAIN.
- **τ-Bench retail:** Ndzomga has `taubench_airline` only. Retail variant exists; data location not pursued (would expand the agent set marginally given tau-bench's small agent pool).

## Recommendation

**Primary held-out source for Gate 0.5 Component C: Full SWE-bench Verified via `swe-bench/experiments`.**

Data fetch:

```bash
# Clone the experiments repo (~340 MB)
git clone https://github.com/swe-bench/experiments.git
# For each submission folder under evaluation/verified/, parse results/results.json
# Build a (agent, instance_id, success) triples table:
#   - For each submission directory D in evaluation/verified/:
#     - Read D/results/results.json
#     - For each instance_id in the canonical SWE-bench Verified 500-instance list:
#       - success = 1 if instance_id in resolved, else 0
#       - emit (D-name, instance_id, success)
# Canonical instance list: princeton-nlp/SWE-bench-Verified on HuggingFace
```

Preprocessing notes:
1. The `no_logs` category is ambiguous (execution failures, not necessarily agent failures). Pre-register the rule: treat `no_logs` as failure (conservative, matches leaderboard scoring) OR exclude those instance_ids per agent (leniency). Default: treat as failure, sensitivity-check by exclusion.
2. The 134 submissions include some that share base scaffold + different model — pre-register whether to treat as 134 distinct "agents" or to deduplicate (e.g. keep most recent per scaffold). Default: treat as 134 distinct, since Plimsoll's claim is about (agent, task) pairs, not (scaffold, model) factorization.
3. License: open a SWE-bench issue or email Princeton NLP / John Yang for re-analysis confirmation before the OSF registration timestamp. If they decline, fall back to METR secondary as the new primary (strict interpretation of "no license = no permission").

**Confirmatory secondary: METR Time Horizon 1.1 via `METR/eval-analysis-public`.**

Data fetch:

```bash
git clone https://github.com/METR/eval-analysis-public.git
# Use reports/time-horizon-1-1/data/raw/runs.jsonl directly
# 24,008 rows, ~21 agents x ~228 tasks x ~5 runs/cell
# For (agent, task, success) triples: aggregate runs per cell to get pass rate (or use score_binarized as the per-run outcome and treat rows as paired observations)
```

Preprocessing notes:
1. Multiple runs per cell — pre-register aggregation rule (mean of `score_binarized`, or median, or any-pass — Plimsoll uses mean per task across agents already, so per-cell mean of runs is the natural extension).
2. Pre-register inclusion rule for the SWAA short-task subset: include all, or only RE-Bench + HCAST. Default: include all (228 tasks gives more power; difficulty spread is wider).

**Decision tree:**
- If primary clears (median |Δ| ≥ 0.05 AND null-baseline z ≥ 3) AND secondary clears: Gate 0.5 verdict = clear, with two-source replication noted.
- If primary clears AND secondary fails: report both honestly, primary verdict carries Gate 0.5 (gate decision rule is on the chosen source). Discuss the divergence in the paper.
- If primary fails: Gate 0.5 fails per decision rule. Report secondary as exploratory texture, do not use it to rescue the verdict.

## If nothing qualifies — fallbacks

The above qualifies, so this section is contingency only.

1. **Current snapshot of Ndzomga sources, post-cut delta only.** Per the gate-0.5 README open question (option 1). Drawback: ~4-5 new agents per benchmark gives weak power. Use only if SWE-bench and METR are both blocked on license.
2. **Non-agent benchmarks (HELM core, MMLU-Pro, etc.) and reframe Gate 0.5 as "generalizes beyond agent eval."** Per gate-0.5 README option 2. HELM Lite has the data format (per-instance JSON downloadable via the GCS bucket once the URL is pinned down) and dozens of models on dozens of scenarios. Reframing weakens the headline because the original Plimsoll claim is about agent eval specifically — but it preserves the methodology paper.
3. **Small fresh-data study within $50 budget.** Per gate-0.5 README option 3. Run 20+ open-weight models (via OpenRouter / vLLM on VPS) on a 50+ task subset with built-in difficulty stratification. Total budget realistic for ≤$50 if models are small and tasks are short (e.g. BIG-Bench Hard, ARC-AGI tasks, or a custom mid-difficulty SQL set). Drawback: bespoke data collection introduces analyst-degrees-of-freedom that the held-out replication is supposed to retire.

Recommended fallback order, given budget and orthodoxy: try the SWE-bench license email first (cheap, fast, almost certainly granted); if it fails, METR-only as primary; if METR is also blocked, BFCL as primary with the "narrow domain" caveat acknowledged in the OSF registration.
