"""
Embedder Module - Create embeddings from text
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


from src.config.settings import settings

class Embedder:
    """Creates embeddings from text using SentenceTransformers"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedder with specified model
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name or settings.RAG_EMBEDDING_MODEL
        self.model = SentenceTransformer(self.model_name, local_files_only=True)
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Create embeddings for text
        
        Args:
            text: Single string or list of strings
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(text)
        return np.array(embeddings).astype('float32')
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        Create embeddings for multiple documents
        
        Args:
            documents: List of document strings
            
        Returns:
            Numpy array of embeddings
        """
        return self.embed_text(documents)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Create embedding for a single query
        
        Args:
            query: Query string
            
        Returns:
            Numpy array with single embedding
        """
        return self.embed_text([query])
