"""
Vector Store - FAISS vector database interface
"""
import faiss
import pickle
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional


class VectorStore:
    """FAISS-based vector store for similarity search"""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize vector store
        
        Args:
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
    
    def add_documents(self, embeddings: np.ndarray, documents: List[str]):
        """
        Add documents and embeddings to the store
        
        Args:
            embeddings: Numpy array of embeddings
            documents: List of document strings
        """
        self.index.add(embeddings)
        self.documents.extend(documents)
    
    def search(self, query_embedding: np.ndarray, k: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding
            k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices
    
    def get_documents(self, indices: List[int]) -> List[str]:
        """
        Get documents by indices
        
        Args:
            indices: List of document indices
            
        Returns:
            List of document strings
        """
        return [self.documents[i] for i in indices if i < len(self.documents)]
    
    def save(self, index_path: str, docs_path: str):
        """
        Save index and documents to disk
        
        Args:
            index_path: Path to save FAISS index
            docs_path: Path to save documents pickle
        """
        # Create directories if needed
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        Path(docs_path).parent.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, index_path)
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    @classmethod
    def load(cls, index_path: str, docs_path: str) -> 'VectorStore':
        """
        Load index and documents from disk
        
        Args:
            index_path: Path to FAISS index
            docs_path: Path to documents pickle
            
        Returns:
            Loaded VectorStore instance
        """
        index = faiss.read_index(index_path)
        with open(docs_path, 'rb') as f:
            documents = pickle.load(f)
        
        # Create instance and set loaded data
        store = cls(dimension=index.d)
        store.index = index
        store.documents = documents
        return store
    
    @property
    def num_documents(self) -> int:
        """Get number of documents in store"""
        return len(self.documents)
