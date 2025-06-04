WITH 
table1_hashed AS (
    SELECT 
        HASH(OBJECT_CONSTRUCT(*)) AS row_hash,
        OBJECT_CONSTRUCT(*) AS row_data
    FROM table1
),
table2_hashed AS (
    SELECT 
        HASH(OBJECT_CONSTRUCT(*)) AS row_hash,
        OBJECT_CONSTRUCT(*) AS row_data
    FROM table2
),
table1_counts AS (
    SELECT 
        row_hash, 
        COUNT(*) AS cnt_table1, 
        ANY_VALUE(row_data) AS sample_row
    FROM table1_hashed
    GROUP BY row_hash
),
table2_counts AS (
    SELECT 
        row_hash, 
        COUNT(*) AS cnt_table2, 
        ANY_VALUE(row_data) AS sample_row
    FROM table2_hashed
    GROUP BY row_hash
),
combined_counts AS (
    SELECT 
        COALESCE(t1.row_hash, t2.row_hash) AS row_hash,
        COALESCE(t1.cnt_table1, 0) AS cnt_table1,
        COALESCE(t2.cnt_table2, 0) AS cnt_table2,
        COALESCE(t1.sample_row, t2.sample_row) AS sample_row
    FROM table1_counts t1
    FULL OUTER JOIN table2_counts t2 
        ON t1.row_hash = t2.row_hash
    WHERE 
        COALESCE(t1.cnt_table1, 0) != COALESCE(t2.cnt_table2, 0)
)
SELECT 
    row_hash,
    cnt_table1,
    cnt_table2,
    cnt_table1 - cnt_table2 AS diff_count,
    sample_row
FROM combined_counts;
