"""Download archived CATS GTFS-Realtime data (daily Parquet files) from gtfsrt.io.

Usage:
    python3 realtime/download.py vehicle_positions 2026-09-28 2026-10-13
    python3 realtime/download.py trip_updates 2026-09-28

Feed types: trip_updates, vehicle_positions, service_alerts.
Files are saved to realtime/data/<feed_type>/<date>.parquet (git-ignored).
Archive coverage for CATS: 2026-04-13 to 2026-10-13 (see inventory.json).
"""

import base64
import datetime
import os
import sys
import urllib.error
import urllib.request

FEEDS = {
    "trip_updates": "https://gtfsrealtime.ridetransit.org/GTFSRealTime/TripUpdate/Tripupdates.pb",
    "vehicle_positions": "https://gtfsrealtime.ridetransit.org/GTFSRealTime/Vehicle/VehiclePositions.pb",
    "service_alerts": "https://gtfsrealtime.ridetransit.org/GTFSRealTime/Alerts/Alerts.pb",
}
BASE = "https://storage.googleapis.com/parquet.gtfsrt.io"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def main():
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in FEEDS:
        sys.exit(__doc__)
    feed = sys.argv[1]
    start = datetime.date.fromisoformat(sys.argv[2])
    end = datetime.date.fromisoformat(sys.argv[3]) if len(sys.argv) == 4 else start
    key = base64.urlsafe_b64encode(FEEDS[feed].encode()).decode().rstrip("=")
    os.makedirs(os.path.join(OUT, feed), exist_ok=True)

    day = start
    while day <= end:
        dest = os.path.join(OUT, feed, f"{day}.parquet")
        url = f"{BASE}/{feed}/date={day}/base64url={key}/data.parquet"
        if os.path.exists(dest):
            print(f"{day}: already downloaded")
        else:
            try:
                urllib.request.urlretrieve(url, dest + ".part")
                os.rename(dest + ".part", dest)
                print(f"{day}: {os.path.getsize(dest) / 1e6:.1f} MB")
            except urllib.error.HTTPError as e:
                print(f"{day}: not available (HTTP {e.code})")
        day += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
