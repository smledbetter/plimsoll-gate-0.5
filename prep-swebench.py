"""Preprocess SWE-bench experiments repo into (agent, task, success) CSV.

Source: https://github.com/swe-bench/experiments  (no LICENSE file; data
treated as public facts about a public leaderboard per Feist v. Rural).
Layout: evaluation/verified/<YYYYMMDD_<scaffold>_<model>>/results/results.json

Each results.json has three lists:
  - resolved: instance_ids the agent passed
  - no_generation: instance_ids where the agent produced no patch
  - no_logs: instance_ids with execution issues

Pre-registered preprocessing for Plimsoll Gate 0.5 Component C:
  - no_logs treated as failure (matches the public leaderboard scoring;
    the conservative interpretation). Sensitivity check available via
    --exclude-no-logs flag.
  - All 134 submissions treated as 134 distinct agents — no dedup by
    scaffold-and-model. Plimsoll's claim is about (agent, task) pairs
    rather than (scaffold, model) factorization.
  - Canonical SWE-bench Verified instance list of 500 IDs is the task
    universe; submissions missing an instance ID are treated as failures
    on that instance.

Usage:
  python prep-swebench.py --repo /path/to/swe-bench-experiments \
                          --instance-list verified-500-ids.txt \
                          --out swebench-triples.csv
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_canonical_instance_list(path: Path) -> set[str]:
    with path.open() as f:
        return {line.strip() for line in f if line.strip()}


def parse_submission(submission_dir: Path, canonical: set[str],
                     exclude_no_logs: bool) -> list[dict]:
    results_path = submission_dir / "results" / "results.json"
    if not results_path.exists():
        return []
    with results_path.open() as f:
        data = json.load(f)

    resolved      = set(data.get("resolved", []))
    no_generation = set(data.get("no_generation", []))
    no_logs       = set(data.get("no_logs", []))

    agent = submission_dir.name
    rows = []
    for instance_id in canonical:
        if instance_id in resolved:
            success = 1
        elif instance_id in no_logs:
            if exclude_no_logs:
                continue  # sensitivity-check mode: drop rather than fail
            success = 0
        else:
            # no_generation OR not mentioned at all → failure (conservative).
            success = 0
        rows.append(dict(
            benchmark_name="swebench-verified",
            agent=agent,
            task_id=instance_id,
            success=success,
        ))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True,
                        help="Path to cloned swe-bench/experiments repo root.")
    parser.add_argument("--instance-list", type=Path, required=True,
                        help="Text file with the canonical 500 SWE-bench Verified instance IDs, one per line.")
    parser.add_argument("--out", type=Path, default=Path("swebench-triples.csv"))
    parser.add_argument("--exclude-no-logs", action="store_true",
                        help="Sensitivity-check mode: drop no_logs cells instead of treating as failure.")
    args = parser.parse_args()

    canonical = load_canonical_instance_list(args.instance_list)
    print(f"Loaded {len(canonical):,} canonical instance IDs.")

    verified_dir = args.repo / "evaluation" / "verified"
    if not verified_dir.exists():
        raise SystemExit(f"{verified_dir} does not exist; check --repo path.")

    submissions = sorted(p for p in verified_dir.iterdir() if p.is_dir())
    print(f"Found {len(submissions):,} submissions in {verified_dir}.")

    all_rows: list[dict] = []
    for sub in submissions:
        rows = parse_submission(sub, canonical, args.exclude_no_logs)
        if rows:
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")
    print(f"  rows:   {len(df):,}")
    print(f"  agents: {df.agent.nunique():,}")
    print(f"  tasks:  {df.task_id.nunique():,}")

    pass_rates = df.groupby("task_id")["success"].mean()
    in_band = ((pass_rates >= 0.30) & (pass_rates <= 0.70)).mean()
    print(f"  tasks in [0.30, 0.70] pass-rate band: {in_band:.1%}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
