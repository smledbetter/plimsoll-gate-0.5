---
project: Plimsoll
kind: gate-0-exploratory-writeup
status: exploratory — NOT registered, NOT confirmatory
created: 2026-04-26
parent_gate: 0 (reclassified exploratory motivation 2026-04-26)
parent_doi: n/a (Gate 0 unregistered)
script: protocol-stratified.py
script_commit: 430ce5e
data: Ndzomga 2026 all_benchmarks_task_heatmap_data.csv (22,304 rows)
---

# Protocol-stratified |Δ effect size| on Gate 0 data — exploratory texture

## Status

**Exploratory, not Plimsoll-compliant.** Descendant of Gate 0, which is itself reclassified as exploratory motivation, not Plimsoll-compliant. Output is descriptive supplementary texture for the methodology paper's Limitations / Future Work section, never a load-bearing finding.

If anything here is paper-headline-worthy, the upgrade path is **registered prospective replication on held-out data** (Gate 0.75 / Gate 1.5 shape). This file does not justify a confirmatory claim.

## Question

Parent README open question #3:
> Effect-size stability under scaffold/temporal shift specifically. Gate 0 measured stability across agent-pair composition. Ndzomga measured rank stability across his 5 protocols (LOAO/LOSO/temporal/random/intra-scaffold). The natural follow-up is computing |Δ effect size| across those same protocols — does the instability worsen under scaffold shift specifically?

## Method

For each agent pair (a, b) on each benchmark, compute Plimsoll's `effect_full` (mean per-task pass-rate difference over all shared tasks) and `effect_margin` (same on the [0.30, 0.70] capability-margin task subset), inclusion thresholds `(≥20, ≥8)`. Stratify pairs by:

- **Scaffold:** `intra-scaffold` if both agents share the same scaffold prefix (e.g., both "Browser-Use"); `inter-scaffold` otherwise. Scaffold parsed via Ndzomga's `scripts/data.py:parse_scaffold_from_name`.
- **Temporal (release-month):** `intra-month` if both agents have the same parsed (Month Year) parenthetical in the agent name (proxy for model release date); `inter-month` otherwise. Parser matches Ndzomga's `parse_date_from_name`.

Report median |Δ effect size| per stratum per benchmark. Inflation ratio = inter / intra.

(Note: the analyst's first run used `download_timestamp` for the temporal split and got 0 inter-month pairs, confirming `download_timestamp` tracks scrape time — single batch — not release time. The agent-name parenthetical is the right field. Fix committed at `430ce5e`.)

## Results

```
benchmark              stratification.stratum   n     median|Δ|  p95     flip_rate
======================================================================================
corebench_hard         all.all                  703   0.1476     0.4032  5.8%
                       scaffold.intra           346   0.1476     0.3984  6.1%
                       scaffold.inter           357   0.1476     0.4216  5.6%   1.00x
                       temporal.intra           111   0.1254     0.3071  4.5%
                       temporal.inter           592   0.1524     0.4180  6.1%   1.22x

gaia                   all.all                  496   0.0706     0.1824  2.6%
                       scaffold.intra           241   0.0617     0.1784  2.1%
                       scaffold.inter           255   0.0827     0.1835  3.1%   1.34x
                       temporal.intra            69   0.0368     0.1663  1.4%
                       temporal.inter           427   0.0762     0.1841  2.8%   2.07x  **
online_mind2web        all.all                  231   0.0574     0.1789  6.9%
                       scaffold.intra           111   0.0447     0.1789  4.5%
                       scaffold.inter           120   0.0608     0.1782  9.2%   1.36x
                       temporal.intra            50   0.0431     0.1665  10.0%
                       temporal.inter           181   0.0604     0.1811  6.1%   1.40x

swebench_verified_mini all.all                  378   0.1886     0.4455  4.8%
                       scaffold.intra           183   0.1733     0.4214  6.6%
                       scaffold.inter           195   0.2267     0.4600  3.1%   1.31x
                       temporal.intra            63   0.1505     0.4371  6.3%
                       temporal.inter           315   0.1905     0.4504  4.4%   1.27x

taubench_airline       all.all                  325   0.0543     0.1386  3.4%
                       scaffold.intra           157   0.0443     0.1246  1.3%
                       scaffold.inter           168   0.0629     0.1504  5.4%   1.42x
                       temporal.intra            61   0.0500     0.1329  4.9%
                       temporal.inter           264   0.0557     0.1389  3.0%   1.11x

usaco                  all.all                   78   0.1450     0.2818  6.4%
                       scaffold.intra            66   0.1450     0.2902  6.1%
                       scaffold.inter            12   0.1142     0.2650  8.3%   0.79x  small-n
                       temporal.intra            16   0.0830     0.2553  25.0%
                       temporal.inter            62   0.1636     0.2930  1.6%   1.97x  small-n
```

(Full numbers in `protocol-stratified-summary.csv`; pair-level detail with stratum labels in `protocol-stratified-pairs.csv`. Both produced by `protocol-stratified.py` at commit `430ce5e`.)

Six benchmarks — assistantbench dropped (0% in-band per Gate 0), scicode dropped (too few in-band per Gate 0).

## Reading

**Scaffold shift produces modest 1.3-1.4× inflation in median |Δ effect size|** on 4 of 6 benchmarks (gaia, online_mind2web, swebench_verified_mini, taubench_airline). corebench_hard shows zero scaffold effect. usaco reverses direction but inter-scaffold n=12 is too small for confidence.

**Temporal shift produces comparable inflation:** typically 1.1-1.4× on most benchmarks. gaia stands out at 2.07× (n=69 intra-month, 427 inter-month). usaco approaches 2× but with small-n on both sides.

**Neither shift dominates.** No benchmark shows a scaffold-only or temporal-only "this is the load-bearing axis" pattern. The inflation magnitudes from scaffold shift and temporal shift are similar order-of-magnitude on each benchmark.

## What this does NOT support

- "Scaffold shift dominates effect-size instability" — not visible in the data
- "Temporal drift is the primary instability driver" — not visible in the data
- Any per-benchmark band-tuning rule based on scaffold/temporal composition — sample sizes are too small per cell
- Confirmatory inflation magnitudes (everything here is descriptive on a single dataset already known to the analyst)

## Caveats

- Single dataset (Ndzomga 2026), single snapshot. Selection effects in the agent set are unknown.
- Release date is parsed from a human-curated parenthetical; missing or malformed entries are excluded silently. Run log shows ~144 of 144 agents parsed.
- The temporal stratum is "same year-month vs different" — coarse. Finer temporal bins were not explored to limit forking paths in this exploratory pass.
- "Intra-scaffold" pairs vary in agent count by benchmark; some benchmarks have many agents per scaffold and some have few. The intra-scaffold sample is not balanced across scaffolds.

## What the methodology paper can say

> "On Ndzomga's 22,303-row corpus, when paired-effect-size shift |Δ| is stratified by whether the two agents in a pair share scaffold or release-month, both stratifications produce comparable modest inflation (~1.3× typical) of median |Δ| under [0.30, 0.70] capability-margin filtering, with one benchmark (gaia) showing 2× temporal inflation. Neither shift type dominates. This is exploratory texture from a single-snapshot dataset; mitigation studies on any specific benchmark should not assume scaffold or temporal stability of effect sizes — verify per-benchmark, paired with element 4 of the protocol."

That sentence belongs in **Limitations / Future Work**, not in the headline.

## Upgrade path if anyone cares about temporal effects

The natural confirmatory question is *"do effect sizes drift across model release waves?"* — testable on data with controlled temporal spread (e.g., HELM v0/v1/v2/v3 over time, or HuggingFace open-llm-leaderboard with timestamped submissions). Run the same |Δ| stratification on that data with pre-registration. If gaia's 2× temporal inflation replicates → temporal drift is a real instability axis worth its own protocol element.
