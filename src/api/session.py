import uuid
from typing import Dict, Any

_sessions: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(sid):
    if sid and sid in _sessions:
        return sid
    new_id = uuid.uuid4().hex
    _sessions[new_id] = {"previous_turns": []}
    return new_id

def read(sid: str) -> Dict[str, Any]:
    return _sessions.setdefault(sid, {"previous_turns": []})

def reset(sid: str) -> None:
    _sessions[sid] = {"previous_turns": []}