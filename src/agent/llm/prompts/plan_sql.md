You write a first SQL draft for Postgres based on the schema.

Original: {{ user_query }}
Rephrased: {{ rephrased_query }}

Schema (markdown, tables, columns, PKs, FKs, samples):
{{ schema_text }}

Rules:
- Use only tables/columns that exist.
- Prefer explicit joins using foreign keys.
- SELECT only.
- Include clear column aliases.
- If date filters are needed, use TIMESTAMPTZ appropriately.

Return JSON ONLY (no backticks, no extra text):
{
  "sql_draft": "SELECT ...",
  "target_tables": ["table1", "table2"],
  "assumptions": "concise notes"
}