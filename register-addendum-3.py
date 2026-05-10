"""File OSF Addendum-3 — ability-gap-quartile-conditional audit rule (Components 1+3).

Schema: Open-Ended Registration (5df83f7dd28338001ac0ab0d).

This addendum locks Q-conditional m_b as a confirmatory audit rule alongside
the parent's source-level pooled rule. It also commits to dual-reporting
(pooled and Q-conditional counts side-by-side) for the LCB reasoning-mode audit.

Components:
  - Component 1: Q-conditional m_b as the operationally correct audit rule
                 (binning policy, boundary rule, decision rule all locked).
  - Component 3: Dual reporting of audit counts (pooled and Q-conditional)
                 with Q-conditional as the headline.
  - Component 2 (cross-benchmark verdict consistency) DEFERRED to follow-up
                 work due to structurally zero pair-availability across
                 SWE-bench Verified and MMLU-Pro at the 2026-04 data snapshot.
                 See SUMMARY for details.

References:
  - Parent registration: G9WFY (Plimsoll Gate 0.5 prospective replication)
  - Sibling: 3PD2A (Addendum-1 robustness pass)
  - Sibling: EKCUQ (Addendum-2 random-subset null)

Auth: PAT from osf.io/settings/tokens (osf.full_write scope).
Pass via OSF_TOKEN env var via `op read 'op://Private/OSF PAT/credential'`.

Usage:
  OSF_TOKEN="$(op read 'op://Private/OSF PAT/credential')" \
    python3 register-addendum-3.py --skip-finalize     # draft for review
  OSF_TOKEN="$(op read 'op://Private/OSF PAT/credential')" \
    python3 register-addendum-3.py --no-confirm        # full submission
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests

API_BASE = "https://api.osf.io/v2"
WB_BASE = "https://files.osf.io/v1"
JSON_API = "application/vnd.api+json"

PROJECT_NODE = "e264j"
SCHEMA_ID = "5df83f7dd28338001ac0ab0d"  # Open-Ended Registration
PARENT_DOI = "10.17605/OSF.IO/G9WFY"
ADDENDUM_1_DOI = "10.17605/OSF.IO/3PD2A"
ADDENDUM_2_DOI = "10.17605/OSF.IO/EKCUQ"
SCRIPT_COMMIT = "083c99f"  # audit-by-quartile.py audit anchor (083c99fbed3ceba7a590a579943f45ec4683f4b4)

ATTACH_FILES = [
    "audit-by-quartile.py",
    "gate-0-followup/pair-stratification.py",
    "gate-0-followup/pair-stratification-by-ability-gap.csv",
]

TITLE = "Plimsoll Gate 0.5 — Addendum-3: Q-Conditional Audit Rule (Components 1+3)"

DESCRIPTION = (
    "Addendum-3 to Plimsoll Gate 0.5. Locks ability-gap-quartile-conditional "
    "m_b as a confirmatory audit rule alongside the parent's source-level "
    "pooled rule (parent DOI " + PARENT_DOI + "). Pooled m_b is dominated by "
    "larger-gap quartiles by approximately an order of magnitude on every "
    "Gate 0.5 source (max-Q / min-Q ratio: 7.6x SWE, 11.1x LCB, 11.1x MMLU); "
    "frontier-vs-frontier audit pairs live in Q1 and comparing them to a "
    "pooled m_b inflated by frontier-vs-weak pairs is methodologically "
    "backwards. Component 1 locks the binning policy, boundary rule, and "
    "three-way decision rule; Component 3 commits to dual reporting of audit "
    "counts under both pooled and Q-conditional rules, with Q-conditional as "
    "the headline. Component 2 (cross-benchmark verdict consistency) is "
    "deferred — pair-availability across the three sources is structurally "
    "zero at the 2026-04 data snapshot. Script anchor: audit-by-quartile.py "
    "at git commit " + SCRIPT_COMMIT + " in "
    "https://github.com/smledbetter/plimsoll-gate-0.5 (attached)."
)

SUMMARY = f"""# Plimsoll Gate 0.5 — Addendum-3: Q-Conditional Audit Rule (Components 1+3)

**Parent registration:** DOI {PARENT_DOI} — Plimsoll Gate 0.5 prospective replication.
**Sibling registrations:** DOI {ADDENDUM_1_DOI} (Addendum-1: robustness pass), DOI {ADDENDUM_2_DOI} (Addendum-2: random-subset null).
**Script anchor:** `audit-by-quartile.py` at git commit `{SCRIPT_COMMIT}` in https://github.com/smledbetter/plimsoll-gate-0.5 (attached).

## Why this is registered

The K&B literature-review reflection on the Gate 0.5 design observed that pooled m_b across all qualifying pairs treats model-pairs as exchangeable when they are not — frontier-vs-frontier comparisons differ structurally from frontier-vs-weak comparisons. The exploratory pair-stratification analysis in `gate-0-followup/pair-stratification.md` (committed before this addendum, see attached `pair-stratification.py` + `pair-stratification-by-ability-gap.csv`) confirmed the concern empirically. Per-quartile m_b ratios (max-Q / min-Q):

- SWE-bench Verified: 7.6x  (Q1 m_b = 0.033, Q4 m_b = 0.250)
- LiveCodeBench:      11.1x (Q1 m_b = 0.029, Q4 m_b = 0.319)
- MMLU-Pro:           11.1x (Q1 m_b = 0.018, Q4 m_b = 0.203)

Pooled m_b is dominated by the larger-gap quartiles by approximately an order of magnitude on every source. Audited reasoning-mode pairs from frontier vendors (Anthropic, Google, OpenAI) almost universally live in Q1 or Q2 of LCB. Comparing them to pooled LCB m_b = 0.156 — which is inflated by frontier-vs-weak pairs the audited pair has nothing to do with — is methodologically backwards.

Q-conditional m_b is the operationally correct comparator: each audited pair is compared against the m_b for its own ability-gap quartile.

## Component 1 — Q-conditional audit rule (LOCKED)

For any audited pair with paired effect `effect_full(a, b)` on a Gate 0.5 source:

**Quartile binning of the source's qualifying-pair distribution.**
- Inputs: registered `<source>-pairs.csv` from analyze.py at commit `3402147` (parent registration).
- Method: `pd.qcut(qualifying.|effect_full|, 4, labels=['Q1','Q2','Q3','Q4'], retbins=True)`. Pandas-default right-inclusive equal-frequency binning.
- Q m_b: `median(|abs_delta|)` over the qualifying pairs assigned to that quartile.

**Audited-pair quartile assignment.**
- Method: `pd.cut(audited.|effect_full|, bins=quartile_edges, include_lowest=True, right=True, labels=['Q1','Q2','Q3','Q4'])`.
- Boundary: an audited pair whose `|effect_full|` equals the upper edge of Q_n is assigned to Q_n; just above the edge falls in Q_{{n+1}}.
- Out-of-range: an audited pair whose `|effect_full|` exceeds the source's largest qualifying-pair |effect_full| is reported as `OUT-OF-RANGE` (no verdict). Below the lowest edge is structurally impossible for non-zero effects.

**Three-way decision rule.**
- `SUBORDINATE-TO-SHIFT` iff `|effect_full| < Q m_b`.
- `PAIR-UNSTABLE` iff `|effect_full| >= Q m_b` AND `pair_shift > |effect_full|`.
- `ROBUST` iff `|effect_full| >= Q m_b` AND `pair_shift <= |effect_full|`.

This is the same three-way structure as the parent's pooled rule (audit-reasoning-modes.py) with `m_b` replaced by `Q m_b`. The exploratory writeup in `pair-stratification.md` simplified to a binary (SUBORDINATE / NOT) and consequently missed PAIR-UNSTABLE cases. The locked rule above preserves the three-way diagnostic.

**Audit-trail discipline.** This addendum is filed *after* the analyst has fully observed the parent OSF registration's results and the exploratory Q-conditional analysis. The discipline that anchors it is OSF-timestamp ordering: this registration's `date_registered` must precede any future audit's first execution of `audit-by-quartile.py` on a NEW pair (e.g., on next-generation reasoning-mode releases). The script's git commit `{SCRIPT_COMMIT}` is timestamped before this addendum filing. Re-running on the existing 13 LCB pairs is documented dual-reporting under Component 3, not novel evidence.

## Component 3 — Dual reporting of audit counts (LOCKED)

The methodology paper's audit section reports the LCB reasoning-mode audit count under both rules:

- **Pooled rule (parent G9WFY, registered 2026-04-26T18:18:39Z UTC):** 11/13 SUBORDINATE-TO-SHIFT, 0/13 PAIR-UNSTABLE, 2/13 ROBUST. m_b = 0.156.
- **Q-conditional rule (this addendum, Component 1):** 4/13 SUBORDINATE-TO-SHIFT, 2/13 PAIR-UNSTABLE, 7/13 ROBUST. Per-pair Q m_b values from the LCB qualifying-pair distribution:

| Audit pair | |effect_full| | Q | Q m_b | Verdict |
|---|---|---|---|---|
| Claude Opus 4 — Thinking lift | 0.0806 | Q1 | 0.0287 | PAIR-UNSTABLE |
| Claude Sonnet 4 — Thinking lift | 0.0910 | Q2 | 0.1149 | SUBORDINATE-TO-SHIFT |
| Gemini Flash 2.0 — Thinking vs Exp | 0.0557 | Q1 | 0.0287 | PAIR-UNSTABLE |
| Gemini Flash 2.0 — Thinking-01-21 vs Exp | 0.1393 | Q2 | 0.1149 | ROBUST |
| Gemini Flash 2.0 — Thinking-12-19 vs Exp | 0.1469 | Q2 | 0.1149 | ROBUST |
| O1 — High vs Low effort | 0.0727 | Q1 | 0.0287 | ROBUST |
| O1 — High vs Med effort | 0.0489 | Q1 | 0.0287 | ROBUST |
| O3-Mini — High vs Low effort | 0.0711 | Q1 | 0.0287 | ROBUST |
| O3-Mini — High vs Med effort | 0.0237 | Q1 | 0.0287 | SUBORDINATE-TO-SHIFT |
| O4-Mini — High vs Low effort | 0.0986 | Q2 | 0.1149 | SUBORDINATE-TO-SHIFT |
| O4-Mini — High vs Medium effort | 0.0284 | Q1 | 0.0287 | SUBORDINATE-TO-SHIFT |
| DeepSeek R1-0528 vs V3 base | 0.3488 | Q3 | 0.2504 | ROBUST |
| QwQ-32B-Preview vs Qwen2.5-Ins-32B | 0.1683 | Q2 | 0.1149 | ROBUST |

**Headline rule:** Q-conditional is the operational headline; pooled is the comparison reported alongside as a methodological cautionary note. Rationale: pooled m_b is the right comparator for **population-level** noise-floor questions ("what is the typical paired-effect shift across this benchmark's qualifying pairs?"); Q-conditional m_b is the right comparator for **audit** questions ("does this specific announced lift clear the noise floor for pairs in its ability-gap class?"). The audit answers the second question.

## Component 2 — DEFERRED

The originally-proposed Component 2 was cross-benchmark verdict consistency: test whether SUBORDINATE / ROBUST verdicts on LCB predict the same verdict on SWE-bench Verified or MMLU-Pro for the same pair, under Q-conditional m_b on each source. The Plimsoll project README flagged the dependency on pair-availability across the three sources.

Pair-availability audit confirmed structurally zero overlap at the 2026-04 data snapshot:

- **MMLU-Pro:** zero matching models. The pool predates the entire reasoning-mode product generation (Llama 2/3, GPT-4o, Gemini 1.5/3.1, Qwen 1.5, Mistral, Mixtral, Claude 3.5 Sonnet only). No Claude Sonnet 4, no o3-mini, no o4-mini, no thinking/effort-tier variants of any model.
- **SWE-bench Verified:** structural mismatch. The pool is 134 *agent submissions* (harness + model). Only one o3-mini submission and one o4-mini submission exist; no effort-tier paired variants under the same harness. Claude 4 Sonnet appears in three submissions (sweagent, moatless, Lingxi); none isolate reasoning-mode flag as a separate factor.

Component 2 is deferred to follow-up work and would either (a) wait for new SWE / MMLU snapshots that include reasoning-mode-paired submissions of the same models, or (b) pivot to a different pair class (model-version vs model-version) at the cost of losing the audit's specific connection to reasoning-mode lift claims. Neither path is in scope for this addendum.

## Honest framing (analyst-has-seen-results clause)

This addendum, like Addendum-1 and Addendum-2, is filed after the analyst has fully observed the parent OSF registration's audit results AND the exploratory Q-conditional analysis in `pair-stratification.md`. The audit-trail discipline is OSF-timestamp ordering of the analysis script:

- `audit-by-quartile.py` at commit `{SCRIPT_COMMIT}` is committed and pushed BEFORE this addendum's `date_registered`.
- The exploratory anchor (`pair-stratification.py` + `pair-stratification-by-ability-gap.csv`) is timestamped earlier on the same public repo.
- The forward-facing commitment is what this addendum binds: future audits on NEW pairs (e.g., next-generation reasoning-mode releases on LCB or any other Gate 0.5 source) MUST use the Q-conditional rule above.

Re-running on the existing 13 LCB pairs is dual-reporting under Component 3 and is an honest exercise of the locked rule against the in-scope evidence at filing time, not novel data.

## Reproduction

- Code + design + run logs: https://github.com/smledbetter/plimsoll-gate-0.5
- Q-conditional audit script: `audit-by-quartile.py` at commit `{SCRIPT_COMMIT}` (attached)
- Exploratory anchor: `gate-0-followup/pair-stratification.py` + `pair-stratification-by-ability-gap.csv` (attached)
- Parent pairs.csv inputs (registered, FROZEN): `component-c-runs/<source>/<source>-pairs.csv` at commit `3402147`
"""


def _hdrs(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": JSON_API}


def upload_to_node(token: str, node_id: str, path: Path, dest_name: str) -> None:
    url = f"{WB_BASE}/resources/{node_id}/providers/osfstorage/?kind=file&name={dest_name}"
    headers = {"Authorization": f"Bearer {token}"}
    with path.open("rb") as f:
        r = requests.put(url, headers=headers, data=f.read())
    if r.status_code == 409:
        print(f"      (skip: {dest_name} already on node)")
        return
    r.raise_for_status()


def create_draft(token: str, node_id: str, schema_id: str) -> str:
    payload = {
        "data": {
            "type": "draft_registrations",
            "relationships": {
                "registration_schema": {
                    "data": {"type": "registration_schemas", "id": schema_id},
                },
            },
        }
    }
    r = requests.post(
        f"{API_BASE}/nodes/{node_id}/draft_registrations/",
        headers=_hdrs(token), json=payload,
    )
    r.raise_for_status()
    return r.json()["data"]["id"]


def patch_draft(token: str, draft_id: str,
                title: str, description: str, summary: str) -> None:
    """PATCH title + description + summary in one shot, BEFORE finalize."""
    payload = {
        "data": {
            "id": draft_id,
            "type": "draft_registrations",
            "attributes": {
                "title": title,
                "description": description,
                "registration_responses": {"summary": summary},
            },
        }
    }
    r = requests.patch(
        f"{API_BASE}/draft_registrations/{draft_id}/",
        headers=_hdrs(token), json=payload,
    )
    r.raise_for_status()


def finalize_registration(token: str, draft_id: str) -> str:
    payload = {
        "data": {
            "type": "registrations",
            "attributes": {"category": "project"},
            "relationships": {
                "draft_registration": {
                    "data": {"type": "draft_registrations", "id": draft_id},
                },
            },
        }
    }
    r = requests.post(f"{API_BASE}/registrations/", headers=_hdrs(token), json=payload)
    r.raise_for_status()
    return r.json()["data"]["id"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-dir", type=Path, default=Path.cwd())
    parser.add_argument("--skip-files", action="store_true")
    parser.add_argument("--skip-finalize", action="store_true")
    parser.add_argument("--no-confirm", action="store_true")
    args = parser.parse_args()

    if SCRIPT_COMMIT.startswith("__FILL_ME"):
        print("ERROR: SCRIPT_COMMIT placeholder not filled in.")
        print("       Push audit-by-quartile.py to GitHub first, then update")
        print("       SCRIPT_COMMIT in this script to the new commit SHA.")
        return 1

    token = os.environ.get("OSF_TOKEN")
    if not token:
        print("ERROR: set OSF_TOKEN env var")
        print("  e.g. OSF_TOKEN=\"$(op read 'op://Private/OSF PAT/credential')\" python3 register-addendum-3.py ...")
        return 1

    files = [args.working_dir / f for f in ATTACH_FILES]
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        print("ERROR: missing files:", missing)
        return 1
    print(f"Attach files: {[f.name for f in files]}")

    if not args.skip_files:
        print(f"\n[1/4] Uploading {len(files)} files to node {PROJECT_NODE} ...")
        for p in files:
            dest = p.relative_to(args.working_dir).as_posix().replace("/", "__")
            print(f"      {p.relative_to(args.working_dir)} -> {dest}")
            upload_to_node(token, PROJECT_NODE, p, dest)
            time.sleep(0.5)

    print(f"\n[2/4] Creating draft on node {PROJECT_NODE} (Open-Ended Registration) ...")
    draft_id = create_draft(token, PROJECT_NODE, SCHEMA_ID)
    print(f"      draft id: {draft_id}")
    print(f"      draft url: https://osf.io/registries/drafts/{draft_id}/")

    print(f"\n[3/4] PATCHing title + description + summary ({len(SUMMARY)} chars) ...")
    patch_draft(token, draft_id, TITLE, DESCRIPTION, SUMMARY)
    print("      ok (title and description set on the same draft we'll finalize)")

    if args.skip_finalize:
        print(f"\n[4/4] STOP per --skip-finalize. Draft NOT registered.")
        print(f"      Review at: https://osf.io/registries/drafts/{draft_id}/")
        return 0

    if not args.no_confirm:
        print(f"\n[4/4] About to finalize. THIS IS IRREVERSIBLE.")
        print(f"      Draft: https://osf.io/registries/drafts/{draft_id}/")
        confirm = input("Type FINALIZE to proceed: ")
        if confirm.strip() != "FINALIZE":
            print("Aborted.")
            return 0

    print("[4/4] Finalizing ...")
    reg_id = finalize_registration(token, draft_id)
    print(f"\nREGISTERED.")
    print(f"   registration: https://osf.io/{reg_id}/")
    print(f"   project:      https://osf.io/{PROJECT_NODE}/")
    print(f"\nNote: Open-Ended Registration requires contributor approval via")
    print(f"      OSF web UI. Visit the registration link above and click Approve.")
    print(f"      DOI mints after approval.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
