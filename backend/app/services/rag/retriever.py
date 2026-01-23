
from dataclasses import dataclass
from typing import Optional, List
import chromadb

@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    similarity_score: float

class Retriever:
    """
    Retrieves chunks from ChromaDB database based on similarity score to user input.
    """
    def __init__(self, collection: chromadb.Collection, embedder):
        self.collection = collection
        self.embedder = embedder
    
    def retrieve(self, query: str, threshold: float | None = None, top_k: int = 5)->List[RetrievedChunk]:
        """
        Retrieves the top_k results filtered by an optional similarity threshold
        
        :param query: User input string
        :type query: str
        :param threshold: Minimum similarity score for lyric to be included 
        :type threshold: Optional[float]
        :param top_k: Number of top results to return (default=5)
        :type top_k: int
        :return: List of chunks and related data stored in RetrievedChunk objects
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if threshold is not None and not (0 <= threshold <= 1):
            raise ValueError("Threshold must be between 0 and 1")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        query_embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Unwrap results (ChromaDB returns nested lists for batch queries)
        ids = results['ids'][0]
        distances = results['distances'][0]
        metadatas = results['metadatas'][0]
        documents = results['documents'][0]

        chunks = []
        for distance, metadata, text in zip(distances, metadatas, documents):
            similarity = 1 - (distance / 2)

            if threshold is not None and similarity < threshold:
                break
        
            chunks.append(RetrievedChunk(
                text=text,
                metadata=metadata,
                similarity_score=similarity
            ))
    
        return chunks