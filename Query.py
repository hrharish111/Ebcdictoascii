import snowflake.connector

# === CONFIGURATION ===
TABLE1 = 'table1'
TABLE2 = 'table2'
OUTPUT_TABLE = 'mismatched_rows'

conn = snowflake.connector.connect(
    user='YOUR_USER',
    password='YOUR_PASSWORD',
    account='YOUR_ACCOUNT',
    warehouse='YOUR_WAREHOUSE',
    database='YOUR_DATABASE',
    schema='YOUR_SCHEMA'
)

cs = conn.cursor()
try:
    # Step 1: Get column names from TABLE1
    cs.execute(f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{TABLE1.upper()}'
        AND TABLE_SCHEMA = CURRENT_SCHEMA()
        ORDER BY ORDINAL_POSITION
    """)
    columns = [row[0] for row in cs.fetchall()]

    # Step 2: Generate SQL components
    coalesce_exprs = ',\n    '.join([
        f"COALESCE(t1.{col}, t2.{col}) AS {col}" for col in columns
    ])
    mismatch_conditions = ' OR\n    '.join([
        f"t1.{col} IS DISTINCT FROM t2.{col}" for col in columns
    ])
    differing_expr = "CONCAT_WS(', ',\n    " + ',\n    '.join([
        f"CASE WHEN t1.{col} IS DISTINCT FROM t2.{col} THEN '{col}' END" for col in columns
    ]) + "\n) AS differing_columns"

    # Step 3: Final SQL
    sql = f"""
CREATE OR REPLACE TABLE {OUTPUT_TABLE} AS
WITH t1 AS (
    SELECT *, ROW_NUMBER() OVER () AS rn FROM {TABLE1}
),
t2 AS (
    SELECT *, ROW_NUMBER() OVER () AS rn FROM {TABLE2}
),
joined AS (
    SELECT
        {coalesce_exprs},
        CASE
            WHEN t1.rn IS NULL THEN 'table2_only'
            WHEN t2.rn IS NULL THEN 'table1_only'
            WHEN {mismatch_conditions} THEN 'column_mismatch'
        END AS mismatch,
        {differing_expr}
    FROM t1
    FULL OUTER JOIN t2 ON t1.rn = t2.rn
)
SELECT * FROM joined
WHERE mismatch IS NOT NULL;
"""
    print("Generated SQL:\n", sql)  # optional for debug
    cs.execute(sql)
    print(f"✅ Mismatched rows written to '{OUTPUT_TABLE}'")

finally:
    cs.close()
    conn.close()
