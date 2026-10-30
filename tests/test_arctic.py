import json
import os
import tempfile
import unittest

from arctic.anomaly import ais_gaps, dark_vessels, speed_jumps
from arctic.eventlog import EventLog
from arctic.models import AISReport, SARDetection

T0 = 1_750_000_000


class TestArctic(unittest.TestCase):
    def test_gap_and_dark(self):
        ais = [AISReport("1", T0, 69, -100, 8, 270), AISReport("1", T0 + 8 * 3600, 69, -101, 8, 270)]
        self.assertEqual(len(ais_gaps(ais)), 1)
        sar = [SARDetection("x", T0, 69, -100), SARDetection("y", T0, 72, -90)]
        self.assertEqual([d["det"] for d in dark_vessels(sar, ais)], ["y"])

    def test_speed_jump(self):
        ais = [AISReport("1", T0, 69, -100, 8, 0), AISReport("1", T0 + 600, 70, -100, 8, 0)]
        self.assertEqual(len(speed_jumps(ais)), 1)

    def test_tamper_detected(self):
        p = os.path.join(tempfile.mkdtemp(), "e.jsonl")
        log = EventLog(p)
        log.append("a", {"x": 1})
        log.append("a", {"x": 2})
        self.assertTrue(log.verify())
        lines = open(p).read().splitlines()
        ev = json.loads(lines[0]); ev["payload"]["x"] = 99
        open(p, "w").write(json.dumps(ev, sort_keys=True) + "\n" + lines[1] + "\n")
        self.assertFalse(EventLog(p).verify())


if __name__ == "__main__":
    unittest.main()
