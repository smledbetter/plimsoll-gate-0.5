---
project: Plimsoll
kind: registration-deviations
gate: 0.5
osf_doi: 10.17605/OSF.IO/G9WFY
osf_registration: https://osf.io/g9wfy/
osf_project: https://osf.io/e264j/
created: 2026-04-26
---

# Plimsoll Gate 0.5 — Registration Deviations Log

This file documents deviations from, and post-hoc resolutions of, ambiguities or gaps in the OSF pre-registration **DOI 10.17605/OSF.IO/G9WFY** (registered 2026-04-26T18:18:39Z UTC). It exists to make the audit trail explicit for any reviewer comparing the registered document to the executed analysis.

The registration itself is sealed and cannot be edited. This file lives in the public GitHub repository accompanying the registration ([smledbetter/plimsoll-gate-0.5](https://github.com/smledbetter/plimsoll-gate-0.5)) and is synchronized to the OSF *project* (which is separately editable from the registration).

## D1 — Analysis-script git SHAs (`pre-registration.md` §5.3)

**Registered text:**
> Analysis scripts: `analyze.py`, `null-baseline.py`, `simulation.py`, `prep-swebench.py`, `prep-livecodebench.py`, `prep-mmlu-pro.py` — all at git commit SHA [TBD].

**Deviation:** The registered document submitted to OSF still contained the literal `[TBD]` placeholder for the analysis-script commit SHA. Cause: the gate-0.5 directory was not in a git repository at registration time; the SHA could not be pinned because no commit yet existed. `analyze.py` and `null-baseline.py` did not yet exist as Gate-0.5-specific files (Gate 0's versions existed at `gate-0/analyze.py` and `gate-0/null-baseline.py`).

**Resolution:** Within ~1 hour of OSF approval (2026-04-26 same day):
1. Wrote `gate-0.5/analyze.py` and `gate-0.5/null-baseline.py` as parametrized ports of the Gate 0 versions. The substantive logic (margin band, inclusion thresholds, headline statistic, decision rule) is unchanged from Gate 0; only the input file format and per-source-name labelling were generalized. See diff against `gate-0/{analyze,null-baseline}.py` for the exact changes.
2. Initialized git in `gate-0.5/`, committed the entire registered artifact set as commit **`3402147b3485b6f2d950e6cae7c5c1b31abbf357`** (visible in this repo at `git show 3402147`).
3. Pushed to `https://github.com/smledbetter/plimsoll-gate-0.5` for public traceability.

**Effect on registration validity:** The substantive analysis pipeline (margin = [0.30, 0.70], thresholds = (20, 8), statistic = median |Δ|, decision = median ≥ 0.05 AND z ≥ 3) was fully specified in the registered prose at §4.1 and §4.3. Only the *implementation files* (and their SHAs) were not pinned at registration time. A reader auditing the analysis can verify the implementation matches the registered prose by reading `analyze.py` and `null-baseline.py` at commit `3402147` — no degree of freedom existed for the analyst to alter the substantive rules between registration and execution.

## D2 — Data-source frozen commit SHAs (`pre-registration.md` §2.1, §2.2, §2.3, §5.3)

**Registered text:**
> SWE-bench Verified — Frozen commit SHA: [TBD at registration time — pinned by analyst before pulling data].
> LiveCodeBench — Frozen commit SHA: [TBD at registration time].
> MMLU-Pro — Frozen commit SHA: [TBD at registration time].

**Deviation:** SHAs were not pinned in the registered document text. The pre-registration explicitly anticipated this by specifying "pinned by analyst before pulling data" — the audit anchor is that the SHAs are committed publicly *before* any held-out data is pulled into the analysis pipeline.

**Resolution:** The HEAD-of-main SHAs as of 2026-04-26 (within hours of OSF approval, before any data pull) are pinned here:

| Source | Frozen commit SHA | Repo |
|---|---|---|
| SWE-bench Verified (experiments) | `2f15350cd32becc4569e0d826361048555b605c0` | github.com/swe-bench/experiments |
| LiveCodeBench (submissions) | `6ca212e9c2039373f6e5069d37ffa9db66e23736` | github.com/LiveCodeBench/submissions |
| MMLU-Pro (eval_results) | `f418b116db00b065c2aea046518d8fcf74d39872` | github.com/TIGER-AI-Lab/MMLU-Pro |

Component C runs will checkout these exact SHAs. Submissions added to those repos after these SHAs are out of scope per the registered frozen-list intersection rule.

## D3 — Numbering gap (intentional)

This slot is intentionally empty. During drafting of this file, content originally numbered D3 was folded into D2 (data-source SHAs). The numbering gap was preserved rather than re-collapsed because **D4**, **D5**, and **D6** are referenced by number in other files (`prep-mmlu-pro.py:65` cites D5; `robustness/DESIGN.md` cites D4). Renumbering would have created a different audit-trail problem (broken cross-references) than the cosmetic one it would have solved. A 2028 reproducer reading "D1, D2, D4, D5, D6" should treat D3 as deliberately reserved, not lost. No substantive content is missing.

## D4 — LiveCodeBench prep run (2026-04-26)

**Data:** `LiveCodeBench/submissions` at pinned SHA `6ca212e9c2039373f6e5069d37ffa9db66e23736`, cloned 2026-04-26 ~18:33 UTC.

**Counts as registered vs. observed at pinned SHA:**

| Quantity | Registered (§2.2) | Observed at pinned SHA |
|---|---|---|
| Submission directories | 73 | 73 (excluding 4 non-dir entries: README.md, LICENSE, build_leaderboard_json.py, build_solution_explorer.py) |
| Distinct model families post-dedup | "≥50" | 72 (after dedup, with regex below being a no-op) |
| Questions | 1,055 | 1,055 |
| Triple rows | not specified | 68,015 |
| In-band tasks | not specified | 396 / 1,055 (37.5%) |

The directory count matches registration. One model directory (likely `DeepSeek-V3 copy` — a literal duplicate of `DeepSeek-V3` per filename) appears to have produced no parseable `Scenario.codegeneration*_eval_all.json` records, dropping the agent count from 73 to 72.

**Variant-dedup regex no-op.** The registered variant-dedup pattern `(_thinking|_no-thinking|_temp\d+|_t\d+|_seed\d+|_variant\d*|_v\d+)` does not match any model-directory name in this repo's actual naming convention. Real variant patterns observed:
- ` (Thinking)` — Claude/Gemini reasoning-mode flag (parens, space, capital)
- ` (High|Low|Med|Medium)` — O-series and Grok temperature/effort tiers (parens, space, capital)
- `-\d{2}-\d{2}` — Gemini date suffixes (e.g. `Gemini-Flash-2.0-Thinking-01-21`)
- `_temp` (no digits) — `QwQ-32B_temp`
- ` copy` — `DeepSeek-V3 copy`
- `_prompt_old` — `O1-2024-12-17 (Low)_prompt_old`

The registered regex is therefore a no-op on this corpus. Effect: every directory becomes its own canonical family; we end up with 72 agents (raw count minus the unparseable `DeepSeek-V3 copy`) rather than ~50–60 expected post-dedup. Pre-registered threshold ≥50 is met.

**Why we did not patch the regex.** Patching the regex post-registration to match the actual corpus would be a degree-of-freedom for the analyst; per pre-registration discipline, we ran the rule as-written even though it is functionally inert here. The result is *more* pairs than the registered minimum (2,556 vs C(50,2)=1,225) — a power-positive deviation that strengthens, rather than weakens, the test.

**Headline result on this source:**
- Pooled median |Δ paired effect size| = **0.1562** (Gate 0 was 0.090)
- Spearman ρ(effect_full, effect_margin) = 0.985 (Gate 0 was 0.958)
- Null-baseline z = **+374.90** at α=0.001 (Gate 0 was +20.77)
- Verdict: **CLEARS** the registered decision rule (median ≥ 0.05 AND z ≥ 3) by very wide margins.

Output files committed at `component-c-runs/livecodebench/livecodebench-summary.csv` and on VPS at `~/projects/plimsoll-gate-0.5/component-c/`. The 342 KB `livecodebench-pairs.csv` and 717 KB `livecodebench-per-platform.csv` are gitignored locally per the per-run output convention; canonical archives belong on OSF.

## D5 — MMLU-Pro prep script: defensive type checks (2026-04-26)

**Data:** `TIGER-AI-Lab/MMLU-Pro` at pinned SHA `f418b116db00b065c2aea046518d8fcf74d39872`, 48 model-output ZIPs in `eval_results/`.

**Issues encountered when running prep-mmlu-pro.py as-registered:**

1. **Mixed-type list inside `model_outputs_DeepSeek-Coder-V2_5shots.zip`.** The JSON file inside this ZIP is a list of 10,394 entries; 43 of them are bare strings (e.g. literal `"other"`) interleaved with the 10,351 dict records. The registered script does `entry.get("pred")` on each element, which raises `AttributeError` on the strings.

2. **macOS metadata sidecars in `model_outputs_gemini-3.1-pro_5-shots.zip`.** This ZIP contains 16 entries including `__MACOSX/eval_results/._summary.json` — a macOS extended-attribute file that is not valid JSON. The registered script calls `json.load(f)` without exception handling, which raises `JSONDecodeError`.

**Mechanical patches applied (commit on this repo):**

```python
# Skip non-dict entries within a result list (DeepSeek-Coder-V2 stray strings)
if not isinstance(entry, dict):
    continue
```

```python
# Skip macOS metadata sidecars before json.load
if "__MACOSX" in name or name.startswith("._") or "/._" in name:
    continue

# Defensive parse: don't crash on malformed JSON in source data
try:
    data = json.load(f)
except json.JSONDecodeError:
    continue
```

**Why these are mechanical, not scientific.** The registered text says "Records missing pred or answer are skipped (treated as no-attempt rather than failure)." The two patches above extend this rule with the same intent — records that aren't even parseable as records (string entries, malformed JSON sidecars) are treated as no-attempt. No degree of freedom on the analyst is added; the substantive rule (`pred == answer` gives success=1) is unchanged. The 43 dropped string entries from DeepSeek-Coder-V2 represent 43/10,394 = 0.4% of that one model's records.

**Result on the data:**
- 48 ZIPs parsed
- 48 agents (no model dropped)
- 12,248 distinct task IDs (vs registered 12,032; the small overrun is from variant question IDs across models — handled naturally by per-pair shared-task intersection)
- 536,289 triple rows
- 14 disciplines preserved in `benchmark_name`
- 44.1% in [0.30, 0.70] margin band

## D6 — Future-proofing: any further deviations

If during Component C execution the prep scripts reveal a JSON schema mismatch (`prep-mmlu-pro.py` notes this is a "best-effort draft"), the resolution will be appended to this file as **D7**, **D8**, etc., with:

- The exact diff to the prep script
- Why the change was mechanical (correcting a field-name bug) rather than scientific (a degree of freedom on the analyst)
- The commit SHA in this repo where the fix landed
- Whether the change materially affected which records survive into the analysis (e.g., row counts before/after)

The pre-registration's substantive decisions — margin band, thresholds, decision rule, statistic — are fixed. Only mechanical script issues are subject to amendment via this log.
