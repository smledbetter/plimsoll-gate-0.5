"""File OSF Addendum registration for Plimsoll Gate 0.5 post-hoc sensitivity pass.

Schema: Open-Ended Registration (5df83f7dd28338001ac0ab0d) — single text field,
right shape for an addendum (no pre-reg form to fight against).

Workflow:
  1. POST /v2/nodes/e264j/draft_registrations/   — draft on existing project
  2. PATCH /v2/draft_registrations/{id}/         — fill summary
  3. PUT  files.osf.io/v1/.../{drafts,registrations}/  — attach DESIGN.md v3
  4. POST /v2/registrations/                     — finalize (irreversible)

Auth: PAT from osf.io/settings/tokens. Pass via OSF_TOKEN env var (set by
shell from `op read 'op://Private/OSF PAT/credential'`).

Usage:
  OSF_TOKEN="$(op read 'op://Private/OSF PAT/credential')" \
    python3 register-addendum.py --skip-finalize
  OSF_TOKEN="$(op read 'op://Private/OSF PAT/credential')" \
    python3 register-addendum.py --no-confirm
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
DESIGN_V3_COMMIT = "33a2d84"

ATTACH_FILES = [
    "robustness/DESIGN.md",
    "registration-deviations.md",
]

SUMMARY = f"""# Plimsoll Gate 0.5 — Post-Hoc Sensitivity Pass Addendum

**Parent registration:** DOI {PARENT_DOI} (registered 2026-04-26T18:18:39Z UTC).
**Design document anchor:** `robustness/DESIGN.md` at git commit `{DESIGN_V3_COMMIT}` in repository https://github.com/smledbetter/plimsoll-gate-0.5 (attached to this registration as `DESIGN.md`).

## Purpose of this addendum

This registration locks in the **menu of post-hoc sensitivity variants** to be run on the Gate 0.5 held-out replication results, *before* any variant is executed. The parent registration committed the substantive analysis (margin band [0.30, 0.70], thresholds (≥20, ≥8), median |Δ| ≥ 0.05 AND z ≥ 3 decision rule). All three sources cleared (z = +230, +375, +499). This addendum exists because the variant menu below is *not* in the parent OSF document — it is post-hoc, and OSF-anchoring it before execution is what gives the sensitivity pass the same audit-trail discipline as the parent.

The git-commit-before-execution convention protects against post-hoc selection of *inputs to a pre-specified menu*; it does not protect against post-hoc selection of *the menu itself*. This addendum closes that gap.

## Variants to run (locked here, executed only after this DOI issues)

**A. Margin band sweep (3 sources × 4 bands).** `{{[0.25, 0.75], [0.30, 0.70] (registered baseline), [0.35, 0.65], [0.40, 0.60]}}` — symmetric ±0.05 and ±0.10 around the registered band. Rule "symmetric ±0.05 and ±0.10 only" is locked; finer-resolution sweeps excluded.

**B. MMLU-Pro per-discipline (14 sub-analyses).** Re-run analyze.py separately on each of the 14 disciplines with null-baseline z computed per discipline. Cells where n_pairs < 50 are reported descriptive-only.

**E. Logit-space SWE-bench + LiveCodeBench.** Empirical-logit-with-continuity-correction (Cox 1970): log((s + 0.5) / (1 − s + 0.5)) where s is per-task pass rate. Tests whether raw-rate Δ vs. logit Δ produces meaningfully different m_b.

**F. Inclusion-threshold sweep (3 sources × 3 thresholds).** (≥10, ≥4) looser; (≥20, ≥8) registered baseline; (≥30, ≥15) stricter.

**G. Null-baseline seed stability.** SWE-bench Verified primary at 11 RNG seeds (registered seed=42 plus {{0..9}}). Report z mean ± std across seeds. (Varying registered seed is itself post-hoc, hence inclusion in this addendum.)

**H. Audit-by-band sub-pass.** Re-run `audit-reasoning-modes.py` against each margin band's empirically-computed m_b on LiveCodeBench. Report per band: how many of the 13 reasoning-mode pairs change verdict.

**I. Audit under logit-space m_b.** Re-run `audit-reasoning-modes.py` with m_b computed from variant E's logit-space LiveCodeBench analysis. The audit's "11/13 fail" depends on m_b's *level*, which logit could move materially.

(Variants C and D — LiveCodeBench `--no-dedup` and SWE-bench `--exclude-no-logs` — are listed by name in §4.2 of the parent pre-registration and need no addendum coverage.)

## Robustness criteria (load-bearing diagnostic, locked here)

**Per-pair sign-flip rate** is the primary diagnostic:
- flip_rate(variant) = #{{pairs where sign(Δ_baseline) ≠ sign(Δ_variant)}} / N_qualifying_pairs
- < 5%: stable. 5–15%: mildly unstable, reported in Limitations. ≥ 15%: destabilizing, reported in headline.

**Verdict-survival** (median |Δ| ≥ 0.05 AND z ≥ 3 unchanged) is reported but **not load-bearing**: at the registered z-scores (+230, +375, +499) the test has near-zero power to fail.

**Cell-level n_pairs floor.** Cells with n_pairs < 50 are descriptive-only; do not contribute to pass/fail or flip-rate aggregates.

## Failure protocol (locked here)

| Outcome | Action |
|---|---|
| All variants pass with flip_rate < 5% | Methodology paper proceeds with layered-clear narrative. |
| Any *secondary* source (LiveCodeBench, MMLU-Pro) fails verdict OR flip_rate ≥ 5% under ≥1 variant | Abstract is rewritten: "three independent sources" → "SWE-bench Verified plus two secondary sources with [variant-specific] caveats." |
| **SWE-bench Verified (primary) fails verdict OR flip_rate ≥ 15% under any variant** | Methodology paper headline rewritten with variant-specific qualifications; public-corrigendum-shaped note added to OSF project before paper preprints. |
| Variant H: flip-count of the 13 audit pairs changes by ≥2 across any band | Audit blog post reports **all four band-conditional numbers**; single-number headline dropped. (No "most conservative" cherry-picking.) |
| Variant I: SUBORDINATE count under logit-m_b differs from raw-m_b count by ≥2 pairs | Audit blog post reports both numbers; single-number headline dropped. |
| Variant G: min(z) across 11 seeds < 100 on SWE-bench primary | Re-run all three null-baselines at n=10,000 perms; report tightened CIs. |

Reframing post-hoc is not permitted; if a SWE-bench variant fails or destabilizes, the headline changes.

## Honest framing

This document specifies a **pre-specified post-hoc sensitivity analysis**, not a pre-registration. The parent OSF registration is the load-bearing primary analysis. This addendum is being filed *after* the analyst knows the baseline numbers — that is an attestation, not a proof, and the OSF-timestamp ordering (this addendum issued *before* any variant execution) is the only mechanical anchor.

## Reproduction

- Code + design + run logs: https://github.com/smledbetter/plimsoll-gate-0.5
- This addendum's design anchor: commit `{DESIGN_V3_COMMIT}` of file `robustness/DESIGN.md` (attached here)
- Execution sequencing: tmux session `plimsoll-robust` on VPS; `gate-0.5/robustness/run-log.txt` records every command + timestamp; results land at `gate-0.5/robustness/all-variants.csv` and `gate-0.5/robustness/robustness-summary.md`.
"""


def _hdrs(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": JSON_API}


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


def patch_draft_responses(token: str, draft_id: str, responses: dict) -> None:
    payload = {
        "data": {
            "id": draft_id,
            "type": "draft_registrations",
            "attributes": {"registration_responses": responses},
        }
    }
    r = requests.patch(
        f"{API_BASE}/draft_registrations/{draft_id}/",
        headers=_hdrs(token), json=payload,
    )
    r.raise_for_status()


def upload_to_node(token: str, node_id: str, path: Path, dest_name: str) -> None:
    """Upload a file to the parent node so the registration inherits it."""
    url = f"{WB_BASE}/resources/{node_id}/providers/osfstorage/?kind=file&name={dest_name}"
    headers = {"Authorization": f"Bearer {token}"}
    with path.open("rb") as f:
        r = requests.put(url, headers=headers, data=f.read())
    if r.status_code == 409:
        # File already exists; that's fine.
        print(f"      (skip: {dest_name} already on node)")
        return
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

    token = os.environ.get("OSF_TOKEN")
    if not token:
        print("ERROR: set OSF_TOKEN env var")
        print("  e.g. OSF_TOKEN=\"$(op read 'op://Private/OSF PAT/credential')\" python3 register-addendum.py ...")
        return 1

    # Validate files exist.
    files = [args.working_dir / f for f in ATTACH_FILES]
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        print("ERROR: missing files:", missing)
        return 1
    print(f"Attach files: {[f.name for f in files]}")

    # Step 1: upload files to project node (inherited by registration).
    if not args.skip_files:
        print(f"\n[1/4] Uploading {len(files)} files to node {PROJECT_NODE} ...")
        for p in files:
            dest = p.relative_to(args.working_dir).as_posix().replace("/", "__")
            print(f"      {p.relative_to(args.working_dir)} → {dest}")
            upload_to_node(token, PROJECT_NODE, p, dest)
            time.sleep(0.5)

    # Step 2: create draft.
    print(f"\n[2/4] Creating draft on node {PROJECT_NODE} (Open-Ended Registration) ...")
    draft_id = create_draft(token, PROJECT_NODE, SCHEMA_ID)
    print(f"      draft id: {draft_id}")
    print(f"      draft url: https://osf.io/registries/drafts/{draft_id}/")

    # Step 3: PATCH summary.
    print(f"\n[3/4] PATCHing summary ({len(SUMMARY)} chars) ...")
    patch_draft_responses(token, draft_id, {"summary": SUMMARY})
    print("      ok")

    if args.skip_finalize:
        print(f"\n[4/4] STOP per --skip-finalize. Draft NOT registered.")
        print(f"      Review at: https://osf.io/registries/drafts/{draft_id}/")
        print(f"      Re-run without --skip-finalize to submit, or finalize via OSF web UI.")
        return 0

    # Step 4: finalize.
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
    print(f"\nNext: backfill the addendum DOI to robustness/DESIGN.md frontmatter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
