#!/usr/bin/env python3
"""Visualize the CATS transit network graph with NetworkX and Matplotlib.

Owner: Elijah (data cleaning, graph construction, packaging).

Loads the packaged graph (nodes.csv / edges.csv) written by build_graph.py and
draws it with NetworkX. Stops are nodes positioned by their lat/lon coordinates;
edges are the consecutive-stop pairs produced by the build step.

Usage:
    python3 network/visualize.py
    python3 network/visualize.py --date 20260928 --out network/output
    python3 network/visualize.py --directed
"""

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

REPO_ROOT = Path(__file__).resolve().parent.parent

MODE_COLORS = {
    "rail": "#1f77b4",
    "bus": "#ff7f0e",
    "mixed": "#2ca02c",
    "other": "#9467bd",
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_graph(nodes_path, edges_path, directed=False):
    graph = nx.DiGraph if directed else nx.Graph
    G = graph(name="CATS")

    for row in read_csv(nodes_path):
        G.add_node(
            row["stop_id"],
            name=row["stop_name"],
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            mode=row["mode"],
            routes=[route for route in row["routes"].split(";") if route],
        )

    for row in read_csv(edges_path):
        G.add_edge(
            row["source"],
            row["target"],
            routes=[route for route in row["routes"].split(";") if route],
            trips=int(row["trips"]),
        )

    return G


def draw_graph(G, ax, date):
    pos = {node: (data["lon"], data["lat"]) for node, data in G.nodes(data=True)}

    node_colors = [
        MODE_COLORS.get(data.get("mode", "other"), "grey")
        for _, data in G.nodes(data=True)
    ]
    degree = dict(G.degree())
    node_sizes = [250 * math.sqrt(degree[node] + 1) for node in G]

    edge_widths = [
        1.0 + 6.0 * math.log1p(G[u][v]["trips"]) for u, v in G.edges
    ]

    nx.draw_networkx_nodes(
        G, pos, node_color=node_colors, node_size=node_sizes, ax=ax
    )
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.35, ax=ax)

    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.set_title(
        f"CATS Transit Network — {date} | "
        f"{G.number_of_nodes()} stops | {G.number_of_edges()} edges | "
        f"{nx.number_connected_components(G)} components"
    )
    return ax


def main():
    parser = argparse.ArgumentParser(description="Visualize the CATS transit network with NetworkX.")
    parser.add_argument(
        "--nodes",
        type=Path,
        default=REPO_ROOT / "network/output/nodes.csv",
        help="Nodes CSV written by build_graph.py (default: network/output/nodes.csv)",
    )
    parser.add_argument(
        "--edges",
        type=Path,
        default=REPO_ROOT / "network/output/edges.csv",
        help="Edges CSV written by build_graph.py (default: network/output/edges.csv)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "network/output/cats_network.png",
        help="Output PNG path (default: network/output/cats_network.png)",
    )
    parser.add_argument(
        "--date",
        default="20260928",
        help="Service date in YYYYMMDD format (default: 20260928)",
    )
    parser.add_argument(
        "--directed",
        action="store_true",
        help="Draw a directed graph; otherwise use an undirected graph",
    )
    args = parser.parse_args()

    G = load_graph(args.nodes, args.edges, directed=args.directed)

    fig, ax = plt.subplots(figsize=(14, 12))
    draw_graph(G, ax, args.date)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150, bbox_inches="tight")
    plt.close(fig)

    kind = "DiGraph" if args.directed else "Graph"
    print(
        f"Drew {G.number_of_nodes():,} stops and {G.number_of_edges():,} {kind} edges "
        f"for {args.date} to {args.out}"
    )


if __name__ == "__main__":
    main()
