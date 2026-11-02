"""Download plain-text Wikipedia articles into data/raw/wiki/ to build a realistic dataset.

Run from the project folder:  python -m scripts.download_wikipedia
Uses only the Python standard library. Respects Wikipedia's API etiquette (User-Agent + small delay).
"""

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

TOPICS = [
    # Data engineering
    "Data engineering", "Extract, transform, load", "Data warehouse", "Data lake", "Data lakehouse",
    "Data mart", "Star schema", "Snowflake schema", "Dimensional modeling", "Data vault modeling",
    "Online analytical processing", "Online transaction processing", "Change data capture",
    "Slowly changing dimension", "Data pipeline", "Data integration", "Data quality", "Data governance",
    "Master data management", "Metadata", "Data lineage", "Data mesh", "Idempotence", "Data validation",
    "Batch processing", "Stream processing", "Event-driven architecture", "Message queue",
    # Databases and storage
    "Relational database", "SQL", "NoSQL", "PostgreSQL", "Column-oriented DBMS", "ACID",
    "Database normalization", "Database index", "Two-phase commit protocol", "CAP theorem",
    "Eventual consistency", "Apache Parquet", "Object storage", "Amazon S3",
    # Big data tools
    "Apache Spark", "Apache Kafka", "Apache Hadoop", "Apache Hive", "Apache Flink", "Apache Airflow",
    "Apache Iceberg", "Delta Lake", "Databricks", "Snowflake Inc.", "Amazon Redshift", "BigQuery",
    "MapReduce", "Distributed computing",
    # Cloud and DevOps
    "Cloud computing", "Amazon Web Services", "Microsoft Azure", "Google Cloud Platform",
    "Serverless computing", "Infrastructure as code", "Terraform (software)", "Docker (software)",
    "Kubernetes", "Continuous integration", "Continuous delivery", "DevOps", "Git", "Microservices",
    # AI and ML
    "Machine learning", "Deep learning", "Large language model", "Retrieval-augmented generation",
    "Word embedding", "Vector database", "Transformer (deep learning architecture)",
    "Natural language processing", "Prompt engineering", "Fine-tuning (deep learning)",
    "Hallucination (artificial intelligence)", "MLOps", "Feature engineering", "Cosine similarity",
    "Nearest neighbor search", "Synthetic data", "Data anonymization", "Personal data",
]

API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "rag-docqa-platform/0.1 (portfolio project; https://github.com/Lokesh4561/rag-docqa-platform)"}
OUT_DIR = Path("data/raw/wiki")


def fetch(title: str) -> tuple[str | None, str]:
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": title,
        "format": "json",
        "formatversion": 2,
    }
    req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    page = data["query"]["pages"][0]
    if page.get("missing"):
        return None, ""
    return page["title"], page.get("extract", "")


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    for topic in TOPICS:
        try:
            title, text = fetch(topic)
        except Exception as exc:  # network hiccup: skip and continue
            print(f"failed   {topic}: {exc}")
            continue
        if not title or len(text) < 500:
            print(f"skipped  {topic} (not found or too short)")
            continue
        (OUT_DIR / f"{slugify(title)}.txt").write_text(f"{title}\n\n{text}", encoding="utf-8")
        saved += 1
        print(f"saved    {title} ({len(text):,} chars)")
        time.sleep(0.5)
    print(f"\nDone: {saved} articles saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
