from pathlib import Path
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from agent.llm.client import make_llm
import json


def respond_node(
    *,
    now_iso: str,
    timezone: str,
    original_question: str,
    rephrased_question: str,
    final_sql: str,
    result_rows: List[Dict[str, Any]],
    rowcount: int,
    previous_turns_minimal: List[dict],
) -> str:
    llm = make_llm(temperature=0.3)
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "respond.md"
    prompt = PromptTemplate.from_template(prompt_path.read_text(), template_format="jinja2")

    preview_len = min(len(result_rows), 20)
    preview = result_rows[:preview_len]

    msg = prompt.format(
        now_iso=now_iso,
        timezone=timezone,
        original_question=original_question,
        rephrased_question=rephrased_question,
        final_sql=final_sql,
        rowcount=rowcount,
        preview_len=preview_len,
        result_preview_json=json.dumps(preview, ensure_ascii=False, default=str),
        history_json=json.dumps(previous_turns_minimal[-10:], ensure_ascii=False),
    )
    resp = llm.invoke(msg)
    return getattr(resp, "content", str(resp))
