from pathlib import Path
from langchain_core.prompts import PromptTemplate
from agent.llm.client import make_llm
from agent.types import PlanSQLOutput
from agent.utils.utility import extract_json, render_schema_markdown


def plan_sql_node(original_q, rephrased_q, schema):
    llm = make_llm()
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "plan_sql.md"
    prompt = PromptTemplate.from_template(
        prompt_path.read_text(),
        template_format="jinja2",
    )
    schema_md = render_schema_markdown(schema, include_samples=True)
    msg = prompt.format(
        user_query=original_q,
        rephrased_query=rephrased_q,
        schema_text=schema_md,
    )
    resp = llm.invoke(msg)
    data = extract_json(getattr(resp, "content", resp))
    return PlanSQLOutput(**data)
