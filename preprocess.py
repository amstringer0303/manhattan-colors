#!/usr/bin/env python3
"""
Fetch Manhattan building data from NYC Open Data (PLUTO) and write
manhattan_buildings.json for the index.html visualization.

Usage:
    pip install requests
    python preprocess.py
Then open a local server:
    python -m http.server 8000
    # visit http://localhost:8000
"""
import json
import sys

try:
    import requests
except ImportError:
    sys.exit("Install requests first:  pip install requests")

API = "https://data.cityofnewyork.us/resource/64uk-42ks.json"
LIMIT = 50_000


def fetch_manhattan():
    buildings = []
    offset = 0
    while True:
        params = {
            "borocode": "1",
            "$select": "xcoord,ycoord,yearbuilt,bldgarea,numfloors",
            "$where": (
                "xcoord IS NOT NULL AND ycoord IS NOT NULL "
                "AND yearbuilt > 1800 AND yearbuilt <= 2025"
            ),
            "$limit": LIMIT,
            "$offset": offset,
            "$order": ":id",
        }
        r = requests.get(API, params=params, timeout=60)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        for b in page:
            try:
                x = float(b["xcoord"])
                y = float(b["ycoord"])
                yr = int(float(b["yearbuilt"]))
                area = int(float(b.get("bldgarea") or 0))
                floors = max(1, int(float(b.get("numfloors") or 1)))
                if 1800 < yr <= 2025 and x > 900_000 and y > 100_000:
                    buildings.append([round(x), round(y), yr, area, floors])
            except Exception:
                pass
        print(f"\r  {len(buildings):,} buildings fetched...", end="", flush=True)
        if len(page) < LIMIT:
            break
        offset += LIMIT
    print()
    return buildings


def main():
    print("Fetching Manhattan buildings from NYC Open Data PLUTO...")
    buildings = fetch_manhattan()
    if not buildings:
        sys.exit("No buildings returned — check your internet connection.")

    xs = [b[0] for b in buildings]
    ys = [b[1] for b in buildings]
    meta = {
        "xmin": min(xs), "xmax": max(xs),
        "ymin": min(ys), "ymax": max(ys),
        "count": len(buildings),
    }

    output = {"meta": meta, "buildings": buildings}
    with open("manhattan_buildings.json", "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_mb = len(json.dumps(output, separators=(",", ":"))) / 1e6
    print(f"Saved manhattan_buildings.json  ({len(buildings):,} buildings, {size_mb:.1f} MB)")
    print()
    print("To view:")
    print("  cd manhattan-colors")
    print("  python -m http.server 8000")
    print("  # open http://localhost:8000 in your browser")


if __name__ == "__main__":
    main()
