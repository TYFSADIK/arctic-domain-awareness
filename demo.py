"""Run: python demo.py  -> synthetic Northwest Passage day with one gap and one dark vessel."""
import os
import tempfile
from dataclasses import asdict

from arctic.anomaly import ais_gaps, dark_vessels, score, speed_jumps
from arctic.eventlog import EventLog
from arctic.models import AISReport, SARDetection

T0 = 1_750_000_000
ais = [
    AISReport("316000001", T0, 68.9, -105.0, 10, 90),
    AISReport("316000001", T0 + 3600, 68.9, -104.6, 10, 90),
    AISReport("316000002", T0, 69.1, -100.0, 8, 270),
    AISReport("316000002", T0 + 9 * 3600, 69.1, -101.2, 8, 270),   # 9 h silence
]
sar = [
    SARDetection("S1-001", T0 + 3600, 68.9, -104.6),   # matches 316000001
    SARDetection("S1-002", T0 + 3600, 70.2, -98.5),    # nothing nearby -> dark
]

log = EventLog(os.path.join(tempfile.mkdtemp(), "events.jsonl"))
for r in ais:
    log.append("ais", asdict(r))
for d in sar:
    log.append("sar", asdict(d))
anoms = ais_gaps(ais) + speed_jumps(ais) + dark_vessels(sar, ais)
for a in anoms:
    log.append("anomaly", a)
    print(a)
print("log intact:", log.verify())
print("score:", score([a["det"] for a in anoms if a["rule"] == "dark_vessel"], ["S1-002"]))
