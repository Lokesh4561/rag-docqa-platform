# Medallion Architecture

The medallion architecture organises a lakehouse into three layers: bronze, silver and gold.

The bronze layer stores raw data exactly as it arrives from source systems. Nothing is cleaned or removed, which means the original records can always be replayed if a downstream bug is found.

The silver layer contains cleaned, validated and deduplicated data. Types are standardised, invalid rows are filtered or quarantined, and records from different sources are joined into consistent entities such as customers or orders.

The gold layer holds business-level aggregates and dimensional models that are ready for reporting, dashboards and machine learning features. Gold tables are usually modelled as star schemas with fact and dimension tables.

Moving data step by step through these layers makes pipelines easier to debug, because each layer can be inspected and tested on its own.
