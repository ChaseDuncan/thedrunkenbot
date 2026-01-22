
from chonkie import TokenChunker
from sentence_transformers import SentenceTransformer

# Singleton chunker
chunker = TokenChunker(
    tokenizer="gpt2",
    chunk_size=25,
    chunk_overlap=7
)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
