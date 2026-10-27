#!/usr/bin/env python3
"""Export report-ready CATS robustness tables and figures from saved notebook outputs.

This script does not execute notebook cells. It parses the saved outputs in
Copy of CATS_Robustness_Experiments.ipynb, builds one structured results object,
and generates all assets from that object.
"""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cats_report_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/cats_report_cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "Copy of CATS_Robustness_Experiments.ipynb"
OUTPUT_DIR = ROOT / "report_assets"


def cell_text(cell: dict[str, Any]) -> str:
    parts: list[str] = []
    for output in cell.get("outputs", []):
        if output.get("output_type") == "stream":
            parts.extend(output.get("text", []))
        else:
            value = output.get("data", {}).get("text/plain", [])
            parts.extend(value if isinstance(value, list) else [value])
    return "".join(parts)


def capture(pattern: str, text: str, cast: type = float) -> Any:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"Could not extract saved result matching: {pattern}")
    return cast(match.group(1))


def extract_results() -> dict[str, Any]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    if len(cells) < 14:
        raise ValueError("Expected at least 14 notebook cells.")

    out = {number: cell_text(cells[number - 1]) for number in range(1, 15)}

    stops = capture(r"Number of stops:\s*(\d+)", out[2], int)
    records = capture(r"Number of connections:\s*(\d+)", out[2], int)
    graph_nodes = capture(r"Total nodes:\s*(\d+)", out[3], int)
    graph_edges = capture(r"Total edges:\s*(\d+)", out[3], int)
    components = capture(r"Connected components:\s*(\d+)", out[3], int)
    largest = capture(r"Largest connected component:\s*(\d+)", out[3], int)

    random_100_pct = capture(r"Average percentage connected:\s*([\d.]+)", out[6])
    degree_removed = capture(r"Stops removed:\s*(\d+)", out[5], int)
    degree_size = capture(r"Largest connected group:\s*(\d+)", out[5], int)
    degree_pct = capture(r"Percentage of original network still connected:\s*([\d.]+)", out[5])
    approx_removed = capture(r"Stops removed:\s*(\d+)", out[7], int)
    approx_size = capture(r"Largest connected group:\s*(\d+)", out[7], int)
    approx_pct = capture(r"Percentage of original network still connected:\s*([\d.]+)", out[7])
    exact_removed = capture(r"Stops removed:\s*(\d+)", out[12], int)
    exact_size = capture(r"Largest connected group:\s*(\d+)", out[12], int)
    exact_pct = capture(r"Percentage of original network still connected:\s*([\d.]+)", out[12])

    random_reach = capture(r"Random \(100-trial average\):\s*([\d.]+)", out[13])
    degree_reach = capture(r"Degree attack:\s*([\d.]+)", out[13])
    exact_reach = capture(r"Exact betweenness attack:\s*([\d.]+)", out[13])

    multi_rows = []
    row_pattern = re.compile(
        r"^[ \t]*(5|10|15|20|25)[ \t]+([\d.]+)[ \t]+([\d.]+)[ \t]+([\d.]+)",
        re.MULTILINE,
    )
    for match in row_pattern.finditer(out[10]):
        removal, approximate, degree, random_mean = match.groups()
        multi_rows.append({
            "removal_percent": int(removal),
            "random_10_trial_mean_percent": float(random_mean),
            "static_degree_percent": float(degree),
            "static_approximate_betweenness_percent": float(approximate),
        })
    if len(multi_rows) != 5:
        raise ValueError(f"Expected five multi-level result rows; found {len(multi_rows)}.")

    return {
        "provenance": {
            "source_notebook": NOTEBOOK.name,
            "experiments_rerun": False,
            "reason": "nodes.csv and edges.csv were unavailable; values were extracted from saved notebook outputs.",
        },
        "baseline": [{
            "stops": stops,
            "connection_records": records,
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges,
            "connected_components": components,
            "largest_connected_component": largest,
            "largest_component_percent_of_original_stops": round(largest / stops * 100, 2),
        }],
        "ten_percent_removal": [
            {
                "removal_strategy": "Random removal (100-trial mean)",
                "betweenness_method": "Not applicable",
                "number_removed": degree_removed,
                "largest_component_size_or_mean": "Not available",
                "largest_component_percent": random_100_pct,
                "pair_reachability_percent": random_reach,
                "trial_count": 100,
                "note": "Mean component size was not printed in the saved output; only the mean percentage was saved.",
            },
            {
                "removal_strategy": "Static degree attack",
                "betweenness_method": "Not applicable",
                "number_removed": degree_removed,
                "largest_component_size_or_mean": degree_size,
                "largest_component_percent": degree_pct,
                "pair_reachability_percent": degree_reach,
                "trial_count": 1,
                "note": "Deterministic attack using degree ranking from the original graph.",
            },
            {
                "removal_strategy": "Static approximate-betweenness attack",
                "betweenness_method": "Approximate, k=200, seed=42",
                "number_removed": approx_removed,
                "largest_component_size_or_mean": approx_size,
                "largest_component_percent": approx_pct,
                "pair_reachability_percent": "Not available",
                "trial_count": 1,
                "note": "Pair reachability was not calculated for the approximate-betweenness graph.",
            },
            {
                "removal_strategy": "Static exact-betweenness attack",
                "betweenness_method": "Exact",
                "number_removed": exact_removed,
                "largest_component_size_or_mean": exact_size,
                "largest_component_percent": exact_pct,
                "pair_reachability_percent": exact_reach,
                "trial_count": 1,
                "note": "Deterministic attack using exact betweenness ranking from the original graph.",
            },
        ],
        "removal_curve": multi_rows,
    }


def display_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_table(stem: str, headers: list[tuple[str, str]], rows: list[dict[str, Any]]) -> None:
    csv_path = OUTPUT_DIR / f"{stem}.csv"
    md_path = OUTPUT_DIR / f"{stem}.md"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[label for _, label in headers],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({label: display_value(row[key]) for key, label in headers})

    labels = [label for _, label in headers]
    lines = [
        "| " + " | ".join(labels) + " |",
        "| " + " | ".join("---" for _ in labels) + " |",
    ]
    for row in rows:
        values = [display_value(row[key]).replace("|", "\\|") for key, _ in headers]
        lines.append("| " + " | ".join(values) + " |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUTPUT_DIR / f"{stem}.png", dpi=300, facecolor="white", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / f"{stem}.svg", facecolor="white", bbox_inches="tight")
    plt.close(fig)


def create_figures(results: dict[str, Any]) -> None:
    colors = {"random": "#3B82F6", "degree": "#E45756", "betweenness": "#2A9D8F"}
    ten = {row["removal_strategy"]: row for row in results["ten_percent_removal"]}
    labels = ["Random\n(100-trial mean)", "Static degree\nattack", "Static exact-\nbetweenness attack"]
    values = [
        ten["Random removal (100-trial mean)"]["largest_component_percent"],
        ten["Static degree attack"]["largest_component_percent"],
        ten["Static exact-betweenness attack"]["largest_component_percent"],
    ]
    fig, ax = plt.subplots(figsize=(8.4, 5.2), facecolor="white")
    bars = ax.bar(labels, values, color=[colors["random"], colors["degree"], colors["betweenness"]], width=0.64)
    ax.set_title("Largest-Component Retention After 10% Node Removal", pad=14, weight="semibold")
    ax.set_ylabel("Largest connected component (% of original stops)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 2, f"{value:.2f}%", ha="center", va="bottom", fontsize=10)
    fig.tight_layout(pad=1.2)
    save_figure(fig, "figure_01_ten_percent_node_removal")

    curve = results["removal_curve"]
    x = [row["removal_percent"] for row in curve]
    fig, ax = plt.subplots(figsize=(8.4, 5.2), facecolor="white")
    ax.plot(x, [row["random_10_trial_mean_percent"] for row in curve], marker="o", linewidth=2.2,
            color=colors["random"], label="Random (10-trial mean)")
    ax.plot(x, [row["static_degree_percent"] for row in curve], marker="o", linewidth=2.2,
            color=colors["degree"], label="Static degree attack")
    ax.plot(x, [row["static_approximate_betweenness_percent"] for row in curve], marker="o", linewidth=2.2,
            color=colors["betweenness"], label="Static approximate-betweenness attack")
    ax.set_title("Network Retention Across Node-Removal Levels", pad=14, weight="semibold")
    ax.set_xlabel("Nodes removed (%)")
    ax.set_ylabel("Largest connected component (% of original stops)")
    ax.set_xticks(x)
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.22)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout(pad=1.2)
    save_figure(fig, "figure_02_retention_by_removal_level")


def write_readme() -> None:
    text = """# CATS report assets

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
"""
    (OUTPUT_DIR / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    results = extract_results()
    (OUTPUT_DIR / "structured_results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )

    write_table("table_01_baseline_network_properties", [
        ("stops", "Stops"),
        ("graph_edges", "Edges"),
        ("connected_components", "Connected components"),
        ("largest_connected_component", "Largest component"),
        ("largest_component_percent_of_original_stops", "Largest component (% of original stops)"),
    ], results["baseline"])
    write_table("table_02_ten_percent_node_removal", [
        ("removal_strategy", "Removal strategy"),
        ("betweenness_method", "Betweenness method"),
        ("number_removed", "Number removed"),
        ("largest_component_size_or_mean", "Largest-component size or mean"),
        ("largest_component_percent", "Largest-component percentage"),
        ("pair_reachability_percent", "Pair reachability percentage"),
        ("trial_count", "Trial count"),
        ("note", "Note"),
    ], results["ten_percent_removal"])
    write_table("table_03_retention_by_removal_level", [
        ("removal_percent", "Removal percentage"),
        ("random_10_trial_mean_percent", "Random mean (10 trials)"),
        ("static_degree_percent", "Static degree attack"),
        ("static_approximate_betweenness_percent", "Static approximate-betweenness attack"),
    ], results["removal_curve"])
    create_figures(results)
    write_readme()


if __name__ == "__main__":
    main()
