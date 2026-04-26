---
project: Plimsoll
kind: gate-0.5-inventory-supplement
cluster: NL2SQL
status: complete
updated: 2026-04-26
---

# Gate 0.5 Inventory Supplement — NL2SQL Cluster

## Summary

No NL2SQL public leaderboard surfaced that publishes per-question pass/fail data per submission across ~20+ submissions in the way SWE-bench Verified does. The strongest candidate, **BIRD-SQL**, has the right scale (1,534 dev examples, ~100+ submissions across tracks, CC BY-SA 4.0) but does not publish per-instance prediction dumps per leaderboard entry — submitters send predictions to the maintainers privately, and only aggregate execution accuracy and VES are posted. Spider 1.0 is frozen (no submissions since 2024-02-05) and was always aggregate-only. Spider 2.0 has only ~70 entries across three sub-tracks and no public per-instance prediction archive. Recommendation: do not select an NL2SQL secondary from public leaderboards; instead, either (a) pivot to a different cluster where per-instance archives exist, or (b) reproduce a BIRD-SQL multi-model evaluation locally using published per-paper artifacts as a curated mini-leaderboard (out of scope for Gate 0.5's "held-out, prospectively-pre-registerable public source" requirement).

## Candidate verdicts

| Candidate | Per-instance data? | Models | Questions | License | Verdict |
|---|---|---|---|---|---|
| Spider 1.0 | NO (aggregate only) | 83 | 1,034 dev / ~2k test | research-only, dataset under non-commercial-ish | DISQUALIFIED |
| Spider 2.0 | NO (no public per-instance dump) | ~70 across 3 sub-tracks | 632 (547 Snow / 68 DBT / 547 Lite) | Repo MIT; data license unclear | DISQUALIFIED |
| BIRD-SQL | NO (aggregate only on leaderboard; submissions held privately) | 100+ across tracks | 1,534 dev (full) / 500 mini-dev | CC BY-SA 4.0 (data) | DISQUALIFIED |
| BIRD-SQL Mini-Dev | NO (same submission flow) | subset of BIRD | 500 | CC BY-SA 4.0 | DISQUALIFIED |
| SParC | NO | ~22 (top of board) | 422 dev | CC BY-SA 4.0 | DISQUALIFIED |
| CoSQL | UNCERTAIN — likely no | small | small | CC BY-SA 4.0 (presumed) | DISQUALIFIED (size) |
| WikiSQL | NO (PapersWithCode aggregate) | many (PR-based) | ~15.8k test | BSD-3 | DISQUALIFIED |
| Defog SQL-Eval | NO (framework, not leaderboard) | N/A (run-it-yourself) | ~200 | Apache-2.0 | DISQUALIFIED |
| KaggleDBQA / Archer / Dr.Spider / Spider-DK / Spider-Realistic | UNCERTAIN — research-paper benchmarks, no central per-instance leaderboard | small | varies | varies | DISQUALIFIED (size + no leaderboard) |
| LiveSQLBench (BIRD-SQL Pro v0.5) | UNCERTAIN — contamination-controlled, very recent (2026-03) | small (early) | 480 | likely CC BY-SA 4.0 (BIRD family) | UNCERTAIN — too new, scale unverified |

## Per-candidate detail

### Spider 1.0

- **Data location:** Leaderboard at https://yale-lily.github.io/spider shows aggregate Execution Accuracy and Exact Set Match only. No per-instance prediction archive is published or linked.
- **Coverage:** 83 submissions × 1,034 dev / 2,147 test questions (200 databases, 138 domains).
- **Difficulty distribution:** Not assessed (no per-instance data available).
- **License:** Research-only / non-commercial-ish (test set held by Yale, evaluated via CodaLab).
- **User prior work:** None (only adjacent NL2SQL work via Pruned Context custom benchmark).
- **Verdict & rationale:** **DISQUALIFIED.** Two independent fatal flaws: (1) aggregate-only public results, no per-question dumps anywhere, and (2) submissions stopped 2024-02-05 — the leaderboard is frozen, so no fresh held-out window exists for pre-registration. Even reconstructing per-instance data from individual papers would be retrospective, not prospectively pre-registerable.

### Spider 2.0

- **Data location:** Leaderboard at https://spider2-sql.github.io/. Submission spec (CSV per database — bq_001.csv, sf_001.csv, snow_001.csv plus metadata.json) implies submissions could in principle contain per-instance data, but the leaderboard page does not surface per-submission prediction archives. GitHub repo (https://github.com/xlang-ai/Spider2) does not host them either.
- **Coverage:** ~70 entries spread across Spider 2.0-Snow (547), Spider 2.0-DBT (68), Spider 2.0-Lite (547). Each sub-track is below the ~20-overlapping-models target once you condition on a single sub-track.
- **Difficulty distribution:** Not assessed.
- **License:** Repo is MIT; data license not surfaced on landing page.
- **User prior work:** None.
- **Verdict & rationale:** **DISQUALIFIED.** Even if per-instance CSVs were retrievable from each submitter privately, the leaderboard does not centrally publish them. Sub-track entry counts (~20-30 each) sit at the lower edge of the threshold and any [0.30, 0.70] pass-rate band would have weak support given the very low overall solve rates reported on Spider 2.0 (most models <30% accuracy, which collapses the band).

### BIRD-SQL (full + mini-dev)

- **Data location:** Leaderboard at https://bird-bench.github.io/. Submitters send predictions in `SQL\t----- bird -----\tdb_id` format to maintainers (per `mini_dev/README.md` and BIRD GitHub `llm/exp_result/` examples), but only aggregate Execution Accuracy / VES / Soft-F1 / R-VES are posted publicly. Code repo at https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird contains baselines only, not third-party submission archives.
- **Coverage:** Dev set 1,534 examples; Mini-Dev 500. Leaderboard has 100+ entries across Overall / Single-Model / Mini-Dev tracks.
- **Difficulty distribution:** BIRD has documented difficulty bands (simple/moderate/challenging) but per-question solve rates per submission are not published.
- **License:** **CC BY-SA 4.0** — permits re-analysis and redistribution with attribution + share-alike. (Best license among candidates.)
- **User prior work:** **YES (partial).** Jig project ran a single-judge accuracy / FAR analysis on BIRD-SQL using Sonnet as a judge (Exp 1, McNemar p<0.001). That work was about judge calibration, not multi-model paired-effect-size capability filtering, so it does not "pollute" Plimsoll's analysis methodologically — but the user has touched this benchmark before, and the methodological frame would need to be unambiguous.
- **Verdict & rationale:** **DISQUALIFIED on per-instance data.** This is the closest miss: license is right, scale is right, leaderboard is active and growing. The kill is that per-submission per-question pass/fail is not a public artifact — it lives only with maintainers and individual paper authors. Reconstructing it would require contacting ~20+ submitters individually, which violates the "held-out, prospectively-pre-registerable public source" gate. (A separate, narrower BIRD-based study using the user's own multi-model runs is feasible but is a different artifact than what Gate 0.5 wants.)

### SParC / CoSQL

- **Data location:** Yale leaderboards. Aggregate metrics only.
- **Coverage:** ~22 entries (SParC), most recent 2022. CoSQL similar or smaller.
- **Difficulty distribution:** Not assessed.
- **License:** CC BY-SA 4.0 (SParC confirmed; CoSQL presumed same family).
- **User prior work:** None.
- **Verdict & rationale:** **DISQUALIFIED.** Aggregate-only, dormant, and below the 20-submission threshold (SParC at the cusp; CoSQL likely below).

### WikiSQL

- **Data location:** PapersWithCode and salesforce/WikiSQL repo via PR. Aggregate metrics only.
- **Coverage:** ~15,878 test questions; many submissions historically.
- **Difficulty distribution:** Not assessed; WikiSQL questions are largely simple single-table SELECT, so [0.30, 0.70] band support is weak (most modern models saturate well above 0.70).
- **License:** BSD-3 (data).
- **User prior work:** None.
- **Verdict & rationale:** **DISQUALIFIED.** Aggregate-only, and saturation of modern LLMs above 0.85+ EX collapses the [0.30, 0.70] band.

### Defog SQL-Eval

- **Data location:** https://github.com/defog-ai/sql-eval — code-and-data harness, not a leaderboard. Per-instance CSV results are produced by anyone who runs it locally.
- **Coverage:** ~200 questions. No central leaderboard with ≥20 submissions of per-instance results.
- **License:** Apache-2.0.
- **User prior work:** None.
- **Verdict & rationale:** **DISQUALIFIED.** This is a benchmark framework, not a leaderboard. Anyone could run it, but the "≥20 submissions with overlapping task coverage" criterion fails because no central archive of per-model per-question results exists. (Could be used as a self-run benchmark for a different study, but not for Gate 0.5's held-out pre-registerable secondary.)

### Variants (KaggleDBQA, Archer, Dr.Spider, Spider-DK, Spider-Realistic, BIRD-SQL Mini-Dev)

- **Data location:** Each is a single-paper benchmark with no live multi-submission leaderboard.
- **Coverage:** Most have <500 questions and <10 evaluated models in the originating paper.
- **License:** Various, mostly research-only.
- **User prior work:** None.
- **Verdict & rationale:** **DISQUALIFIED.** None has a public multi-submission per-instance leaderboard at the required scale.

### LiveSQLBench (BIRD-SQL Pro v0.5)

- **Data location:** https://livesqlbench.ai/ — contamination-controlled rolling benchmark in the BIRD family, March 2026 release of LiveSQLBench-Large-v1 (480 tasks, ~1k columns).
- **Coverage:** Too new to assess submission count or per-instance availability.
- **Difficulty distribution:** Not assessed.
- **License:** Likely CC BY-SA 4.0 (BIRD family).
- **User prior work:** None.
- **Verdict & rationale:** **UNCERTAIN — could not locate per-instance data file.** Worth a follow-up check in 1-2 months if the leaderboard fills out and per-instance dumps appear. Currently too thin and too recent to qualify.

## Recommendation

**No NL2SQL candidate qualifies as a Plimsoll Gate 0.5 confirmatory secondary** under the stated selection criteria.

The methodological gap is structural, not accidental: NL2SQL leaderboards in 2026 universally treat per-instance predictions as proprietary submission artifacts held by maintainers (Spider, BIRD) or by individual paper authors (variants), and publish only aggregate metrics. This is the inverse of SWE-bench Verified, where every submission ships its trajectory + per-instance pass/fail JSON to a public archive.

**Suggested next step:** Look for a Plimsoll secondary in a cluster where per-instance archives are routine — e.g., agentic coding (HumanEval+ / MBPP+ via BigCode harness has per-instance dumps; LiveCodeBench has per-problem-per-model Parquet exports), reasoning benchmarks (MATH / GPQA via lm-eval-harness if archives exist), or revisit Ndzomga 2026's 8 agentic benchmarks for one not already in the primary. If an NL2SQL secondary is essential for thematic balance, the only viable path is to **commission a multi-model BIRD-SQL run locally** (CC BY-SA 4.0 permits it) — but that produces a self-generated artifact, not a held-out public secondary, and would need a different framing in the pre-registration.

If the user wants to revisit LiveSQLBench in ~Q3 2026 once it has filled out, that is the only NL2SQL candidate with a non-zero forward probability of qualifying.
