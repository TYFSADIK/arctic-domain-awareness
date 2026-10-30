from dataclasses import dataclass
import math


@dataclass
class AISReport:
    mmsi: str
    t: float      # unix seconds
    lat: float
    lon: float
    sog: float    # knots
    cog: float    # degrees


@dataclass
class SARDetection:
    id: str
    t: float
    lat: float
    lon: float
    length_m: float | None = None
    scene: str = ""   # Sentinel-1 product id


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def dead_reckon(r: AISReport, t: float):
    """Project an AIS position forward along course/speed (good enough for < 1 h)."""
    dist_km = r.sog * 1.852 * (t - r.t) / 3600.0
    br = math.radians(r.cog)
    dlat = dist_km * math.cos(br) / 111.32
    dlon = dist_km * math.sin(br) / (111.32 * max(math.cos(math.radians(r.lat)), 0.01))
    return r.lat + dlat, r.lon + dlon
