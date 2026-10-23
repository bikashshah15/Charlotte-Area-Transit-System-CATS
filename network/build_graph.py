#!/usr/bin/env python3
"""Build a CATS transit graph from a static GTFS feed.

Owner: Elijah (data cleaning, graph construction, packaging).

The graph uses stops as nodes and consecutive stops on a trip as edges for one
service date. By default edges are undirected and repeated service on the same
stop pair is collapsed into one edge, which is what NetLogo needs.

Usage:
    python3 network/build_graph.py
    python3 network/build_graph.py --date 20260928 --out network/output
    python3 network/build_graph.py --directed
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def route_mode(route_type):
    if route_type == "0":
        return "rail"
    if route_type == "3":
        return "bus"
    return "other"


def main():
    parser = argparse.ArgumentParser(description="Build a CATS GTFS graph.")
    parser.add_argument(
        "--feed",
        type=Path,
        default=REPO_ROOT / "feeds/2026-fall",
        help="GTFS feed folder (default: feeds/2026-fall in this repo)",
    )
    parser.add_argument(
        "--date",
        default="20260928",
        help="Service date in YYYYMMDD format (default: 20260928, a weekday)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "network/output",
        help="Output folder (default: network/output in this repo)",
    )
    parser.add_argument(
        "--directed",
        action="store_true",
        help="Keep edge direction; otherwise collapse A-B and B-A into one edge",
    )
    args = parser.parse_args()

    stops = {row["stop_id"]: row for row in read_csv(args.feed / "stops.txt")}
    routes = {row["route_id"]: row for row in read_csv(args.feed / "routes.txt")}
    trips = read_csv(args.feed / "trips.txt")
    stop_times = read_csv(args.feed / "stop_times.txt")
    calendar = read_csv(args.feed / "calendar_dates.txt")

    active_services = {
        row["service_id"]
        for row in calendar
        if row["date"] == args.date and row["exception_type"] == "1"
    }
    if not active_services:
        dates = sorted(
            {row["date"] for row in calendar if row["exception_type"] == "1"}
        )
        raise SystemExit(
            f"No service on {args.date}. This feed has service dates "
            f"{dates[0]} through {dates[-1]}."
        )

    active_trips = {
        row["trip_id"]: row for row in trips if row["service_id"] in active_services
    }

    calls_by_trip = defaultdict(list)
    for row in stop_times:
        if row["trip_id"] in active_trips:
            calls_by_trip[row["trip_id"]].append(
                (int(row["stop_sequence"]), row["stop_id"])
            )

    nodes = set()
    routes_at_stop = defaultdict(set)
    edges = defaultdict(lambda: {"routes": set(), "trips": 0})

    for trip_id, calls in calls_by_trip.items():
        calls.sort()
        route_id = active_trips[trip_id]["route_id"]

        for _, stop_id in calls:
            nodes.add(stop_id)
            routes_at_stop[stop_id].add(route_id)

        for (_, from_stop), (_, to_stop) in zip(calls, calls[1:]):
            if from_stop == to_stop:
                continue
            if args.directed:
                key = (from_stop, to_stop)
            else:
                key = tuple(sorted((from_stop, to_stop)))
            edges[key]["routes"].add(route_id)
            edges[key]["trips"] += 1

    args.out.mkdir(parents=True, exist_ok=True)

    with (args.out / "nodes.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["stop_id", "stop_name", "lat", "lon", "mode", "routes"])
        for stop_id in sorted(nodes):
            stop = stops[stop_id]
            stop_routes = sorted(routes_at_stop[stop_id])
            modes = sorted({route_mode(routes[r]["route_type"]) for r in stop_routes})
            mode = modes[0] if len(modes) == 1 else "mixed"
            writer.writerow(
                [
                    stop_id,
                    stop["stop_name"],
                    stop["stop_lat"].strip(),
                    stop["stop_lon"].strip(),
                    mode,
                    ";".join(stop_routes),
                ]
            )

    with (args.out / "edges.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["source", "target", "routes", "trips"])
        for (from_stop, to_stop) in sorted(edges):
            edge = edges[(from_stop, to_stop)]
            writer.writerow(
                [
                    from_stop,
                    to_stop,
                    ";".join(sorted(edge["routes"])),
                    edge["trips"],
                ]
            )

    kind = "directed" if args.directed else "undirected"
    print(
        f"Wrote {len(nodes):,} nodes and {len(edges):,} {kind} edges "
        f"for {args.date} to {args.out}"
    )


if __name__ == "__main__":
    main()
