# Retrieval Augmented Generation (RAG)

Retrieval augmented generation combines a search step with a large language model. Instead of relying only on what the model memorised during training, the system first retrieves relevant passages from a document store and then asks the model to answer using those passages.

Documents are split into chunks because embedding models and LLM prompts have size limits, and because smaller chunks make retrieval more precise. A chunk that is too small loses context; a chunk that is too large dilutes the match. Overlap between chunks keeps sentences that cross a boundary searchable.

Each chunk is turned into an embedding vector and stored in a vector database such as pgvector. At question time, the question is embedded the same way and the closest chunks are returned by cosine similarity.

RAG systems should be evaluated on two things: whether retrieval finds the right passages (hit rate, MRR) and whether the generated answer is faithful to them.
