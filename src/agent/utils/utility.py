from datetime import datetime
import pytz
import json
import re
from typing import Iterable, Optional
from agent.types import SchemaSnapshot, Table


def _fmt_table_line(t, include_samples, preview_rows):
    cols = []
    for c in t.columns:
        marks = []
        if c.name in t.primary_key: marks.append("PK")
        if any(fk.column == c.name for fk in t.foreign_keys): marks.append("FK")
        suffix = f" ({','.join(marks)})" if marks else ""
        nn = "" if c.nullable else " NOT NULL"
        cols.append(f"- {c.name}: {c.data_type}{nn}{suffix}")
    fk_lines = [
        f"- {fk.column} → {fk.ref_table}.{fk.ref_column}"
        for fk in t.foreign_keys
    ]

    lines = []
    lines.append(f"### {t.name}")
    lines.append("**Columns**")
    lines.extend(cols)
    if fk_lines:
        lines.append("**Foreign Keys**")
        lines.extend(fk_lines)
    if include_samples and t.sample_rows:
        lines.append(f"**Samples (up to {min(preview_rows,len(t.sample_rows))})**")
        headers = list(t.sample_rows[0].keys())
        lines.append(", ".join(headers))
        for row in t.sample_rows[:preview_rows]:
            vals = [str(row.get(h, "")) for h in headers]
            lines.append(", ".join(vals))
    lines.append("")
    return "\n".join(lines)

def render_schema_markdown(
    snapshot,
    tables = None,
    include_samples = False,
    preview_rows = 2,
):
    names = set(tables) if tables else set(snapshot.tables.keys())
    ordered = [snapshot.tables[n] for n in sorted(names) if n in snapshot.tables]
    parts = [f"## Schema: {snapshot.schema_name}", ""]
    for t in ordered:
        parts.append(_fmt_table_line(t, include_samples=include_samples, preview_rows=preview_rows))
    return "\n".join(parts)


def now_iso_tz(tz: str) -> str:
    return datetime.now(pytz.timezone(tz)).isoformat()


def extract_json(text):
    if not isinstance(text, str):
        text = str(text or "")

    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fence:
        candidate = fence.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError("Could not extract valid JSON from LLM output.")
