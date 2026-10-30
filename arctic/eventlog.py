"""Append-only event log: the backbone. Every ingest and every anomaly is an event.

Each line is JSON with a sequence number and the hash of the previous line, so
replay is deterministic and silent edits are detectable.
"""
import hashlib
import json
import os


class EventLog:
    def __init__(self, path):
        self.path = path
        self.seq, self.prev = 0, "0" * 64
        if os.path.exists(path):
            for ev in self.read():
                self.seq, self.prev = ev["seq"], ev["hash"]

    def append(self, kind: str, payload: dict) -> dict:
        self.seq += 1
        body = {"seq": self.seq, "kind": kind, "payload": payload, "prev": self.prev}
        body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        with open(self.path, "a") as fh:
            fh.write(json.dumps(body, sort_keys=True) + "\n")
        self.prev = body["hash"]
        return body

    def read(self, kind=None):
        if not os.path.exists(self.path):
            return
        with open(self.path) as fh:
            for line in fh:
                ev = json.loads(line)
                if kind is None or ev["kind"] == kind:
                    yield ev

    def verify(self) -> bool:
        prev = "0" * 64
        for ev in self.read():
            h = ev.pop("hash")
            if ev["prev"] != prev or hashlib.sha256(json.dumps(ev, sort_keys=True).encode()).hexdigest() != h:
                return False
            prev = h
        return True
