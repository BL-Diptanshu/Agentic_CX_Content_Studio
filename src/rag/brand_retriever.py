from crewai.tools import BaseTool
from pydantic import Field, PrivateAttr, BaseModel
import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import Type
from src.prompt.rag_prompt_temp import (
    BRAND_RETRIEVER_DESCRIPTION,
    format_retrieval_results,
    NO_RESULTS_MESSAGE,
    RETRIEVAL_ERROR_TEMPLATE
)

class BrandGuidelineRetrieverInput(BaseModel):
    """Input schema for Brand Guideline Retriever"""
    query: str = Field(..., description="The search query to find relevant brand guideline information")

class BrandGuidelineRetriever(BaseTool):
    name: str = "Brand Guideline Retriever"
    description: str = BRAND_RETRIEVER_DESCRIPTION
    args_schema: Type[BaseModel] = BrandGuidelineRetrieverInput
    
    _model: SentenceTransformer = PrivateAttr()
    _index: faiss.Index = PrivateAttr()
    _docs: list = PrivateAttr()
    _top_k: int = PrivateAttr(default=3)

    def __init__(self, data_dir: str = "data", top_k: int = 3):
        super().__init__()
        self._top_k = top_k
        self._load_resources(data_dir)

    def _load_resources(self, data_dir):
        index_file = os.path.join(data_dir, "vectordb", "faiss", "brand_index.bin")
        docs_file = os.path.join(data_dir, "vectordb", "faiss", "brand_docs.pkl")
        
        if not os.path.exists(index_file) or not os.path.exists(docs_file):
            raise FileNotFoundError(
                "Brand guideline index not found. "
                "Please run src/rag/build_embeds.py first."
            )
            
        self._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', local_files_only=True)
        self._index = faiss.read_index(index_file)
        
        with open(docs_file, "rb") as f:
            self._docs = pickle.load(f)

    def _run(self, query: str) -> str:
        """Run the retrieval tool with the given query"""
        try:
            query_vector = self._model.encode([query])
            
            distances, indices = self._index.search(
                np.array(query_vector).astype('float32'), 
                self._top_k
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
            
            # Use template formatting
            return format_retrieval_results(results)
            
        except Exception as e:
            return RETRIEVAL_ERROR_TEMPLATE.format(error=str(e))

if __name__ == "__main__":
    try:
        retriever = BrandGuidelineRetriever()
        print("BrandGuidelineRetriever initialized successfully")
        
        test_query = "What is the brand voice?"
        print(f"\nTest Query: {test_query}")
        print(retriever._run(test_query))
        
    except Exception as e:
        print(f"Error: {e}")

