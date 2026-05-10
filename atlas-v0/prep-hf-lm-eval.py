"""Atlas v0 — HF Open LLM Leaderboard v1 lm-eval-harness prep.

For a given benchmark config (e.g. 'hellaswag|10' or 'gsm8k|5'), pulls
per-doc pass/fail from open-llm-leaderboard-old/details_<model> repos
on HuggingFace. Output: triples CSV (agent, task_id, success).

Defensible model selection rule (LOCKED before pulling any benchmark data):
  - A fixed list of well-known open-weights models from the v1 era,
    spanning organizations and parameter sizes (7B to 70B+).
  - For each model, take the MOST RECENT timestamped run available.
  - If a model has no parquet for the requested benchmark, skip it.
  - The same model list is used for both HellaSwag and GSM8K (gives a
    matched-agent corpus across the two benchmarks).

The list is intentionally conservative: 30 well-known models. We're not
trying to maximize n_pairs; we're testing whether the doctor's Stage 1
correctly flags saturated benchmarks. 30 models gives ~435 candidate pairs,
well above the ≥8-agents floor.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
import io

import pandas as pd

# Locked model list — frontier open-weights models from the v1 leaderboard era
# (2023–2024). Spans 7 orgs × 4 size buckets.
LOCKED_MODELS = [
    # Meta Llama family
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-13b-hf",
    "meta-llama/Llama-2-70b-hf",
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "meta-llama/Llama-2-70b-chat-hf",
    "meta-llama/Meta-Llama-3-8B",
    "meta-llama/Meta-Llama-3-70B",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "meta-llama/Meta-Llama-3-70B-Instruct",
    # Mistral / Mixtral
    "mistralai/Mistral-7B-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai/Mixtral-8x7B-v0.1",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    # Qwen
    "Qwen/Qwen1.5-7B-Chat",
    "Qwen/Qwen1.5-14B-Chat",
    "Qwen/Qwen1.5-72B-Chat",
    "Qwen/Qwen2-7B-Instruct",
    "Qwen/Qwen2-72B-Instruct",
    # DeepSeek
    "deepseek-ai/deepseek-llm-7b-base",
    "deepseek-ai/deepseek-llm-67b-base",
    # Yi
    "01-ai/Yi-6B",
    "01-ai/Yi-34B",
    # Gemma
    "google/gemma-7b",
    "google/gemma-2b",
    # Phi
    "microsoft/Phi-3-mini-4k-instruct",
    # Falcon
    "tiiuae/falcon-7b",
    "tiiuae/falcon-40b",
    # Zephyr (popular tune)
    "HuggingFaceH4/zephyr-7b-beta",
]


def list_files(model_repo_name: str) -> list[str] | None:
    """Return list of parquet filenames in a details_<model> repo, or None if 404."""
    try:
        url = f"https://huggingface.co/api/datasets/open-llm-leaderboard-old/details_{model_repo_name.replace('/', '__')}"
        req = urllib.request.Request(url, headers={"User-Agent": "plimsoll-atlas-v0"})
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        return [s["rfilename"] for s in data.get("siblings", [])]
    except Exception as e:
        print(f"  [skip {model_repo_name}] {e}")
        return None


def find_latest_parquet(filenames: list[str], bench_glob: str) -> str | None:
    """Find the most-recent parquet matching the benchmark pattern.

    bench_glob is the substring to match in the filename, e.g.
    'harness|hellaswag|10' or 'harness|gsm8k|5'.
    Returns the full filename (path within the repo) or None.
    """
    matches = [f for f in filenames if bench_glob in f and f.endswith(".parquet")]
    if not matches:
        return None
    # Filenames are like '<timestamp_dir>/details_<bench>_<timestamp>.parquet'.
    # Sort by the timestamp_dir (first path component) → newest last.
    return sorted(matches)[-1]


def download_parquet(model_repo_name: str, filename: str) -> bytes | None:
    """Download a single parquet file."""
    try:
        url = f"https://huggingface.co/datasets/open-llm-leaderboard-old/details_{model_repo_name.replace('/', '__')}/resolve/main/{filename}"
        req = urllib.request.Request(url, headers={"User-Agent": "plimsoll-atlas-v0"})
        return urllib.request.urlopen(req, timeout=120).read()
    except Exception as e:
        print(f"  [download fail {model_repo_name}] {e}")
        return None


def parquet_to_triples(blob: bytes, agent_name: str) -> pd.DataFrame:
    """Extract per-doc (agent, task_id, success) from an lm-eval parquet."""
    df = pd.read_parquet(io.BytesIO(blob))
    # Schema in v1 lm-eval parquets typically has 'doc_id' (or index) + 'metrics' (dict)
    # plus arr columns like 'acc', 'acc_norm', etc.
    # Identify the success column. For HellaSwag: 'acc_norm' or 'acc'. For GSM8K: 'em' or 'acc'.
    success_col = None
    for cand in ["acc_norm", "acc", "em", "exact_match"]:
        if cand in df.columns:
            success_col = cand
            break
    if success_col is None:
        # Try parsing 'metrics' dict
        if "metrics" in df.columns:
            df["__success__"] = df["metrics"].apply(
                lambda m: float(list(m.values())[0]) if isinstance(m, dict) and m else None
            )
            success_col = "__success__"
        else:
            return pd.DataFrame()
    if "doc_id" in df.columns:
        task_id_col = "doc_id"
    elif "id" in df.columns:
        task_id_col = "id"
    else:
        df["__doc_id__"] = df.index
        task_id_col = "__doc_id__"

    out = pd.DataFrame({
        "agent": agent_name,
        "task_id": df[task_id_col].astype(str),
        "success": pd.to_numeric(df[success_col], errors="coerce"),
    })
    out = out.dropna(subset=["success"])
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bench-glob", required=True,
                   help="lm-eval-harness benchmark substring, e.g. 'harness|hellaswag|10' or 'harness|gsm8k|5'.")
    p.add_argument("--out", type=Path, required=True,
                   help="Output triples CSV path.")
    args = p.parse_args()

    all_triples = []
    n_ok = 0
    n_skip = 0

    for i, model in enumerate(LOCKED_MODELS, 1):
        agent_name = model.replace("/", "__")
        print(f"[{i}/{len(LOCKED_MODELS)}] {model}")
        filenames = list_files(model)
        if filenames is None:
            n_skip += 1
            continue
        target = find_latest_parquet(filenames, args.bench_glob)
        if target is None:
            print(f"  [no parquet for {args.bench_glob}]")
            n_skip += 1
            continue
        print(f"  -> {target}")
        blob = download_parquet(model, target)
        if blob is None:
            n_skip += 1
            continue
        triples = parquet_to_triples(blob, agent_name)
        if triples.empty:
            print(f"  [empty after parse]")
            n_skip += 1
            continue
        all_triples.append(triples)
        n_ok += 1

    if not all_triples:
        sys.exit("ERROR: no triples extracted.")
    full = pd.concat(all_triples, ignore_index=True)
    full.to_csv(args.out, index=False)
    print(f"\nWrote {args.out}")
    print(f"  agents OK: {n_ok}  skipped: {n_skip}")
    print(f"  rows: {len(full):,}  agents: {full['agent'].nunique()}  tasks: {full['task_id'].nunique()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
