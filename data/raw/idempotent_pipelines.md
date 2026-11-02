# Idempotent Data Pipelines

A pipeline is idempotent when running it twice with the same input produces the same result as running it once. This matters because real pipelines fail halfway and get retried, and a retry must never create duplicate rows or double-count values.

A common technique is to write with a MERGE (upsert) statement keyed on a natural or business key. If a row with that key already exists it is updated; otherwise it is inserted. Rerunning the same batch therefore leaves the table unchanged.

Other techniques include overwriting a whole partition for a given date, tracking processed batch IDs in a control table, and using content hashes to skip files that have not changed.

Idempotency should be proven with tests: kill a job midway, rerun it, and check that row counts and totals still match the source.
