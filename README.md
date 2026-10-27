# Charlotte-Area-Transit-System-CATS

Public data on the Charlotte Area Transit System (CATS): static GTFS schedules, fares, ridership, and a downloader for archived GTFS-Realtime data.

```
feeds/       Static GTFS schedules, one folder per feed version
fares/       Official fare policy PDFs
ridership/   Route- and mode-level ridership
realtime/    Script to download archived GTFS-Realtime data (data itself not committed)
```

## Network robustness analysis

[`Copy of CATS_Robustness_Experiments.ipynb`](Copy%20of%20CATS_Robustness_Experiments.ipynb) contains the network robustness analysis and its saved outputs. [`export_report_assets.py`](export_report_assets.py) extracts those saved outputs into the report tables, figures, and structured results documented in [`report_assets/README.md`](report_assets/README.md).

The graph inputs used by the notebook, `nodes.csv` and `edges.csv`, are not available in this repository, so the experiments were not rerun and the exported results cannot be independently associated with any of the GTFS feeds below. The report assets preserve the notebook's distinction between exact and approximate betweenness results.

## feeds/ — GTFS schedules

| Folder | Service period | Transitland feed version (SHA1) | Source |
|---|---|---|---|
| [`feeds/2026-fall`](feeds/2026-fall) | 2026-09-28 – 2027-01-31 | `0b81804f8b8c4f38eb242ef77ae40157838a42f1` | [CATS GTFS](https://gtfsrealtime.ridetransit.org/GTFSStatic/api/GTFSDownload/GTFS.zip) |
| [`feeds/2025-fall`](feeds/2025-fall) | 2025-09-17 – 2026-02-01 | `2e36558a41be7de92a40a6894dd670f0733aa90d` | [Mobility Database snapshot `mdb-2265-202509180032`](https://files.mobilitydatabase.org/mdb-2265/mdb-2265-202509180032/mdb-2265-202509180032.zip) |
| [`feeds/2021-fall`](feeds/2021-fall) | 2021-10-09 – 2022-02-06 | `6ffadf06ce0caa621bf6abbaad1ce147e521395f`* | [OpenMobilityData snapshot 2021-11-02](https://openmobilitydata-data.s3.us-west-1.amazonaws.com/public/feeds/charlotte-area-transit-system/1252/20211102/gtfs.zip) |
| [`feeds/2020-fall`](feeds/2020-fall) | 2020-09-11 – 2021-01-31 | `e788f468f8d18a0731c3684929b4358c8b43742a`* | [OpenMobilityData snapshot 2020-09-25](https://openmobilitydata-data.s3.us-west-1.amazonaws.com/public/feeds/charlotte-area-transit-system/1252/20200925/gtfs.zip) |
| [`feeds/2019-fall`](feeds/2019-fall) | 2019-09-10 – 2020-02-02 | `8aaa0eb969917b14cbc0460e66d185cf0268a031`* | [OpenMobilityData snapshot 2019-10-15](https://openmobilitydata-data.s3.us-west-1.amazonaws.com/public/feeds/charlotte-area-transit-system/1252/20191015/gtfs.zip) |

The SHA1 column is the hash of the original GTFS zip. Hashes without `*` match the version listed on Transitland. Those with `*` come from the OpenMobilityData (formerly TransitFeeds) archive, Mobility Database feed `mdb-640`, which Transitland does not have.

In the 2019–2021 feeds, `route_id` combines the route number and the schedule period (e.g. `10-272`, `10-274`), so one route can have several IDs. Use `route_short_name` to compare routes across years.
Archive of all versions: <https://www.transit.land/feeds/f-dnq-charlotteareatransitsystem>

| File | Contents |
|---|---|
| `agency.txt` | Agency name, URL, time zone, phone |
| `routes.txt` | Routes (bus `route_type` 3, light rail/streetcar `route_type` 0) |
| `trips.txt` | Scheduled trips: route, service ID, headsign, direction, block, shape |
| `stop_times.txt` | Arrival/departure time at each stop for every trip |
| `stops.txt` | Stop IDs, names and coordinates |
| `shapes.txt` | GPS points tracing each route's path |
| `calendar_dates.txt` | Dates each service ID runs |

CATS feeds have no `calendar.txt`; service days are defined entirely in `calendar_dates.txt`. They also contain no fare files or `feed_info.txt`.

## fares/ — Fare policies

| File | Fares documented | Source |
|---|---|---|
| [`2025-07-01_MTC-02_fare-policy.pdf`](fares/2025-07-01_MTC-02_fare-policy.pdf) | Fares as of 2025-07-01 (pages 7–8). Approved by the MTC 2025-05-28 | [charlottenc.gov](https://www.charlottenc.gov/files/sharedassets/cats/v/2/mtc-policies/mtc-02-fare-policy.pdf) |
| [`2026-07-01_MPTA_fare-policy.pdf`](fares/2026-07-01_MPTA_fare-policy.pdf) | Fares as of 2026-06-10 and at full Fare Modernization (pages 9–11). Effective 2026-07-01 | [MPTA (Granicus)](https://mpta.granicus.com/MinutesViewer.php?clip_id=182&doc_id=bbe9d7b3-66ab-11f1-9494-005056a89546&view_id=10) |

Adult one-way fares:

| Service | 2025-07-01 | 2026-06-10 | At full modernization |
|---|---:|---:|---:|
| Local bus / LYNX Blue Line | $2.20 | $2.20 | $2.20 |
| Express (within Mecklenburg) | $3.00 | $3.00 | $2.20 |
| Regional Express ("Express Plus") | $4.40 | $4.40 | $3.50 |
| CityLYNX Gold Line (streetcar) | Free | Free | $2.20 |

Modernization fares are phased in as technology becomes available; the policy gives no single changeover date, so don't apply them to all of 2026.

## ridership/

| File | Contents | Source |
|---|---|---|
| [`2026-09-23_ops-safety-committee-packet.pdf`](ridership/2026-09-23_ops-safety-committee-packet.pdf) | MPTA Operations & Safety Committee packet. Pages 18–23: August 2026 performance by mode (OTP definition on page 19). Page 28: ridership by service type. Pages 29–32: ridership by route for Aug 2026, Jul 2026 and Aug 2025 | [MPTA (Granicus)](https://mpta.granicus.com/AgendaViewer.php?clip_id=277&view_id=5) |
| [`ntd_monthly_ridership_cats_40008.csv`](ridership/ntd_monthly_ridership_cats_40008.csv) | FTA National Transit Database monthly ridership for CATS (NTD ID `40008`), Jan 2002 – Aug 2026, by mode and type of service. Filtered from the national dataset | [data.transportation.gov](https://data.transportation.gov/api/v3/views/8bui-9xvu/export.csv?accessType=DOWNLOAD) |

NTD columns: `UPT` unlinked passenger trips (boardings), `VRM` vehicle revenue miles, `VRH` vehicle revenue hours, `VOMS` vehicles operated in maximum service. Mode codes: `MB` bus, `CB` commuter bus (express), `LR` light rail (Blue Line), `SR` streetcar (Gold Line), `DR` demand response (STS/microtransit), `VP` vanpool. Type of service: `DO` directly operated, `PT` purchased transportation. NTD values include FTA adjustments and estimates and are by mode, not by route.

## realtime/ — Archived GTFS-Realtime

The [gtfsrt.io](https://gtfsrt.io) archive has daily Parquet files of CATS's realtime feeds for **2026-04-13 – 2026-10-13** (about 42 GB in total), too large for git. Download the days you need:

```sh
python3 realtime/download.py vehicle_positions 2026-09-28 2026-10-13
python3 realtime/download.py trip_updates 2026-09-28
```

Files go to `realtime/data/<feed_type>/<date>.parquet`, which is git-ignored. Approximate size per day: trip updates ~200 MB, vehicle positions ~45 MB, service alerts ~15 MB. Trip updates contain predictions, not measured arrivals.

## Gaps and terms

- No public realtime archive was found for before 2026-04-13, so there is none for the fall 2025 schedule period.
- Route-level ridership is only available month by month in board packets. There is no public dataset covering every month.
- The CATS PDFs carry no explicit reuse license. NTD data is a U.S. government work.
- Contacts for missing data: CATS Transit Planning (telltransit@charlottenc.gov, 704-336-7433); City of Charlotte public records requests (PublicRecordsRequest@charlottenc.gov).
