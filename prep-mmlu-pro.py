"""Preprocess MMLU-Pro eval_results/ into (model, task, success) CSV.

Source: https://github.com/TIGER-AI-Lab/MMLU-Pro  (Apache-2.0 code, MIT data)
Layout: eval_results/<model_name>.zip

Each ZIP contains per-discipline JSON files with per-question records:
  - question_id (or analogous)
  - pred (model prediction, e.g. "A")
  - answer (gold answer letter)
  - category / subject (one of 14 disciplines)

Pre-registered preprocessing for Plimsoll Gate 0.5 Component C:
  - success = (pred == answer), trimmed string comparison.
  - Pooled across 14 disciplines is the primary analysis. The discipline
    is preserved in benchmark_name so per-discipline texture is
    recoverable downstream as a sensitivity / supplementary analysis.
  - No model dedup (each ZIP corresponds to one model).
  - Records missing pred or answer are skipped (treated as no-attempt
    rather than failure; alternative would be conservative-failure but
    MMLU-Pro doesn't have a documented no-generation case).

NB: This is a best-effort draft. The exact JSON schema inside the ZIPs
needs validation against a real file before this script is treated as
the frozen Component C input. The inventory documents the field names
but has not exercised them through this script yet.

Usage:
  python prep-mmlu-pro.py --eval-results-dir /path/to/MMLU-Pro/eval_results \\
                          --out mmlu-pro-triples.csv
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import pandas as pd


def parse_zip(zip_path: Path) -> list[dict]:
    model = zip_path.stem
    rows: list[dict] = []
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if not name.endswith(".json"):
                continue
            if "__MACOSX" in name or name.startswith("._") or "/._" in name:
                # macOS extended-attribute sidecar files; not real JSON.
                continue
            with zf.open(name) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    # Defensive: malformed JSON in source data (e.g. truncated
                    # files from one ZIP). Skip and continue.
                    continue
            if not isinstance(data, list):
                continue
            for entry in data:
                if not isinstance(entry, dict):
                    # Defensive: at least one ZIP (DeepSeek-Coder-V2) has
                    # stray non-dict records (e.g. literal "other" strings)
                    # mixed into the eval list. Treat as no-attempt.
                    # Documented in registration-deviations.md D5.
                    continue
                pred = entry.get("pred")
                answer = entry.get("answer")
                if pred is None or answer is None:
                    continue
                qid = entry.get("question_id") or entry.get("id")
                if qid is None:
                    continue
                category = entry.get("category") or entry.get("subject") or "unknown"
                success = 1 if str(pred).strip() == str(answer).strip() else 0
                rows.append(dict(
                    benchmark_name=str(category),
                    agent=model,
                    task_id=str(qid),
                    success=success,
                ))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-results-dir", type=Path, required=True,
                        help="Path to MMLU-Pro/eval_results/ directory containing model ZIPs.")
    parser.add_argument("--out", type=Path, default=Path("mmlu-pro-triples.csv"))
    args = parser.parse_args()

    if not args.eval_results_dir.exists():
        raise SystemExit(f"{args.eval_results_dir} does not exist.")

    zips = sorted(args.eval_results_dir.glob("*.zip"))
    print(f"Found {len(zips):,} model ZIP files.")

    all_rows: list[dict] = []
    for z in zips:
        rows = parse_zip(z)
        if rows:
            all_rows.extend(rows)
            print(f"  {z.name}: {len(rows):,} rows")
        else:
            print(f"  {z.name}: SKIPPED (no parseable records)")

    df = pd.DataFrame(all_rows)
    df.to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")
    print(f"  rows:        {len(df):,}")
    print(f"  agents:      {df.agent.nunique():,}")
    print(f"  tasks:       {df.task_id.nunique():,}")
    print(f"  disciplines: {df.benchmark_name.nunique():,}")

    pass_rates = df.groupby("task_id")["success"].mean()
    in_band = ((pass_rates >= 0.30) & (pass_rates <= 0.70)).mean()
    print(f"  tasks in [0.30, 0.70] pass-rate band: {in_band:.1%}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
