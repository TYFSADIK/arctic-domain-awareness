"""Parsers for the public feeds. Keep these thin; everything lands in the event log.

- AIS: CSV export (e.g. from your own RTL-SDR AIS receiver, or AIS Hub)
       columns: mmsi,timestamp,lat,lon,sog,cog
- ADS-B: dump1090 / readsb aircraft.json
- Sentinel-1: ship detections exported from SNAP/ESA's ship detection, or your own CFAR, as CSV
       columns: id,timestamp,lat,lon,length_m,scene
"""
import csv
import json
from datetime import datetime

from .models import AISReport, SARDetection


def _ts(s):
    try:
        return float(s)
    except ValueError:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def read_ais_csv(path):
    with open(path) as fh:
        for row in csv.DictReader(fh):
            yield AISReport(row["mmsi"], _ts(row["timestamp"]), float(row["lat"]), float(row["lon"]),
                            float(row.get("sog") or 0), float(row.get("cog") or 0))


def read_sar_csv(path):
    with open(path) as fh:
        for row in csv.DictReader(fh):
            yield SARDetection(row["id"], _ts(row["timestamp"]), float(row["lat"]), float(row["lon"]),
                               float(row["length_m"]) if row.get("length_m") else None, row.get("scene", ""))


def read_adsb_json(path):
    with open(path) as fh:
        doc = json.load(fh)
    now = doc.get("now", 0)
    for ac in doc.get("aircraft", []):
        if "lat" in ac and "lon" in ac:
            yield {"hex": ac["hex"], "t": now - ac.get("seen_pos", 0), "lat": ac["lat"], "lon": ac["lon"],
                   "alt_ft": ac.get("alt_baro"), "flight": (ac.get("flight") or "").strip()}
