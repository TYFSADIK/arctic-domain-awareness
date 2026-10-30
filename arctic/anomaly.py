"""Anomaly rules.

1. AIS gap: a vessel that was transmitting goes silent longer than `gap_s`
   while not near a port, which suggests AIS was switched off.
2. Dark vessel: a SAR ship detection with no AIS track that could plausibly be
   there at the image time.
3. Speed jump: consecutive AIS fixes that imply an impossible speed (spoofing).
"""
from collections import defaultdict

from .models import dead_reckon, haversine_km


def ais_gaps(reports, gap_s=6 * 3600, ports=(), port_radius_km=10):
    by = defaultdict(list)
    for r in reports:
        by[r.mmsi].append(r)
    out = []
    for mmsi, rs in by.items():
        rs.sort(key=lambda r: r.t)
        for a, b in zip(rs, rs[1:]):
            if b.t - a.t >= gap_s and not any(haversine_km(a.lat, a.lon, p[0], p[1]) < port_radius_km for p in ports):
                out.append({"rule": "ais_gap", "mmsi": mmsi, "start": a.t, "end": b.t,
                            "hours": round((b.t - a.t) / 3600, 1), "lat": a.lat, "lon": a.lon})
    return out


def speed_jumps(reports, max_kn=40):
    by = defaultdict(list)
    for r in reports:
        by[r.mmsi].append(r)
    out = []
    for mmsi, rs in by.items():
        rs.sort(key=lambda r: r.t)
        for a, b in zip(rs, rs[1:]):
            dt = b.t - a.t
            if dt <= 0:
                continue
            kn = haversine_km(a.lat, a.lon, b.lat, b.lon) / 1.852 / (dt / 3600)
            if kn > max_kn:
                out.append({"rule": "speed_jump", "mmsi": mmsi, "t": b.t, "implied_kn": round(kn)})
    return out


def dark_vessels(sar_dets, reports, window_s=1800, match_km=5.0):
    """SAR detections not explained by any AIS track within +-window_s."""
    out = []
    for d in sar_dets:
        matched = None
        for r in reports:
            if abs(r.t - d.t) > window_s:
                continue
            lat, lon = dead_reckon(r, d.t)
            if haversine_km(lat, lon, d.lat, d.lon) <= match_km:
                matched = r.mmsi
                break
        if matched is None:
            out.append({"rule": "dark_vessel", "det": d.id, "t": d.t, "lat": d.lat, "lon": d.lon})
    return out


def score(predicted_ids, labelled_ids):
    """Precision/recall against labelled history (the twin grading itself)."""
    p, l = set(predicted_ids), set(labelled_ids)
    tp = len(p & l)
    return {"tp": tp, "fp": len(p - l), "fn": len(l - p),
            "precision": tp / len(p) if p else 0.0, "recall": tp / len(l) if l else 0.0}
