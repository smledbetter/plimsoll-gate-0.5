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

## D3 — Future-proofing: any further deviations

If during Component C execution the prep scripts reveal a JSON schema mismatch (`prep-mmlu-pro.py` notes this is a "best-effort draft"), the resolution will be appended to this file as **D4**, **D5**, etc., with:

- The exact diff to the prep script
- Why the change was mechanical (correcting a field-name bug) rather than scientific (a degree of freedom on the analyst)
- The commit SHA in this repo where the fix landed
- Whether the change materially affected which records survive into the analysis (e.g., row counts before/after)

The pre-registration's substantive decisions — margin band, thresholds, decision rule, statistic — are fixed. Only mechanical script issues are subject to amendment via this log.
