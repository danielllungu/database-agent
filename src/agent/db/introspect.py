from typing import Dict
from psycopg2.extras import RealDictCursor
from agent.config import settings
from agent.db.connection import get_conn
from agent.types import SchemaSnapshot, Table, Column, ForeignKey


def load_schema_snapshot() -> SchemaSnapshot:
    schema = settings.db_schema
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.table_name, c.column_name, c.is_nullable, c.data_type, c.column_default
            FROM information_schema.columns c
            WHERE c.table_schema = %s
            ORDER BY c.table_name, c.ordinal_position
        """, (schema,))
        cols = list(cur.fetchall())

        cur.execute("""
            SELECT tc.table_name, kcu.column_name, ccu.table_name AS ref_table, ccu.column_name AS ref_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.table_schema = %s AND tc.constraint_type = 'FOREIGN KEY'
        """, (schema,))
        fks = list(cur.fetchall())

        cur.execute("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.table_schema = %s AND tc.constraint_type = 'PRIMARY KEY'
        """, (schema,))
        pks = list(cur.fetchall())

        tables: Dict[str, Table] = {}
        for r in cols:
            t = r["table_name"]
            tables.setdefault(t, Table(
                name=t, columns=[], primary_key=[], foreign_keys=[], sample_rows=[]
            ))
            tables[t].columns.append(Column(
                name=r["column_name"],
                data_type=r["data_type"],
                nullable=(r["is_nullable"] == "YES"),
                default=r["column_default"],
            ))

        for r in pks:
            t = r["table_name"]
            if t in tables:
                tables[t].primary_key.append(r["column_name"])

        for r in fks:
            t = r["table_name"]
            if t in tables:
                tables[t].foreign_keys.append(ForeignKey(
                    table=t, column=r["column_name"], ref_table=r["ref_table"], ref_column=r["ref_column"]
                ))

        for t in tables.keys():
            cur.execute(f'SELECT * FROM "{schema}"."{t}" LIMIT 3;')
            rows = [dict(x) for x in cur.fetchall()]
            tables[t].sample_rows = rows

        return SchemaSnapshot(schema_name=schema, tables=tables)

