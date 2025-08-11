from pathlib import Path
from langchain_core.prompts import PromptTemplate
from agent.db.execute import run_select, explain
from agent.llm.client import make_llm
from agent.types import SchemaSnapshot, ValidateFixOutput
from agent.utils.utility import extract_json, render_schema_markdown
import sqlparse


def _pretty_sql(sql):
    try:
        return sqlparse.format(
            sql,
            reindent=True,
            keyword_case="upper",
            use_space_around_operators=True,
            comma_first=False,
        )
    except Exception:
        return sql


def validate_fix_node(sql_draft: str, schema: SchemaSnapshot, max_attempts: int = 3) -> ValidateFixOutput:
    try:
        _ = explain(sql_draft)
        _ = run_select(sql_draft, limit_default=3)
        return ValidateFixOutput(validated_sql=_pretty_sql(sql_draft), attempts=1, last_error=None)
    except Exception as e:
        last_err = str(e)

    llm = make_llm()
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "fix_sql.md"
    prompt = PromptTemplate.from_template(
        prompt_path.read_text(),
        template_format="jinja2",
    )
    schema_md = render_schema_markdown(schema, include_samples=True)

    attempts = 1
    candidate = sql_draft
    while attempts < max_attempts:
        attempts += 1
        msg = prompt.format(sql=candidate, error=last_err, schema_text=schema_md, attempts=attempts)
        resp = llm.invoke(msg)
        data = extract_json(getattr(resp, "content", resp))
        fixed = data.get("validated_sql") or data.get("sql") or candidate
        try:
            _ = explain(fixed)
            _ = run_select(fixed, limit_default=3)
            return ValidateFixOutput(validated_sql=_pretty_sql(fixed), attempts=attempts, last_error=None)
        except Exception as e:
            last_err = str(e)
            candidate = fixed

    return ValidateFixOutput(validated_sql=None, attempts=attempts, last_error=last_err)
