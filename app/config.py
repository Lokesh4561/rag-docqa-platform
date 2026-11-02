"""Central configuration. Every setting can be overridden with an environment variable (see .env.example)."""

import os

from dotenv import load_dotenv

load_dotenv()

# Database (Postgres + pgvector)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rag:rag@localhost:5432/rag")

# Embeddings (runs locally, free)
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))

# LLM: any OpenAI-compatible endpoint (Ollama locally, Groq, Gemini, OpenAI...)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")

# Chunking and retrieval
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "5"))

RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data/raw")
