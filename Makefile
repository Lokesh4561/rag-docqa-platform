.PHONY: setup db-up db-down init ingest api eval test lint

setup:      ## create virtualenv and install dependencies
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt

db-up:      ## start Postgres + pgvector
	docker compose up -d

db-down:
	docker compose down

init:       ## create tables
	python -m app.db

ingest:     ## load documents from data/raw
	python -m app.ingest

api:        ## run the API with auto-reload
	uvicorn app.api:app --reload

eval:       ## measure retrieval quality
	python -m eval.run_eval

test:
	pytest -q

lint:
	ruff check .
