# Portfolio roadmap

| # | Project | Closes gaps for | Status |
|---|---|---|---|
| 1 | **DocQA: RAG platform** (this repo) | AI Engineer, GenAI Data Scientist, Target, Ford | 🚧 in progress |
| 2 | **Real-time CDC lakehouse** (upgrade of `kafka-stock-market-project`) | Trading data, IBM AWS, dbt + Iceberg roles | ⏳ next |
| 3 | **PII de-identification + synthetic data toolkit** | AI training-data roles (Handshake-type) | ⏳ later |

---

## Project 2: Upgrade `kafka-stock-market-project` into a CDC lakehouse

You already have a working Kafka producer and consumer. Upgrading it is faster than starting over, and it shows growth in your commit history.

**Phase A: Fix what's there (1 day)**
- [ ] Fix the README's screenshot paths: move the PNGs into `screenshots/` or update the links.
- [ ] Rename the ticker `GOOGLE` → `GOOGL`.
- [ ] Add setup and run instructions, plus a `docker-compose.yml` that starts Kafka (KRaft mode, no Zookeeper) so anyone can run it with one command.
- [ ] Add a LICENSE, `.gitignore` and pytest tests for the message format.

**Phase B: Make it a real pipeline (1 week)**
- [ ] Add a **schema** for each message (Pydantic or Avro) and reject or quarantine bad messages into a dead-letter topic.
- [ ] Land the data in **S3 as Apache Iceberg** tables (Spark Structured Streaming or PyIceberg), partitioned by date.
- [ ] Use **MERGE on (symbol, event_time)** so replaying messages never creates duplicates. Then prove it: write a test that replays the same 10,000 messages twice and checks the row count.
- [ ] Commit Kafka offsets only **after** a successful write (at-least-once delivery plus an idempotent sink = effectively exactly-once).

**Phase C: CDC + modelling (1 week)**
- [ ] Add a PostgreSQL "trades" database, and stream its changes with **Debezium → Kafka** (or AWS DMS if you use AWS).
- [ ] Build **dbt** models: staging → `fct_trades`, `dim_symbol`, plus daily OHLC aggregates. Add dbt tests.
- [ ] Query with **Athena** (or DuckDB locally).

**Phase D: Operate it (3–4 days)**
- [ ] Orchestrate with **Airflow** (docker compose).
- [ ] Add a daily **reconciliation** check (source rows vs. lake rows) that alerts on mismatch.
- [ ] Load-test an "end-of-day burst" of 1M messages and document throughput.
- [ ] Add a **GitHub Actions** CI workflow and an architecture diagram (draw.io or Excalidraw).

**Resume bullet:** *Built a real-time CDC lakehouse (Kafka, Debezium, Apache Iceberg on S3, dbt, Airflow) with idempotent MERGE ingestion, dead-letter handling and automated reconciliation, sustaining X msgs/sec under end-of-day peak load.*

---

## Project 3: PII de-identification and synthetic data toolkit

**Steps**
1. [ ] Generate a linked relational dataset (customers → orders → support_tickets) with **Faker**, planting known PII.
2. [ ] Detect PII in columns and free text with **Microsoft Presidio**, plus an LLM pass for anything it misses.
3. [ ] Replace identifiers with **consistent pseudonyms** (salted HMAC), so joins still work across tables. Write a test proving every foreign key still matches after anonymization.
4. [ ] Generate **synthetic support tickets** with an LLM, and synthetic tabular data with **SDV**.
5. [ ] Evaluate:
   - **PII recall:** what percentage of planted PII was caught?
   - **Utility:** do distributions and correlations stay close to the original?
   - **Privacy:** run a simple linkage or re-identification attack and report the success rate.
6. [ ] Package it as a CLI (`deid run --config config.yaml`) and publish it on GitHub with docs.

**Resume bullet:** *Built a reusable PII de-identification and synthetic-data toolkit (Presidio, LLMs, SDV) that preserves referential integrity across tables, with automated PII-recall, utility and re-identification-risk evaluations.*
