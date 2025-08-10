import json, os, time
from agent.types import SchemaSnapshot
from agent.db.introspect import load_schema_snapshot

CACHE_FILE = ".schema_snapshot.json"
TTL_SECONDS = 300

def get_schema_snapshot() -> SchemaSnapshot:
    if os.path.exists(CACHE_FILE):
        mtime = os.path.getmtime(CACHE_FILE)
        if (time.time() - mtime) < TTL_SECONDS:
            with open(CACHE_FILE, "r") as f:
                return SchemaSnapshot.model_validate(json.load(f))
    snap = load_schema_snapshot()
    with open(CACHE_FILE, "w") as f:
        json.dump(snap.model_dump(), f, indent=2, default=str)
    return snap
