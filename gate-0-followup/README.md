# Gate 0 Follow-up — Exploratory

This subdirectory holds **exploratory follow-up analyses on Gate 0 data**. Contents are NOT registered, NOT Plimsoll-compliant, NOT load-bearing for the methodology paper's headline claim.

## Provenance

Gate 0 (the parent of this work) is reclassified as exploratory motivation, not Plimsoll-compliant — see [the parent README](../../README.md) §"Gate 0 — Empirical kill-or-proceed" status note (2026-04-26). Anything done on Gate 0 data inherits that exploratory framing automatically. Descendants cannot be more rigorous than the parent.

The load-bearing prospective replication is **Gate 0.5** (OSF-registered, DOI [10.17605/OSF.IO/G9WFY](https://doi.org/10.17605/OSF.IO/G9WFY)). Robustness pass for Gate 0.5 is locked at OSF Addendum DOI [10.17605/OSF.IO/3PD2A](https://doi.org/10.17605/OSF.IO/3PD2A).

## Contents

- `protocol-stratified.py` — attacks parent README open question #3: does scaffold/temporal shift produce more |Δ effect size| instability than within-scaffold/within-time pairs? Stratifies pairs from Ndzomga 2026's heatmap by (a) intra-scaffold vs inter-scaffold and (b) intra-month vs inter-month download timestamp, reports median |Δ| per stratum per benchmark. Output: `protocol-stratified-summary.csv` + `protocol-stratified-pairs.csv`.

## Audit anchor

Each script in this directory is committed to git **before** it runs. The commit SHA pins the analytic choices (stratification rule, parser logic, band, thresholds). Output CSVs reference the script + commit they were produced under.

## Use in the methodology paper

Findings from this directory go in:
- **Limitations / Future Work**, framed explicitly as exploratory texture, *or*
- A clearly-labeled supplementary descriptive section ("we additionally observed that on Ndzomga's data, |Δ| is X under scaffold shift, Y under temporal shift; this is exploratory and cannot be used to justify a confirmatory mitigation-study claim").

If a result here is paper-headline-worthy, the upgrade path is **registered prospective replication on held-out data** (Gate 0.75 / Gate 1.5 shape) — never retroactive promotion of this exploratory analysis.
