"""Plimsoll Gate 0.5 — robustness pass orchestrator.

Runs every variant locked in OSF Addendum DOI 10.17605/OSF.IO/3PD2A:

  A. Margin band sweep   — 3 new bands × 3 sources
  B. MMLU-Pro per-discipline  — 14 disciplines
  C. LCB --no-dedup
  D. SWE-bench --exclude-no-logs
  E. Logit-space  — SWE-bench + LiveCodeBench
  F. Inclusion-threshold sweep — 2 new settings × 3 sources
  G. Seed stability  — 11 seeds on SWE-bench primary
  H. Audit re-run at 4 bands  — LiveCodeBench
  I. Audit under logit m_b  — LiveCodeBench (depends on E)

Per variant cell: prep (if needed) → analyze → null-baseline → compute-flip-rate.
Logs every subprocess invocation to <out_dir>/run-log.txt with ISO-8601 timestamp,
command line, exit code, wall-clock seconds.

Captures environment at start: uname, Python version, pip freeze, np.show_config(),
requirements.txt sha256.

Failures in individual cells are logged but do not abort the run; the goal is
to capture every cell's outcome, not to bail on first error.

Usage:
  python run-robustness.py \\
    --triples-dir ~/projects/plimsoll-gate-0.5/component-c \\
    --out-dir robustness \\
    [--skip-variants F,G]   # optional comma-sep list
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ALL_VARIANTS = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

# Variant A: margin band sweep. 3 new bands (registered baseline excluded).
A_BANDS = [
    ("0.25-0.75", 0.25, 0.75),
    ("0.35-0.65", 0.35, 0.65),
    ("0.40-0.60", 0.40, 0.60),
]

# Variant F: inclusion-threshold sweep. 2 new settings (registered baseline excluded).
F_THRESHOLDS = [
    ("loose-10-4", 10, 4),
    ("strict-30-15", 30, 15),
]

# Variant G: seeds. Registered seed=42; sweep 0..9.
G_SEEDS = list(range(10))

SOURCES = [
    # (source_name, prep_script, prep_args (or None for "use existing triples"),
    #  triples-relative-path)
    ("swebench-verified", None, None, "swebench/swebench-triples.csv"),
    ("livecodebench",     None, None, "livecodebench/livecodebench-triples.csv"),
    ("mmlu-pro",          None, None, "mmlu-pro/mmlu-pro-triples.csv"),
]

# MMLU-Pro disciplines (14, per Component C output). Discovered at runtime
# from the per-discipline summary CSV; this constant is a fallback if the
# discovery fails.
MMLU_DISCIPLINES_FALLBACK = [
    "biology", "business", "chemistry", "computer_science", "economics",
    "engineering", "health", "history", "law", "math", "other",
    "philosophy", "physics", "psychology",
]


class Logger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = log_path.open("a", buffering=1)
        self.fh.write(f"\n=== run-robustness.py session start: {self._now()} ===\n")

    def close(self):
        self.fh.write(f"=== session end: {self._now()} ===\n")
        self.fh.close()

    @staticmethod
    def _now() -> str:
        return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    def log(self, msg: str):
        line = f"[{self._now()}] {msg}"
        print(line, flush=True)
        self.fh.write(line + "\n")

    def run(self, cmd: list[str], cwd: Path | None = None) -> int:
        cmd_s = " ".join(repr(c) if " " in c else c for c in cmd)
        self.log(f"$ {cmd_s}")
        t0 = time.time()
        try:
            cp = subprocess.run(cmd, cwd=cwd, check=False)
            rc = cp.returncode
        except FileNotFoundError as e:
            self.log(f"  ERROR: {e}")
            return 127
        wall = time.time() - t0
        self.log(f"  -> rc={rc} wall={wall:.1f}s")
        return rc


def capture_env(out_dir: Path, log: Logger, gate_dir: Path):
    env_path = out_dir / "environment.txt"
    log.log(f"Capturing environment to {env_path}")
    with env_path.open("w") as f:
        f.write(f"=== captured: {dt.datetime.now(dt.timezone.utc).isoformat()} ===\n\n")
        for label, cmd in [
            ("uname -a", ["uname", "-a"]),
            ("python --version", [sys.executable, "--version"]),
            ("pip freeze", [sys.executable, "-m", "pip", "freeze"]),
        ]:
            f.write(f"--- {label} ---\n")
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, check=False)
                f.write(r.stdout + r.stderr + "\n")
            except Exception as e:
                f.write(f"(error: {e})\n")
        f.write("--- numpy.show_config() ---\n")
        try:
            import numpy as np
            from io import StringIO
            buf = StringIO()
            np.show_config(mode="dicts")  # newer numpy
            f.write(json.dumps(np.show_config(mode="dicts"), indent=2, default=str))
            f.write("\n")
        except Exception as e:
            try:
                import numpy as np
                np.show_config()  # legacy: prints to stdout, can't capture cleanly
                f.write(f"(legacy show_config; not captured: numpy {np.__version__})\n")
            except Exception as e2:
                f.write(f"(error: {e2})\n")
        f.write("--- requirements.txt sha256 ---\n")
        req = gate_dir / "requirements.txt"
        if req.exists():
            f.write(hashlib.sha256(req.read_bytes()).hexdigest() + "  " + str(req) + "\n")
        else:
            f.write(f"(not found: {req})\n")


def variant_C(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              baseline_pairs: dict[str, Path]) -> None:
    """LCB --no-dedup."""
    log.log("\n========== Variant C: LCB --no-dedup ==========")
    cell = out_dir / "C-lcb-no-dedup"
    cell.mkdir(parents=True, exist_ok=True)
    repo = Path(os.path.expanduser("~/data/livecodebench-submissions"))
    if not repo.exists():
        log.log(f"  SKIP: LiveCodeBench repo not found at {repo}")
        return
    triples_out = cell / "lcb-no-dedup-triples.csv"
    log.run([sys.executable, str(gate_dir / "prep-livecodebench.py"),
             "--repo", str(repo), "--out", str(triples_out), "--no-dedup"])
    pairs_out = cell / "pairs.csv"
    summary_out = cell / "summary.csv"
    log.run([sys.executable, str(gate_dir / "analyze.py"),
             "--input", str(triples_out), "--out", str(pairs_out),
             "--summary-out", str(summary_out),
             "--source-name", "livecodebench"])
    null_out = cell / "null.csv"
    log.run([sys.executable, str(gate_dir / "null-baseline.py"),
             "--input", str(triples_out), "--pairs", str(pairs_out),
             "--out", str(null_out), "--source-name", "livecodebench"])
    flip_out = cell / "flip-rate.csv"
    log.run([sys.executable, str(gate_dir / "compute-flip-rate.py"),
             "--baseline", str(baseline_pairs["livecodebench"]),
             "--variant", str(pairs_out),
             "--out", str(flip_out),
             "--source", "livecodebench",
             "--variant-name", "C-no-dedup"])


def variant_D(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              baseline_pairs: dict[str, Path]) -> None:
    """SWE-bench --exclude-no-logs."""
    log.log("\n========== Variant D: SWE --exclude-no-logs ==========")
    cell = out_dir / "D-swe-exclude-no-logs"
    cell.mkdir(parents=True, exist_ok=True)
    repo = Path(os.path.expanduser("~/data/swebench-experiments"))
    instance_list = Path(os.path.expanduser("~/data/swebench-verified-instances.txt"))
    if not repo.exists() or not instance_list.exists():
        log.log(f"  SKIP: SWE-bench repo or instance list not found ({repo}, {instance_list})")
        return
    triples_out = cell / "swe-exclude-no-logs-triples.csv"
    log.run([sys.executable, str(gate_dir / "prep-swebench.py"),
             "--repo", str(repo), "--instance-list", str(instance_list),
             "--out", str(triples_out), "--exclude-no-logs"])
    pairs_out = cell / "pairs.csv"
    summary_out = cell / "summary.csv"
    log.run([sys.executable, str(gate_dir / "analyze.py"),
             "--input", str(triples_out), "--out", str(pairs_out),
             "--summary-out", str(summary_out),
             "--source-name", "swebench-verified"])
    null_out = cell / "null.csv"
    log.run([sys.executable, str(gate_dir / "null-baseline.py"),
             "--input", str(triples_out), "--pairs", str(pairs_out),
             "--out", str(null_out), "--source-name", "swebench-verified"])
    flip_out = cell / "flip-rate.csv"
    log.run([sys.executable, str(gate_dir / "compute-flip-rate.py"),
             "--baseline", str(baseline_pairs["swebench-verified"]),
             "--variant", str(pairs_out),
             "--out", str(flip_out),
             "--source", "swebench-verified",
             "--variant-name", "D-exclude-no-logs"])


def variant_A(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              baseline_pairs: dict[str, Path]) -> None:
    """Margin band sweep — 3 new bands × 3 sources."""
    log.log("\n========== Variant A: margin band sweep ==========")
    for source_name, _, _, rel in SOURCES:
        triples = triples_dir / rel
        if not triples.exists():
            log.log(f"  SKIP {source_name}: triples not found at {triples}")
            continue
        for label, lo, hi in A_BANDS:
            cell = out_dir / "A-band-sweep" / f"{source_name}__{label}"
            cell.mkdir(parents=True, exist_ok=True)
            pairs = cell / "pairs.csv"
            summary = cell / "summary.csv"
            null_out = cell / "null.csv"
            flip_out = cell / "flip-rate.csv"
            log.run([sys.executable, str(gate_dir / "analyze.py"),
                     "--input", str(triples), "--out", str(pairs),
                     "--summary-out", str(summary),
                     "--source-name", source_name,
                     "--margin-lo", str(lo), "--margin-hi", str(hi)])
            log.run([sys.executable, str(gate_dir / "null-baseline.py"),
                     "--input", str(triples), "--pairs", str(pairs),
                     "--out", str(null_out), "--source-name", source_name,
                     "--margin-lo", str(lo), "--margin-hi", str(hi)])
            log.run([sys.executable, str(gate_dir / "compute-flip-rate.py"),
                     "--baseline", str(baseline_pairs[source_name]),
                     "--variant", str(pairs),
                     "--out", str(flip_out),
                     "--source", source_name,
                     "--variant-name", f"A-band-{label}"])


def variant_B(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              baseline_pairs: dict[str, Path]) -> None:
    """MMLU-Pro per-discipline — 14 disciplines."""
    log.log("\n========== Variant B: MMLU-Pro per-discipline ==========")
    triples = triples_dir / "mmlu-pro/mmlu-pro-triples.csv"
    if not triples.exists():
        log.log(f"  SKIP: MMLU-Pro triples not found at {triples}")
        return
    # Discover disciplines from the triples file.
    try:
        import pandas as pd
        df_head = pd.read_csv(triples, usecols=["benchmark_name"])
        disciplines = sorted(df_head["benchmark_name"].unique())
    except Exception:
        disciplines = MMLU_DISCIPLINES_FALLBACK
    log.log(f"  disciplines: {disciplines}")
    for d in disciplines:
        d_safe = d.replace("/", "_").replace(" ", "_")
        cell = out_dir / "B-mmlu-per-discipline" / d_safe
        cell.mkdir(parents=True, exist_ok=True)
        pairs = cell / "pairs.csv"
        summary = cell / "summary.csv"
        null_out = cell / "null.csv"
        flip_out = cell / "flip-rate.csv"
        log.run([sys.executable, str(gate_dir / "analyze.py"),
                 "--input", str(triples), "--out", str(pairs),
                 "--summary-out", str(summary),
                 "--source-name", "mmlu-pro",
                 "--filter-benchmark", d])
        log.run([sys.executable, str(gate_dir / "null-baseline.py"),
                 "--input", str(triples), "--pairs", str(pairs),
                 "--out", str(null_out), "--source-name", "mmlu-pro",
                 "--filter-benchmark", d])
        log.run([sys.executable, str(gate_dir / "compute-flip-rate.py"),
                 "--baseline", str(baseline_pairs["mmlu-pro"]),
                 "--variant", str(pairs),
                 "--out", str(flip_out),
                 "--source", "mmlu-pro",
                 "--variant-name", f"B-disc-{d_safe}"])


def variant_E(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              baseline_pairs: dict[str, Path]) -> Path | None:
    """Logit-space — SWE-bench + LiveCodeBench. Returns LCB logit pairs path for variant I."""
    log.log("\n========== Variant E: logit-space ==========")
    lcb_logit_pairs: Path | None = None
    for source_name, rel in [
        ("swebench-verified", "swebench/swebench-triples.csv"),
        ("livecodebench",     "livecodebench/livecodebench-triples.csv"),
    ]:
        triples = triples_dir / rel
        if not triples.exists():
            log.log(f"  SKIP {source_name}: triples not found at {triples}")
            continue
        cell = out_dir / "E-logit" / source_name
        cell.mkdir(parents=True, exist_ok=True)
        pairs = cell / "pairs.csv"
        summary = cell / "summary.csv"
        null_out = cell / "null.csv"
        flip_out = cell / "flip-rate.csv"
        log.run([sys.executable, str(gate_dir / "analyze-logit.py"),
                 "--input", str(triples), "--out", str(pairs),
                 "--summary-out", str(summary),
                 "--source-name", source_name])
        # Note: null-baseline stays raw-scale; logit re-run is for the magnitude diagnostic.
        log.run([sys.executable, str(gate_dir / "compute-flip-rate.py"),
                 "--baseline", str(baseline_pairs[source_name]),
                 "--variant", str(pairs),
                 "--out", str(flip_out),
                 "--source", source_name,
                 "--variant-name", "E-logit"])
        if source_name == "livecodebench":
            lcb_logit_pairs = pairs
    return lcb_logit_pairs


def variant_F(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              baseline_pairs: dict[str, Path]) -> None:
    """Inclusion-threshold sweep — 2 new settings × 3 sources."""
    log.log("\n========== Variant F: inclusion-threshold sweep ==========")
    for source_name, _, _, rel in SOURCES:
        triples = triples_dir / rel
        if not triples.exists():
            log.log(f"  SKIP {source_name}: triples not found at {triples}")
            continue
        for label, mf, mm in F_THRESHOLDS:
            cell = out_dir / "F-threshold-sweep" / f"{source_name}__{label}"
            cell.mkdir(parents=True, exist_ok=True)
            pairs = cell / "pairs.csv"
            summary = cell / "summary.csv"
            null_out = cell / "null.csv"
            flip_out = cell / "flip-rate.csv"
            log.run([sys.executable, str(gate_dir / "analyze.py"),
                     "--input", str(triples), "--out", str(pairs),
                     "--summary-out", str(summary),
                     "--source-name", source_name,
                     "--min-shared-full", str(mf), "--min-shared-margin", str(mm)])
            log.run([sys.executable, str(gate_dir / "null-baseline.py"),
                     "--input", str(triples), "--pairs", str(pairs),
                     "--out", str(null_out), "--source-name", source_name,
                     "--min-shared-full", str(mf), "--min-shared-margin", str(mm)])
            log.run([sys.executable, str(gate_dir / "compute-flip-rate.py"),
                     "--baseline", str(baseline_pairs[source_name]),
                     "--variant", str(pairs),
                     "--out", str(flip_out),
                     "--source", source_name,
                     "--variant-name", f"F-thresh-{label}"])


def variant_G(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              baseline_pairs: dict[str, Path]) -> None:
    """Seed stability — 11 seeds on SWE-bench primary."""
    log.log("\n========== Variant G: seed stability (SWE-bench × 11 seeds) ==========")
    triples = triples_dir / "swebench/swebench-triples.csv"
    pairs = baseline_pairs["swebench-verified"]
    if not triples.exists() or not pairs.exists():
        log.log(f"  SKIP: triples or baseline pairs not found ({triples}, {pairs})")
        return
    cell = out_dir / "G-seed-stability"
    cell.mkdir(parents=True, exist_ok=True)
    seeds = G_SEEDS + [42]
    for s in seeds:
        out = cell / f"null-seed-{s:02d}.csv"
        log.run([sys.executable, str(gate_dir / "null-baseline.py"),
                 "--input", str(triples), "--pairs", str(pairs),
                 "--out", str(out), "--source-name", "swebench-verified",
                 "--seed", str(s)])


def variant_H(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path) -> None:
    """Audit re-run at 4 bands — LiveCodeBench."""
    log.log("\n========== Variant H: audit-by-band on LCB ==========")
    triples = triples_dir / "livecodebench/livecodebench-triples.csv"
    if not triples.exists():
        log.log(f"  SKIP: LCB triples not found at {triples}")
        return
    bands = [("0.30-0.70-baseline", 0.30, 0.70)] + A_BANDS
    cell = out_dir / "H-audit-by-band"
    cell.mkdir(parents=True, exist_ok=True)
    # For each band, compute m_b first by re-running analyze.py at that band,
    # then run audit with --m-b set to that band's median |Δ|.
    for label, lo, hi in bands:
        sub = cell / label
        sub.mkdir(parents=True, exist_ok=True)
        pairs = sub / "pairs.csv"
        log.run([sys.executable, str(gate_dir / "analyze.py"),
                 "--input", str(triples), "--out", str(pairs),
                 "--source-name", "livecodebench",
                 "--margin-lo", str(lo), "--margin-hi", str(hi)])
        # Read m_b from pairs.csv
        try:
            import pandas as pd
            df = pd.read_csv(pairs)
            m_b = float(df["abs_delta"].median())
        except Exception as e:
            log.log(f"  ERROR reading m_b from {pairs}: {e}")
            continue
        log.log(f"  band {label}: m_b={m_b:.4f} (n_pairs={len(df)})")
        audit_out = sub / "audit.csv"
        log.run([sys.executable, str(gate_dir / "audit-reasoning-modes.py"),
                 "--input", str(triples), "--out", str(audit_out),
                 "--m-b", str(m_b),
                 "--margin-lo", str(lo), "--margin-hi", str(hi)])


def variant_I(log: Logger, gate_dir: Path, triples_dir: Path, out_dir: Path,
              lcb_logit_pairs: Path | None) -> None:
    """Audit under logit m_b — LiveCodeBench. Depends on E."""
    log.log("\n========== Variant I: audit under logit m_b ==========")
    triples = triples_dir / "livecodebench/livecodebench-triples.csv"
    if not triples.exists():
        log.log(f"  SKIP: LCB triples not found at {triples}")
        return
    if lcb_logit_pairs is None or not lcb_logit_pairs.exists():
        log.log(f"  SKIP: LCB logit pairs not produced by variant E")
        return
    try:
        import pandas as pd
        df = pd.read_csv(lcb_logit_pairs)
        m_b_logit = float(df["abs_delta"].median())
    except Exception as e:
        log.log(f"  ERROR reading m_b from {lcb_logit_pairs}: {e}")
        return
    log.log(f"  logit m_b={m_b_logit:.4f}")
    cell = out_dir / "I-audit-under-logit"
    cell.mkdir(parents=True, exist_ok=True)
    log.run([sys.executable, str(gate_dir / "audit-reasoning-modes.py"),
             "--input", str(triples), "--out", str(cell / "audit.csv"),
             "--m-b", str(m_b_logit)])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--triples-dir", type=Path, required=True,
                   help="Directory containing <source>/<source>-triples.csv files.")
    p.add_argument("--out-dir", type=Path, default=Path("robustness"))
    p.add_argument("--baseline-runs", type=Path,
                   default=Path("component-c-runs"),
                   help="Directory containing the registered baseline pairs CSVs.")
    p.add_argument("--gate-dir", type=Path, default=Path.cwd(),
                   help="Directory containing analyze.py, null-baseline.py, etc.")
    p.add_argument("--skip-variants", type=str, default="",
                   help="Comma-separated list of variants to skip (e.g. 'F,G').")
    p.add_argument("--only-variants", type=str, default="",
                   help="If set, run ONLY these variants (overrides --skip).")
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    log = Logger(args.out_dir / "run-log.txt")

    skip = set(s.strip().upper() for s in args.skip_variants.split(",") if s.strip())
    only = set(s.strip().upper() for s in args.only_variants.split(",") if s.strip())
    to_run = [v for v in ALL_VARIANTS if (v not in skip) and (not only or v in only)]
    log.log(f"Variants to run: {to_run}")
    log.log(f"Triples dir:  {args.triples_dir}")
    log.log(f"Out dir:      {args.out_dir}")
    log.log(f"Baseline:     {args.baseline_runs}")

    capture_env(args.out_dir, log, args.gate_dir)

    baseline_pairs = {
        "swebench-verified": args.baseline_runs / "swebench" / "swebench-pairs.csv",
        "livecodebench":     args.baseline_runs / "livecodebench" / "livecodebench-pairs.csv",
        "mmlu-pro":          args.baseline_runs / "mmlu-pro" / "mmlu-pro-pairs.csv",
    }
    for k, v in baseline_pairs.items():
        ok = v.exists()
        log.log(f"  baseline {k}: {v} {'OK' if ok else 'MISSING'}")

    lcb_logit_pairs: Path | None = None

    if "C" in to_run:
        variant_C(log, args.gate_dir, args.triples_dir, args.out_dir, baseline_pairs)
    if "D" in to_run:
        variant_D(log, args.gate_dir, args.triples_dir, args.out_dir, baseline_pairs)
    if "A" in to_run:
        variant_A(log, args.gate_dir, args.triples_dir, args.out_dir, baseline_pairs)
    if "B" in to_run:
        variant_B(log, args.gate_dir, args.triples_dir, args.out_dir, baseline_pairs)
    if "E" in to_run:
        lcb_logit_pairs = variant_E(log, args.gate_dir, args.triples_dir, args.out_dir, baseline_pairs)
    if "F" in to_run:
        variant_F(log, args.gate_dir, args.triples_dir, args.out_dir, baseline_pairs)
    if "G" in to_run:
        variant_G(log, args.gate_dir, args.triples_dir, args.out_dir, baseline_pairs)
    if "H" in to_run:
        variant_H(log, args.gate_dir, args.triples_dir, args.out_dir)
    if "I" in to_run:
        variant_I(log, args.gate_dir, args.triples_dir, args.out_dir, lcb_logit_pairs)

    log.log("\nDONE.")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
