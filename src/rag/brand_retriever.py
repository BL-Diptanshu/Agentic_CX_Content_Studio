from crewai.tools import BaseTool
from pydantic import Field, PrivateAttr
import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import Type

class BrandGuidelineRetriever(BaseTool):
    name: str = "Brand Guideline Retriever"
    description: str = (
        "Retrieves specific brand guideline information including voice, tone, "
        "target audience, visual identity, and messaging framework. "
        "Input should be a focused question about brand guidelines."
    )
    
    _model: SentenceTransformer = PrivateAttr()
    _index: faiss.Index = PrivateAttr()
    _docs: list = PrivateAttr()
    _top_k: int = PrivateAttr(default=3)

    def __init__(self, data_dir: str = "data", top_k: int = 3):
        super().__init__()
        self._top_k = top_k
        self._load_resources(data_dir)

    def _load_resources(self, data_dir):
        index_file = os.path.join(data_dir, "brand_index.bin")
        docs_file = os.path.join(data_dir, "brand_docs.pkl")
        
        if not os.path.exists(index_file) or not os.path.exists(docs_file):
            raise FileNotFoundError(
                "Brand guideline index not found. "
                "Please run src/rag/build_embeds.py first."
            )
            
        self._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', local_files_only=True)
        self._index = faiss.read_index(index_file)
        
        with open(docs_file, "rb") as f:
            self._docs = pickle.load(f)

    def _run(self, query: str, k: int = None) -> str:
        try:
            num_results = k if k is not None else self._top_k
            query_vector = self._model.encode([query])
            
            distances, indices = self._index.search(
                np.array(query_vector).astype('float32'), 
                num_results
            )
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self._docs):
                    relevance = 1 / (1 + distances[0][i])
                    result_entry = {
                        'text': self._docs[idx],
                        'relevance': relevance,
                        'rank': i + 1
                    }
                    results.append(result_entry)
            
            if not results:
                return "No relevant brand guideline information found."
            
            output = "Brand Guideline Information:\n\n"
            for res in results:
                output += f"[Result {res['rank']} - Relevance: {res['relevance']:.2%}]\n"
                output += f"{res['text']}\n\n"
                output += "-" * 60 + "\n\n"
            
            return output.strip()
            
        except Exception as e:
            return f"Error retrieving brand guidelines: {str(e)}"

if __name__ == "__main__":
    try:
        retriever = BrandGuidelineRetriever()
        print("BrandGuidelineRetriever initialized successfully")
        
        test_query = "What is the brand voice?"
        print(f"\nTest Query: {test_query}")
        print(retriever._run(test_query))
        
    except Exception as e:
        print(f"Error: {e}")

