# Arctic Domain Awareness

Private research repo. A streaming pipeline that fuses ADS-B aircraft data, AIS ship tracking, and Sentinel-1 radar imagery over Canada's North, with anomaly detection for dark vessels.

Full write-up: [`docs/project-page.md`](docs/project-page.md)

## What's here

| File | Purpose |
|---|---|
| `arctic/eventlog.py` | Append-only, hash-chained JSONL event log with replay and `verify()` |
| `arctic/models.py` | AIS and SAR record types, haversine distance, dead-reckoning |
| `arctic/ingest.py` | Parsers for AIS CSV, SAR detection CSV, and dump1090/readsb `aircraft.json` |
| `arctic/anomaly.py` | AIS gap, speed-jump (spoofing), and dark-vessel rules, plus precision/recall scoring against labels |

## Quickstart

```bash
python demo.py
python -m unittest -v
```

## Next steps
- [ ] Pull Sentinel-1 GRD scenes for a fixed AOI (e.g. Lancaster Sound) from ASF and run ship detection
- [ ] Feed AIS from your own RTL-SDR receiver (see the water-acoustic repo) or an AIS Hub export
- [ ] Build a labelled history set (known dark events) and track precision and recall per rule over time
- [ ] Stream with NATS or Kafka and keep the JSONL log as the replayable source of truth
- [ ] Map view: anomalies as GeoJSON, opened in QGIS or Leaflet

Uses only public, open data.
