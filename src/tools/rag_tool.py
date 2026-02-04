from crewai.tools import BaseTool
from pydantic import Field, PrivateAttr
import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import Type

class BrandKnowledgeTool(BaseTool):
    name: str = "Brand Knowledge Tool"
    description: str = (
        "Useful for retrieving brand guidelines, voice, tone, and do's/don'ts. "
        "Input should be a specific query about the brand (e.g., 'What is the brand tone?', 'Forbidden words')."
    )
    
    # Private attributes (not involved in validation)
    _model: SentenceTransformer = PrivateAttr()
    _index: faiss.Index = PrivateAttr()
    _docs: list = PrivateAttr()

    def __init__(self, data_dir: str = "data"):
        super().__init__()
        self._load_resources(data_dir)

    def _load_resources(self, data_dir):
        """Load model and index efficiently"""
        index_file = os.path.join(data_dir, "brand_index.bin")
        docs_file = os.path.join(data_dir, "brand_docs.pkl")
        
        if not os.path.exists(index_file) or not os.path.exists(docs_file):
            raise FileNotFoundError("RAG Index not found. Please run scripts/setup_rag.py first.")
            
        self._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self._index = faiss.read_index(index_file)
        
        with open(docs_file, "rb") as f:
            self._docs = pickle.load(f)

    def _run(self, query: str) -> str:
        """Retrieve relevant context"""
        try:
            # Create embedding
            query_vector = self._model.encode([query])
            
            # Search FAISS
            k = 3
            D, I = self._index.search(np.array(query_vector).astype('float32'), k)
            
            results = []
            for idx in I[0]:
                if idx < len(self._docs):
                    results.append(self._docs[idx])
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"Error retrieving brand knowledge: {str(e)}"
