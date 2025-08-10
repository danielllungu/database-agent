from agent.db.execute import run_select
from agent.types import ExecutionResult

def run_query_node(final_sql: str) -> ExecutionResult:
    rows = run_select(final_sql)
    return ExecutionResult(final_sql=final_sql, rows=rows, rowcount=len(rows))
