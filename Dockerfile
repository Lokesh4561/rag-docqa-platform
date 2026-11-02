FROM python:3.11-slim

WORKDIR /app

# CPU-only PyTorch keeps the image much smaller than the default CUDA build.
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the embedding model at build time so cold starts are faster.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY app ./app

ENV PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT}"]
