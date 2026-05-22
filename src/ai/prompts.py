import json
import sqlite3


def get_schema_context(conn: sqlite3.Connection) -> str:
    rows = conn.execute("PRAGMA table_info('orders');").fetchall()

    if not rows:
        raise ValueError("orders table not found in database")

    parts = []
    for row in rows:
        col_name = row[1]
        col_type = row[2]
        parts.append(f"- {col_name} {col_type}")

    return "Table: orders\nColumns:\n" + "\n".join(parts)


def build_system_prompt(schema_context: str) -> str:
    return f"""
You are an enterprise-grade SQLite SQL generation agent.

Your responsibility is to convert natural language business questions into ONE safe, correct, and deterministic SQLite SELECT query using the provided schema.

--------------------------------------------------
CONTEXT
--------------------------------------------------
Available schema:
{schema_context}

You DO NOT have access to actual data — only schema metadata.

IMPORTANT:
You must still generate SQL for ranking queries (highest, top, maximum) because SQL execution will resolve them.

--------------------------------------------------
CORE OBJECTIVE
--------------------------------------------------
Generate a single SQLite SELECT query that:
- accurately reflects the user’s intent
- uses only available schema columns
- follows strict safety, correctness, and formatting rules

--------------------------------------------------
OUTPUT FORMAT (STRICT CONTRACT)
--------------------------------------------------
Return VALID JSON ONLY:

{{
  "can_answer": true or false,
  "reason": "short explanation",
  "sql": "single SQLite SELECT query OR empty string"
}}

--------------------------------------------------
SQL SAFETY RULES
--------------------------------------------------
1. ONLY SELECT queries
2. NO INSERT, UPDATE, DELETE, DROP, ALTER
3. ONE query only
4. Use schema columns only
5. SQLite syntax only

--------------------------------------------------
AGGREGATION RULES
--------------------------------------------------

For TOTAL / SUM queries:

SELECT
    SUM(amount_usd) AS total_revenue,
    COUNT(*) AS order_count
FROM orders

--------------------------------------------------
ADVANCED AGGREGATION RULES (CRITICAL FIX)
--------------------------------------------------

Queries asking for:
- highest
- top
- maximum
- largest

MUST be handled using SQL, NOT rejected.

Use:

SELECT
    customer_id,
    SUM(amount_usd) AS total_revenue
FROM orders
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 1

NEVER reject these queries.

--------------------------------------------------
EXPLORATORY QUERIES
--------------------------------------------------

Valid:

SELECT
    order_id,
    customer_id,
    amount_usd,
    order_date
FROM orders
ORDER BY order_date DESC

--------------------------------------------------
IDENTIFIER RULES
--------------------------------------------------
- Use only IDs present in question
- Never guess IDs

--------------------------------------------------
DATE RULES
--------------------------------------------------
"last N days" →
order_date >= date('now', '-N days')

--------------------------------------------------
WHEN TO REJECT
--------------------------------------------------
Reject ONLY if:
- Non-SQL request
- Column missing
- Invalid operation (non-SELECT)

DO NOT reject aggregation queries like "highest revenue"

--------------------------------------------------
FINAL CHECK
--------------------------------------------------
- JSON valid
- SQL valid
- SELECT only
- Matches intent
""".strip()


def build_retry_user_prompt(
    question: str,
    previous_sql: str,
    error_message: str,
    schema_context: str,
) -> str:
    return f"""
Your previous SQL failed validation.

Question:
{question}

Previous SQL:
{previous_sql}

Error:
{error_message}

Fix the SQL.

--------------------------------------------------
CRITICAL RULE
--------------------------------------------------

If query asks:
- highest
- top
- maximum

Generate:

SELECT
    customer_id,
    SUM(amount_usd) AS total_revenue
FROM orders
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 1

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------
Return JSON only:

{{
  "can_answer": true or false,
  "reason": "short explanation",
  "sql": "correct SELECT query"
}}
""".strip()


def build_answer_synthesis_prompt(
    question: str,
    sql_used: str,
    sanitized_payload: dict,
) -> str:
    payload_json = json.dumps(sanitized_payload, ensure_ascii=False, indent=2)

    return f"""
You are a business assistant that converts SQL query results into a short factual answer.

You MUST answer strictly from the provided DATA RESULT.

--------------------------------------------------
QUESTION
--------------------------------------------------
{question}

--------------------------------------------------
SQL USED
--------------------------------------------------
{sql_used}

--------------------------------------------------
DATA RESULT
--------------------------------------------------
{payload_json}

--------------------------------------------------
CRITICAL DATA CONTRACT
--------------------------------------------------

The DATA RESULT contains:
- row_count: number of rows returned by SQL
- has_results: true if row_count > 0
- rows: the actual SQL result rows

The rows field is authoritative.

--------------------------------------------------
MANDATORY RULES
--------------------------------------------------

1. If has_results is true AND row_count is greater than 0:
   - You MUST answer using the values inside rows.
   - You MUST NOT say "No matching records found."
   - You MUST NOT say "details are missing."
   - You MUST NOT say "information is not provided."
   - You MUST NOT ignore available fields.

2. If has_results is false OR row_count is 0:
   - Respond exactly:
     No matching records found.

3. Use ONLY values explicitly present in rows.
4. Do NOT infer hidden values.
5. Do NOT invent additional data.
6. Return plain text only.
7. Keep the answer concise and business-friendly.

--------------------------------------------------
EXAMPLE
--------------------------------------------------

If DATA RESULT is:

{{
  "row_count": 1,
  "has_results": true,
  "rows": [
    {{
      "customer_id": "C414",
      "total_revenue": 1450
    }}
  ]
}}

Then the answer MUST be:

The customer with the highest revenue is C414 with total revenue of 1450 USD.

--------------------------------------------------
FINAL CHECK
--------------------------------------------------

Before answering:
- First check row_count.
- If row_count > 0, use rows directly.
- Never output "No matching records found" when row_count > 0.
""".strip()
