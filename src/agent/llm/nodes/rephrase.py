from pathlib import Path
from langchain_core.prompts import PromptTemplate
from agent.llm.client import make_llm
from agent.types import QueryContext, RephraseOutput
from agent.utils.utility import extract_json
import json


def rephrase_node(ctx: QueryContext) -> RephraseOutput:
    llm = make_llm()
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "rephrase.md"
    prompt = PromptTemplate.from_template(
        prompt_path.read_text(),
        template_format="jinja2",
    )
    minimal_turns = [
        {
            "original_question": t.original_question,
            "rephrased_question": t.rephrased_question,
            "final_sql": t.final_sql,
            "rowcount": t.rowcount,
            "timestamp_iso": t.timestamp_iso,
        } for t in ctx.previous_turns[-10:]
    ]
    msg = prompt.format(
        now_iso=ctx.now_iso,
        timezone=ctx.timezone,
        user_query=ctx.user_query,
        history_json=json.dumps(minimal_turns, ensure_ascii=False, indent=2),
    )
    resp = llm.invoke(msg)
    data = extract_json(getattr(resp, "content", resp))

    return RephraseOutput(**data)
