"""Preprocess LiveCodeBench submissions repo into (model, task, success) CSV.

Source: https://github.com/LiveCodeBench/submissions  (MIT)
Layout: <model_variant>/Scenario.codegeneration_*_eval_all.json

Each eval_all.json file is a list of question records with at least:
  - question_id, contest_id, platform (codeforces/leetcode/atcoder)
  - difficulty (easy/medium/hard)
  - graded_list: list[bool] — pass/fail per attempt; primary = graded_list[0]

Pre-registered preprocessing for Plimsoll Gate 0.5 Component C:
  - Pass/fail = graded_list[0] (first-attempt pass@1). Sensitivity check
    --any-pass uses any(graded_list) as the alternate definition.
  - Variants per model family deduplicated to one canonical variant
    per family — the latest-mtime directory under common variant
    suffixes (_thinking, _temp\\d+, _seed\\d+, _v\\d+). Override with
    --no-dedup to keep all 73 raw submissions.
  - Tasks identified by (platform, contest_id, question_id) tuple to
    avoid cross-platform ID collision. Stored in benchmark_name column
    so per-platform texture is recoverable downstream.

NB: This is a best-effort draft. Validate against a real submission
file before treating its output as the frozen Component C input. The
LiveCodeBench file schema is documented in the inventory but has not
been exercised by this script yet.

Usage:
  python prep-livecodebench.py --repo /path/to/LiveCodeBench-submissions \\
                               --out livecodebench-triples.csv
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


VARIANT_SUFFIX_RE = re.compile(
    r"(_thinking|_no-thinking|_temp\d+(\.\d+)?|_t\d+|_seed\d+|_variant\d*|_v\d+)$",
    re.IGNORECASE,
)


def canonical_family(model_dir_name: str) -> str:
    """Strip common variant suffixes to derive a canonical family name."""
    name = model_dir_name
    while True:
        new = VARIANT_SUFFIX_RE.sub("", name)
        if new == name:
            return name
        name = new


def parse_submission(model_dir: Path, any_pass: bool) -> list[dict]:
    rows = []
    for eval_path in model_dir.glob("Scenario.codegeneration*_eval_all.json"):
        with eval_path.open() as f:
            data = json.load(f)
        if not isinstance(data, list):
            continue
        for entry in data:
            graded = entry.get("graded_list")
            if not graded:
                continue
            if any_pass:
                success = 1 if any(bool(g) for g in graded) else 0
            else:
                success = 1 if bool(graded[0]) else 0
            platform   = entry.get("platform", "unknown")
            contest_id = entry.get("contest_id", "na")
            question_id = entry.get("question_id", "na")
            rows.append(dict(
                benchmark_name=platform,
                agent=model_dir.name,
                task_id=f"{platform}::{contest_id}::{question_id}",
                success=success,
            ))
    return rows


def dedup_to_canonical(df: pd.DataFrame, repo_root: Path) -> pd.DataFrame:
    df = df.copy()
    df["family"] = df["agent"].map(canonical_family)
    family_to_canonical: dict[str, str] = {}
    for family, agents in df.groupby("family")["agent"].unique().items():
        latest = max(agents,
                     key=lambda a: (repo_root / a).stat().st_mtime
                     if (repo_root / a).exists() else 0)
        family_to_canonical[family] = latest
    keep = set(family_to_canonical.values())
    return df[df["agent"].isin(keep)].drop(columns=["family"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True,
                        help="Path to cloned LiveCodeBench/submissions repo root.")
    parser.add_argument("--out", type=Path, default=Path("livecodebench-triples.csv"))
    parser.add_argument("--no-dedup", action="store_true",
                        help="Skip variant dedup; keep all 73 submissions.")
    parser.add_argument("--any-pass", action="store_true",
                        help="Sensitivity-check mode: success = any(graded_list) instead of graded_list[0].")
    args = parser.parse_args()

    if not args.repo.exists():
        raise SystemExit(f"{args.repo} does not exist; check --repo path.")

    submissions = sorted(p for p in args.repo.iterdir() if p.is_dir())
    print(f"Found {len(submissions):,} submission directories.")

    all_rows: list[dict] = []
    for sub in submissions:
        rows = parse_submission(sub, args.any_pass)
        if rows:
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    print(f"\nPre-dedup:")
    print(f"  rows:   {len(df):,}")
    print(f"  agents: {df.agent.nunique():,}")
    print(f"  tasks:  {df.task_id.nunique():,}")

    if not args.no_dedup:
        df = dedup_to_canonical(df, args.repo)
        print(f"\nPost-dedup:")
        print(f"  rows:   {len(df):,}")
        print(f"  agents: {df.agent.nunique():,}")
        print(f"  tasks:  {df.task_id.nunique():,}")

    df.to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")

    pass_rates = df.groupby("task_id")["success"].mean()
    in_band = ((pass_rates >= 0.30) & (pass_rates <= 0.70)).mean()
    print(f"  tasks in [0.30, 0.70] pass-rate band: {in_band:.1%}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
