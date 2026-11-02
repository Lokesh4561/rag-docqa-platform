# DocQA: Production RAG Platform

> Ask questions about your documents and get cited answers. Built end to end: ingestion pipeline → vector search → LLM API → React UI → Docker → GCP Cloud Run with Terraform and CI/CD.

![CI](https://github.com/Lokesh4561/rag-docqa-platform/actions/workflows/ci.yml/badge.svg)

## Architecture

```
 data/raw (PDF, TXT, MD)
        │
        ▼
 ┌──────────────────┐   clean → chunk → embed    ┌──────────────────────┐
 │ Ingestion (Python)│ ─────────────────────────▶ │ Postgres + pgvector  │
 └──────────────────┘   idempotent (content hash) │ documents / chunks   │
                                                  └──────────┬───────────┘
                                                             │ cosine similarity
 ┌──────────────┐   POST /ask    ┌──────────────────┐        │
 │ React (Vite) │ ─────────────▶ │ FastAPI          │ ◀──────┘
 └──────────────┘ ◀───────────── │ /search  /ask    │ ──────▶ LLM (Ollama / Groq / Gemini)
                 answer + sources└──────────────────┘
                                   Docker → Cloud Run (Terraform, GitHub Actions)
```

## Tech stack

| Layer | Tools |
|---|---|
| Ingestion | Python, pypdf, content-hash idempotency |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2, runs locally, free) |
| Vector store | PostgreSQL + pgvector (HNSW index) |
| LLM | Any OpenAI-compatible API: Ollama (local), Groq or Gemini (free tiers) |
| API | FastAPI, Pydantic |
| Frontend | React + Vite |
| Evaluation | hit@k and MRR retrieval metrics |
| DevOps | Docker, Terraform, GCP Cloud Run, Artifact Registry, GitHub Actions |

## Results

| Config | hit@5 | MRR |
|---|---|---|
| chunk 800 / overlap 150 | _fill in_ | _fill in_ |
| chunk 400 / overlap 80 | _fill in_ | _fill in_ |

*(Fill this table in during Phase 4. Real numbers make the project stand out.)*

---

# Step-by-step build guide

Work through the phases in order. **Commit after every step** using the suggested commit message. A steady commit history shows reviewers how you built it.

Tick the boxes as you go: `- [x]`.

## Phase 0: Set up your machine (about 1 hour)

- [ ] **0.1 Install the tools**
  - Python 3.11+ → <https://www.python.org/downloads/>
  - Docker Desktop → <https://www.docker.com/products/docker-desktop/>
  - Git → <https://git-scm.com/downloads>
  - Node.js 20 LTS (for the frontend) → <https://nodejs.org/>
  - VS Code (recommended) → <https://code.visualstudio.com/>
- [ ] **0.2 Pick your LLM** (one is enough):
  - **Free and local:** install Ollama from <https://ollama.com>, then run `ollama pull llama3.2`
  - **Free cloud:** get a Groq key at <https://console.groq.com> or a Gemini key at <https://aistudio.google.com>
- [ ] **0.3 Create the GitHub repo**
  1. On GitHub, click **New repository**. Name it `rag-docqa-platform`, make it **Public**, and don't add a README (this folder already has one).
  2. In a terminal inside this folder:
     ```bash
     git init
     git add .
     git commit -m "chore: project scaffold"
     git branch -M main
     git remote add origin https://github.com/Lokesh4561/rag-docqa-platform.git
     git push -u origin main
     ```
  3. Open the **Actions** tab on GitHub. The CI workflow should run and pass ✅.

## Phase 1: Local environment and database (about 1 hour)

- [ ] **1.1 Create a virtual environment and install packages**
  ```bash
  python -m venv .venv
  # Windows:    .venv\Scripts\activate
  # Mac/Linux:  source .venv/bin/activate
  pip install -r requirements-dev.txt
  ```
- [ ] **1.2 Create your `.env`**
  ```bash
  cp .env.example .env      # Windows: copy .env.example .env
  ```
  Edit `.env` to match the LLM option you chose in step 0.2.
- [ ] **1.3 Start Postgres with pgvector**
  ```bash
  docker compose up -d
  docker ps                 # docqa-db should be "healthy"
  ```
- [ ] **1.4 Create the tables**
  ```bash
  python -m app.db          # prints "Database initialised."
  ```
- [ ] **1.5 Run the tests**
  ```bash
  pytest -q
  ruff check .
  ```
  📝 Commit: `chore: local dev environment with pgvector`

**What you learn:** Docker, pgvector, environment configuration.

## Phase 2: Ingestion pipeline (about 2–3 hours)

- [ ] **2.1 Read the code** in this order: `app/chunking.py` → `app/embeddings.py` → `app/ingest.py`. Make sure you can explain every function in an interview.
- [ ] **2.2 Run ingestion on the sample docs**
  ```bash
  python -m app.ingest
  ```
  The first run downloads the embedding model (about 90 MB).
- [ ] **2.3 Prove it is idempotent.** Run `python -m app.ingest` again. Every file should say `skipped (unchanged)`. Edit one file and run it again: only that file is re-ingested.
- [ ] **2.4 Look inside the database**
  ```bash
  docker exec -it docqa-db psql -U rag -c "SELECT d.title, count(*) FROM chunks c JOIN documents d ON d.id = c.document_id GROUP BY 1;"
  ```
- [ ] **2.5 Add a real dataset** of 200–1,000 documents to `data/raw/`. Good free options:
  - Your own PDFs (study notes, certification guides)
  - Company annual reports (download PDFs from investor-relations pages)
  - Wikipedia articles saved as `.txt`

  Note: large datasets are git-ignored only if you add them to `.gitignore`. Keep the repo small and explain in the README where the data comes from.
- [ ] **2.6 Your own improvement:** add a `--rebuild` flag that deletes all rows and re-ingests everything.

  📝 Commit: `feat: idempotent ingestion pipeline with pgvector`

**What you learn:** chunking strategy, embeddings, vector indexes (HNSW), idempotency. These are the exact topics in AI and data engineer JDs.

## Phase 3: API (about 2 hours)

- [ ] **3.1 Start the API**
  ```bash
  uvicorn app.api:app --reload
  ```
- [ ] **3.2 Try it** at <http://localhost:8000/docs>:
  - `POST /search` with `{"question": "What is change data capture?"}`
  - `POST /ask` with the same body. You should get an answer with `[1]`-style citations.
- [ ] **3.3 Your own improvements** (pick at least one):
  - Add a `POST /ingest` endpoint that accepts a file upload
  - Add request logging with response time
  - Write `tests/test_api.py` using FastAPI's `TestClient`, mocking `search` and `generate_answer`

  📝 Commit: `feat: FastAPI search and ask endpoints`

## Phase 4: Evaluation (about 2 hours) ⭐ the part most portfolios skip

- [ ] **4.1 Run the baseline**
  ```bash
  python -m eval.run_eval
  ```
- [ ] **4.2 Write 30–50 questions** about YOUR dataset in `eval/questions.jsonl`, using the same format as the examples.
- [ ] **4.3 Experiment.** Change `CHUNK_SIZE` and `CHUNK_OVERLAP` in `.env`, re-ingest (truncate the tables first), and re-run the eval. Record every result in the **Results** table at the top of this README.
- [ ] **4.4 Stretch:** add answer-quality scoring with an LLM-as-judge or the `ragas` library (faithfulness, answer relevance).

  📝 Commit: `feat: retrieval evaluation with hit@k and MRR`

**Interview gold:** "I measured hit@5 at X%, tuned the chunk size and got it to Y%."

## Phase 5: React frontend (about 2–3 hours)

- [ ] **5.1 Run it**
  ```bash
  cd frontend
  cp .env.example .env
  npm install
  npm run dev               # opens http://localhost:5173
  ```
- [ ] **5.2 Ask a question in the browser** with the API still running.
- [ ] **5.3 Your own improvements:** show the source text when a citation is clicked, add a loading spinner and a "copy answer" button.

  📝 Commit: `feat: React frontend for asking questions`

## Phase 6: Docker (about 1 hour)

- [ ] **6.1 Build and run the API container**
  ```bash
  docker build -t docqa-api .
  docker run --rm -p 8080:8080 --env-file .env \
    -e DATABASE_URL=postgresql://rag:rag@host.docker.internal:5432/rag docqa-api
  ```
- [ ] **6.2 Test** <http://localhost:8080/health>

  📝 Commit: `chore: production Dockerfile`

## Phase 7: Deploy to GCP with Terraform (about 3–4 hours)

> 💰 **Cost safety first.** Create a GCP account (the $300 free credit) and immediately set a **budget alert** at ₹500: Billing → Budgets & alerts. Cloud Run scales to zero, so it costs almost nothing when idle.

- [ ] **7.1 Get a free hosted Postgres with pgvector.** Sign up at <https://neon.tech> (free tier), create a database, and copy its connection string. Then run ingestion against it:
  ```bash
  DATABASE_URL="<neon-url>" python -m app.ingest
  ```
- [ ] **7.2 Install the gcloud CLI and Terraform**
  - <https://cloud.google.com/sdk/docs/install>
  - <https://developer.hashicorp.com/terraform/install>
  ```bash
  gcloud auth login
  gcloud auth application-default login
  gcloud config set project YOUR_PROJECT_ID
  ```
- [ ] **7.3 Create the registry first, then push the image**
  ```bash
  cd infra/terraform
  cp terraform.tfvars.example terraform.tfvars    # fill in your values
  terraform init
  terraform apply -target=google_artifact_registry_repository.docqa -target=google_project_service.services

  cd ../..
  gcloud builds submit --tag asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/docqa/api:v1
  ```
- [ ] **7.4 Deploy everything**
  ```bash
  cd infra/terraform
  terraform apply           # prints api_url at the end
  ```
- [ ] **7.5 Test the live URL:** `<api_url>/health`, then `<api_url>/docs`.
- [ ] **7.6 Point the frontend at it:** set `VITE_API_URL=<api_url>` in `frontend/.env`. Optionally deploy the frontend for free on Vercel or Netlify.

  📝 Commit: `infra: deploy API to Cloud Run with Terraform`

**When you're done showing it:** run `terraform destroy` to remove everything.

## Phase 8: CI/CD and polish (about 2 hours)

- [ ] **8.1 CI is already running** on every push (lint + tests). Add the badge at the top of this README. It's already there; make sure it shows green.
- [ ] **8.2 Stretch: continuous deployment.** Add a workflow that builds the image and deploys to Cloud Run on every push to `main`, using GitHub's Workload Identity Federation (no keys stored in GitHub).
- [ ] **8.3 Record a 1–2 minute demo** (Loom or a screen recording → GIF) and add it to this README.
- [ ] **8.4 Write a "What I learned" section** at the bottom: three or four honest bullets.
- [ ] **8.5 Pin the repo** on your GitHub profile.

---

## Resume bullet (after you finish)

> **DocQA: Production RAG Platform** | Python, FastAPI, pgvector, React, Docker, Terraform, GCP Cloud Run
> - Built an idempotent document ingestion pipeline (chunking, embeddings, pgvector HNSW index) over **N documents**, and a FastAPI service returning cited LLM answers.
> - Created a retrieval evaluation suite (hit@k, MRR) and tuned chunking to raise hit@5 from **X% to Y%**.
> - Deployed to GCP Cloud Run with Terraform and GitHub Actions CI, with a React frontend.

Replace N, X and Y with your real numbers.

## Project structure

```
rag-docqa-platform/
├── app/
│   ├── config.py        # settings from .env
│   ├── chunking.py      # clean + chunk text (pure Python, unit-tested)
│   ├── db.py            # Postgres + pgvector schema
│   ├── embeddings.py    # sentence-transformers
│   ├── ingest.py        # idempotent ingestion pipeline
│   ├── retrieve.py      # vector search
│   ├── llm.py           # OpenAI-compatible LLM client + prompt
│   └── api.py           # FastAPI endpoints
├── eval/                # retrieval evaluation
├── tests/               # pytest unit tests
├── data/raw/            # source documents
├── frontend/            # React + Vite UI
├── infra/terraform/     # GCP Cloud Run deployment
├── .github/workflows/   # CI
├── docs/ROADMAP.md      # next projects
├── docker-compose.yml   # local Postgres + pgvector
└── Dockerfile
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `connection refused` on port 5432 | Docker isn't running, or run `docker compose up -d` |
| `extension "vector" does not exist` | Use the `pgvector/pgvector` image (already set in docker-compose.yml) |
| `/ask` returns 502 | The LLM isn't reachable. Check that Ollama is running (`ollama list`) or that your API key in `.env` is valid |
| Changed `EMBED_MODEL` and inserts fail | The vector size changed. Update `EMBED_DIM`, drop the tables, and re-ingest |
| `pip install` is very slow | `sentence-transformers` pulls in PyTorch (large). Install the CPU build first: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |

## Author

**Lokesh Reddy Maddali**, Data Engineer · [GitHub](https://github.com/Lokesh4561)
