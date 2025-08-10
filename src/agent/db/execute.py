from psycopg2.extras import RealDictCursor
from agent.db.connection import get_conn

READONLY_GUARD = "SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY;"

def run_select(sql, params = None, limit_default = 100):
    if "select" not in sql.lower():
        raise ValueError("Only SELECT statements are allowed.")
    if "limit" not in sql.lower():
        sql = f"{sql.rstrip(';')} LIMIT {limit_default};"
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(READONLY_GUARD)
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return [dict(r) for r in rows]

def explain(sql: str) -> str:
    if "select" not in sql.lower():
        raise ValueError("Only SELECT explain supported.")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(READONLY_GUARD)
        cur.execute(f"EXPLAIN {sql}")
        plan = "\n".join(r[0] for r in cur.fetchall())
        return plan
