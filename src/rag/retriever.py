"""
Retriever - High-level retrieval interface using Embedder + VectorStore
"""
from typing import List, Dict
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore


class Retriever:
    """High-level retrieval interface combining embedder and vector store"""
    
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        """
        Initialize retriever
        
        Args:
            embedder: Embedder instance
            vector_store: VectorStore instance
        """
        self.embedder = embedder
        self.vector_store = vector_store
    
    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            
        Returns:
            List of dicts with 'text', 'relevance', 'rank' keys
        """
        # Embed query
        query_embedding = self.embedder.embed_query(query)
        
        # Search vector store
        distances, indices = self.vector_store.search(query_embedding, k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < self.vector_store.num_documents:
                relevance = 1 / (1 + distances[0][i])
                results.append({
                    'text': self.vector_store.documents[idx],
                    'relevance': relevance,
                    'rank': i + 1,
                    'distance': float(distances[0][i])
                })
        
        return results
    
    @classmethod
    def from_index(cls, index_path: str, docs_path: str, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2') -> 'Retriever':
        """
        Create retriever from saved index
        
        Args:
            index_path: Path to FAISS index
            docs_path: Path to documents pickle
            model_name: Embedder model name
            
        Returns:
            Retriever instance
        """
        embedder = Embedder(model_name)
        vector_store = VectorStore.load(index_path, docs_path)
        return cls(embedder, vector_store)
