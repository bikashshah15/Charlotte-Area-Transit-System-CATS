# Charlotte-Area-Transit-System-CATS

Static GTFS schedule feeds for the Charlotte Area Transit System (CATS), one folder per feed version.

## Feeds

| Folder | Service period | Transitland feed version (SHA1) | Source |
|---|---|---|---|
| [`feeds/2026-fall`](feeds/2026-fall) | 2026-09-28 – 2027-01-31 | `0b81804f8b8c4f38eb242ef77ae40157838a42f1` | [CATS GTFS](https://gtfsrealtime.ridetransit.org/GTFSStatic/api/GTFSDownload/GTFS.zip) |
| `feeds/2025-fall` (pending) | 2025-09-17 – 2026-02-01 | `2e36558a41be7de92a40a6894dd670f0733aa90d` | [Transitland archive](https://www.transit.land/feeds/f-dnq-charlotteareatransitsystem/versions/2e36558a41be7de92a40a6894dd670f0733aa90d) |

Archive of all versions: <https://www.transit.land/feeds/f-dnq-charlotteareatransitsystem>

## Files in each feed

| File | Contents |
|---|---|
| `agency.txt` | Agency name, URL, time zone, phone |
| `routes.txt` | Routes (bus `route_type` 3, light rail/streetcar `route_type` 0) |
| `trips.txt` | Scheduled trips: route, service ID, headsign, direction, block, shape |
| `stop_times.txt` | Arrival/departure time at each stop for every trip |
| `stops.txt` | Stop IDs, names and coordinates |
| `shapes.txt` | GPS points tracing each route's path |
| `calendar_dates.txt` | Dates each service ID runs |

CATS feeds have no `calendar.txt`; service days are defined entirely in `calendar_dates.txt`.
