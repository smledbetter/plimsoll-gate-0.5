"""Atlas v0 — METR HCAST prep.

Pulls METR Time Horizon 1.1 runs.jsonl (already downloaded), filters to HCAST
tasks, collapses seed reruns via mean, emits Plimsoll triples format.

Source: https://github.com/METR/eval-analysis-public/blob/main/reports/time-horizon-1-1/data/raw/runs.jsonl
Schema: task_id, alias, score_binarized, task_source, etc.

Output: metr-hcast-triples.csv with columns (agent, task_id, success).
'success' is the mean of score_binarized across seed reruns for that
(agent, task_id) pair. analyze.py treats this as a per-task pass rate.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

INPUT = Path("/Users/stevo/Sites/Thinking/Projects/Research/Plimsoll/gate-0.5/atlas-v0/metr-time-horizon-1-1-runs.jsonl")
OUTPUT = Path("/Users/stevo/Sites/Thinking/Projects/Research/Plimsoll/gate-0.5/atlas-v0/metr-hcast-triples.csv")


def main() -> int:
    rows = []
    with INPUT.open() as f:
        for line in f:
            r = json.loads(line)
            if r.get("task_source") != "HCAST":
                continue
            sb = r.get("score_binarized")
            if sb is None:
                continue
            rows.append({
                "agent": r["alias"],
                "task_id": r["task_id"],
                "score_binarized": float(sb),
            })

    df = pd.DataFrame(rows)
    print(f"HCAST rows: {len(df):,}")
    print(f"Agents: {df['agent'].nunique()}")
    print(f"Tasks: {df['task_id'].nunique()}")
    print(f"Mean (agent, task_id) reruns: {df.groupby(['agent','task_id']).size().mean():.2f}")

    # Collapse seeds via mean
    triples = (
        df.groupby(["agent", "task_id"])["score_binarized"]
        .mean()
        .reset_index()
        .rename(columns={"score_binarized": "success"})
    )
    print(f"\nTriples rows after seed collapse: {len(triples):,}")
    print(f"Pass-rate distribution:")
    print(triples["success"].describe().to_string())

    triples.to_csv(OUTPUT, index=False)
    print(f"\nWrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
