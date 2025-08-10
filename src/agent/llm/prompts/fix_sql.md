You are fixing a Postgres SQL query that had error.

SQL:
{{ sql }}
Error:
{{ error }}

Schema (markdown):
{{ schema_text }}

Task:
- Identify the cause.
- Produce a corrected SELECT query that will run.
- If you change table/column names, explain briefly.

Return JSON ONLY (no backticks, no extra text):
{
  "validated_sql": "SELECT ...",
  "attempts": {{ attempts }},
  "last_error": "{{ error | replace('\n',' ') }}"
}