WITH all_data AS (
  SELECT TASK_NAME, TO_VARIANT(*) AS full_row, * EXCLUDE (TASK_NAME) AS original_data, 'table1' AS source_table FROM table1
  UNION ALL
  SELECT TASK_NAME, TO_VARIANT(*) AS full_row, * EXCLUDE (TASK_NAME) AS original_data, 'table2' AS source_table FROM table2
),
deduplicated AS (
  SELECT DISTINCT TASK_NAME, full_row, source_table, original_data FROM all_data
),
unmatched_rows AS (
  SELECT TASK_NAME, full_row
  FROM deduplicated
  GROUP BY TASK_NAME, full_row
  HAVING COUNT(*) = 1 -- present in only one table
),
joined AS (
  SELECT d.TASK_NAME, a.source_table, a.original_data
  FROM unmatched_rows d
  JOIN deduplicated a
    ON d.TASK_NAME = a.TASK_NAME AND d.full_row = a.full_row
),
with_row_num AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY TASK_NAME, source_table ORDER BY TASK_NAME) AS rn
  FROM joined
),
agg_counts AS (
  SELECT TASK_NAME, source_table, COUNT(*) AS mismatch_count
  FROM joined
  GROUP BY TASK_NAME, source_table
)
SELECT c.TASK_NAME, c.source_table, c.mismatch_count,
       s.original_data AS sample_row
FROM agg_counts c
JOIN with_row_num s
  ON c.TASK_NAME = s.TASK_NAME AND c.source_table = s.source_table
WHERE s.rn = 1
ORDER BY c.mismatch_count DESC;
