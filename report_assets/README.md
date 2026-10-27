# CATS report assets

These assets were generated from saved outputs in `Copy of CATS_Robustness_Experiments.ipynb`. The required `nodes.csv` and `edges.csv` files were not present, so the experiments were **not rerun**. `export_report_assets.py` parses the notebook outputs and regenerates every file without manual chart-value editing.

## Exported files and report-ready captions

- `structured_results.json` — Canonical structured dataset used to generate all tables and figures. Caption: **Structured results extracted from the saved CATS robustness notebook outputs.**
- `table_01_baseline_network_properties.csv` and `.md` — Caption: **Baseline properties of the undirected, unweighted CATS stop network represented in the notebook.**
- `table_02_ten_percent_node_removal.csv` and `.md` — Caption: **Largest-component retention and pair reachability after removal of 289 stops (approximately 10% of the original network). Random retention is the 100-trial mean; degree and betweenness attacks use static rankings from the original graph.**
- `table_03_retention_by_removal_level.csv` and `.md` — Caption: **Largest-component retention under random removal, static degree attack, and static approximate-betweenness attack across 5–25% node removal. Random values are means of 10 trials per level.**
- `figure_01_ten_percent_node_removal.png` and `.svg` — Caption: **Largest connected component after approximately 10% node removal. Random removal is the 100-trial mean; targeted attacks use static degree and exact-betweenness rankings.**
- `figure_02_retention_by_removal_level.png` and `.svg` — Caption: **Largest-component retention across 5–25% node removal. Random values are 10-trial means; targeted series use static degree and approximate-betweenness rankings.**
- `README.md` — Provenance, captions, metric definitions, notebook references, and limitations for the exported assets.
- `../export_report_assets.py` — Reusable exporter that parses the notebook’s saved outputs and regenerates this folder.

## Metric definitions

**Largest-component retention** is the number of nodes in the largest connected component after removal divided by the **2,899 original stops**, multiplied by 100. Removed stops remain in the denominator. It is therefore not the percentage of surviving stops that remain connected.

**Pair reachability** is the sum of `s(s−1)/2` over all surviving connected components of size `s`, divided by the number of unordered pairs among the **2,899 original stops**, `2899(2899−1)/2`, multiplied by 100. Pairs containing a removed stop count as unreachable because the denominator uses the original network.

## Notebook evidence

| Asset content | Notebook evidence | Status |
|---|---|---|
| Baseline counts | Cells 2–3 saved outputs | Extracted; not recalculated |
| Random 10% mean retention | Cell 6 saved output | 100-trial mean extracted; mean component size was not saved |
| Degree 10% attack | Cell 5 saved output | Extracted; one deterministic static attack |
| Approximate-betweenness 10% attack | Cell 7 saved output | Extracted; `k=200`, seed 42 |
| Exact-betweenness 10% attack | Cell 12 saved output | Extracted; one deterministic static attack |
| Pair reachability | Cell 13 saved output | Extracted; approximate-betweenness reachability was not calculated |
| 5–25% retention table and curve | Cell 10 saved output | Extracted; random uses 10 trials per level and betweenness is approximate |

## Missing data and methodological inconsistencies

- `nodes.csv` and `edges.csv` were unavailable, so input data and saved calculations could not be independently verified.
- The notebook mixes approximate and exact betweenness. The 10% bar chart intentionally uses the exact result from cell 12; the multi-level curve necessarily uses the approximate ranking from cell 10 because no exact multi-level results are available.
- The random 100-trial output reports a mean percentage but not the corresponding mean component size. That table cell is marked `Not available` rather than deriving a potentially misleading value from a rounded percentage.
- Pair reachability was calculated for random removal, degree attack, and exact-betweenness attack only. The approximate-betweenness entry is marked `Not available`.
- Targeted rankings are static: degree or betweenness is calculated on the original graph and is not recalculated after each removal.
- No uncertainty intervals were available, so none are shown.
