"""File OSF Addendum-2 — random-subset null-baseline (sampling-artifact test).

Schema: Open-Ended Registration (5df83f7dd28338001ac0ab0d).

Difference from register-addendum.py (the v3 robustness pass addendum):
  - title + description PATCHed in the SAME script run, BEFORE finalize.
    Previous run's title-after-fresh-draft race condition is avoided here.
  - Single variant in scope (random-subset null + decision rule); no menu.
  - References both parent registrations:
      G9WFY (Gate 0.5 OSF preregistration)
      3PD2A (Addendum-1: post-hoc sensitivity pass)
  - Files attached: random-subset-null.py (the analysis script, audit-anchored
    at git commit 23104aa BEFORE the run).

Auth: PAT from osf.io/settings/tokens (osf.full_write scope).
Pass via OSF_TOKEN env var via `op read 'op://Private/OSF PAT/credential'`.

Usage:
  OSF_TOKEN="$(op read 'op://Private/OSF PAT/credential')" \\
    python3 register-addendum-2.py --skip-finalize     # draft for review
  OSF_TOKEN="$(op read 'op://Private/OSF PAT/credential')" \\
    python3 register-addendum-2.py --no-confirm        # full submission
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
SCRIPT_COMMIT = "23104aa"  # random-subset-null.py audit anchor

ATTACH_FILES = [
    "random-subset-null.py",
]

TITLE = "Plimsoll Gate 0.5 — Addendum-2: Random-Subset Null-Baseline"

DESCRIPTION = (
    "Addendum-2 to Plimsoll Gate 0.5. Locks the random-subset null-baseline "
    "test before it runs on held-out data. Tests whether the registered "
    "capability-margin signal (parent DOI 10.17605/OSF.IO/G9WFY) is "
    "statistically distinguishable from random task-subset selection of the "
    "same size, at the per-pair level. Failure mode: the registered m_b is "
    "sampling structure dressed up as instability, which would qualify or "
    "rewrite the methodology paper headline. See Summary for full design + "
    "decision rule. Script anchor: random-subset-null.py at git commit "
    + SCRIPT_COMMIT + " in https://github.com/smledbetter/plimsoll-gate-0.5 "
    "(attached). Independent of, and complementary to, the registered "
    "label-swap null-baseline."
)

SUMMARY = f"""# Plimsoll Gate 0.5 — Addendum-2: Random-Subset Null-Baseline

**Parent registration:** DOI {PARENT_DOI} (registered 2026-04-26T18:18:39Z UTC) — Plimsoll Gate 0.5 prospective replication.

**Sister registration:** DOI {ADDENDUM_1_DOI} — Addendum-1: post-hoc sensitivity pass (variants A, B, E, F, G, H, I, plus C, D from §4.2 of parent).

**Script anchor:** `random-subset-null.py` at git commit `{SCRIPT_COMMIT}` in https://github.com/smledbetter/plimsoll-gate-0.5 (attached).

## Why this is registered separately from Addendum-1

Addendum-1 locked sensitivity sweeps that vary analytic *choices* (band, thresholds, scale, seed) around the registered baseline. The registered baseline is preserved unchanged — Addendum-1 is robustness theatre when the verdict-survival check has near-zero power to fail at z=+230.

This addendum (Addendum-2) is different. The random-subset null-baseline can FALSIFY the registered Plimsoll signal entirely — if the registered median |Δ| under capability-margin filtering is statistically indistinguishable from median |Δ| under random task-subset selection of the same per-pair size, then the registered m_b is sampling structure, not capability-margin signal. The methodology paper headline must be qualified or rewritten in that case.

Because outcome (a) "signal defended" and outcome (b) "signal is artifact" produce diametrically different paper claims, the analysis must be registered before running to prevent selective reporting.

## Null hypothesis

H0: For pairs that survive the registered inclusion thresholds (≥20 shared full tasks, ≥8 shared margin-band tasks), the median across pairs of |effect_margin − effect_full| under capability-margin filtering [0.30, 0.70] is statistically indistinguishable from the median under random task-subset selection of the same per-pair size n_margin.

In English: maybe the [0.30, 0.70] band is doing nothing more than any random subset of equal size would do. If so, the "capability-margin shift" framing is a misnomer; what we measured in Gate 0.5 (z=+230/+375/+499) is finite-sample variance.

## Test construction (locked here)

For each qualifying pair (a, b) on each of the 3 registered sources independently:
- `n_margin` = the integer count of shared tasks falling in the pre-registered margin band [0.30, 0.70] (matches `analyze.py` exactly).
- `effect_full` = mean(s_a − s_b) across all `n_full` shared tasks; FROZEN at the `analyze.py`-computed value.
- For each permutation k in 1..N_PERM:
  - Sample `random_subset_k` of size `n_margin` from the `n_full` shared tasks WITHOUT REPLACEMENT.
  - `effect_random_k` = mean((s_a − s_b) restricted to `random_subset_k`).
  - `delta_random_k` = |effect_random_k − effect_full|.
- Per-perm aggregate: median across pairs of `delta_random_k` → `null_medians[k]`.
- Observed: median across pairs of |effect_margin − effect_full| (read from registered analyze.py output, unchanged).

Parameters locked here:
- `N_PERM` = 1000
- `SEED` = 42 (matches registered label-swap null-baseline)
- Sampling: without replacement, from the per-pair shared task indices
- Per-pair `n_margin` matches the registered analyze.py value (NOT a separate threshold)

Test statistic: z = (observed_median − null_medians.mean()) / null_medians.std()

## Decision rule (locked here)

Per source independently:
- **z ≥ 3** → capability-margin signal is statistically distinguishable from random-subset baseline. Plimsoll signal on this source is **NOT** a sampling artifact at this n. Methodology defended for this source.
- **z < 3** → capability-margin signal is **NOT** distinguishable from random task-subset selection of the same size. The registered m_b is plausibly sampling artifact for this source. Methodology paper headline must be qualified or rewritten for this source.

Layered verdict (all 3 sources):
- **PASS:** z ≥ 3 on all 3 sources → methodology paper headline survives intact.
- **PARTIAL:** z ≥ 3 on SWE-bench (primary) but < 3 on a secondary → headline drops "three independent sources" claim, retains the primary-source claim with secondary-failure caveats.
- **FAIL (primary):** z < 3 on SWE-bench → methodology paper headline rewritten. Public corrigendum filed on OSF before paper preprints.

Magnitude diagnostic (descriptive, not gated):
- `ratio = observed_median / null_medians.mean()` reported alongside z. ratio ≈ 1 means signal is fully sampling-artifact-shaped even if z is technically ≥ 3 due to small null variance. ratio ≥ 2 with z ≥ 3 is the clearest defense.

## Smoke tests passed on synthetic data (committed at {SCRIPT_COMMIT})

- IID synthetic data (no signal):           z = -1.48 → correctly rejects
- IID + capability-margin signal baked in:  z = +3.39 → correctly identifies signal
- The test is well-calibrated against the failure modes it is supposed to detect.

## Honest framing

This addendum, like Addendum-1, is filed *after* the analyst has fully observed the parent OSF registration's results. The audit-trail discipline that anchors it is OSF-timestamp ordering: this registration's date_registered must precede the first execution of `random-subset-null.py` against any of the 3 registered triples files. The git commit `{SCRIPT_COMMIT}` of the analysis script is timestamped before this addendum filing.

## Reproduction

- Code + design + run logs: https://github.com/smledbetter/plimsoll-gate-0.5
- Script audit anchor: commit `{SCRIPT_COMMIT}` of `random-subset-null.py` (attached)
- Execution: tmux session `plimsoll-rs-null` on VPS; outputs to `~/projects/plimsoll-gate-0.5/random-subset-null/<source>-null.csv` + `<source>-summary.csv`
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

    token = os.environ.get("OSF_TOKEN")
    if not token:
        print("ERROR: set OSF_TOKEN env var")
        print("  e.g. OSF_TOKEN=\"$(op read 'op://Private/OSF PAT/credential')\" python3 register-addendum-2.py ...")
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
            print(f"      {p.relative_to(args.working_dir)} → {dest}")
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
