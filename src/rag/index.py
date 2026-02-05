"""
Index Builder - Build FAISS index from documents
"""
from typing import List
from pathlib import Path
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore


class IndexBuilder:
    """Build and save FAISS index from documents"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize index builder
        
        Args:
            model_name: Embedder model name
        """
        self.embedder = Embedder(model_name)
    
    def build_from_documents(self, documents: List[str]) -> VectorStore:
        """
        Build vector store from documents
        
        Args:
            documents: List of document strings
            
        Returns:
            VectorStore with indexed documents
        """
        # Create embeddings
        embeddings = self.embedder.embed_documents(documents)
        
        # Create vector store
        vector_store = VectorStore(dimension=embeddings.shape[1])
        vector_store.add_documents(embeddings, documents)
        
        return vector_store
    
    def build_from_file(self, file_path: str, chunk_size: int = 500) -> VectorStore:
        """
        Build vector store from text file
        
        Args:
            file_path: Path to text file
            chunk_size: Characters per chunk
            
        Returns:
            VectorStore with indexed document chunks
        """
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chunk content
        documents = self._chunk_text(content, chunk_size)
        
        return self.build_from_documents(documents)
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text
            chunk_size: Character per chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
