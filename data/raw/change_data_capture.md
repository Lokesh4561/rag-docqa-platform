# Change Data Capture (CDC)

Change data capture is a way to stream every insert, update and delete from a source database to downstream systems, instead of copying whole tables on a schedule.

Log-based CDC reads changes directly from the database transaction log, such as the PostgreSQL write-ahead log or the MySQL binlog. Because it reads the log rather than querying tables, it adds very little load to the source and captures every change in commit order.

Tools such as Debezium publish these change events to Apache Kafka. AWS DMS can also capture ongoing changes and deliver them to targets like Kinesis or S3.

Downstream, the events are applied to a target table with MERGE logic, and ordering must be preserved per key so that an older update never overwrites a newer one.
