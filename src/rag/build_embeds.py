import logging
import os
from pathlib import Path
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.config.settings import settings
from src.rag.index import IndexBuilder

def load_documents(kb_path: Path) -> List[str]:
    """Load all text documents from the knowledge base directory"""
    documents = []
    logger.info(f"Scanning for documents in {kb_path}...")
    
    if not kb_path.exists():
        logger.warning(f"Knowledge base directory not found: {kb_path}")
        return []
        
    for file_path in kb_path.glob("**/*"):
        if file_path.suffix.lower() in ['.txt', '.md', '.docx']:
             try:
                # Simple text loader for now. 
                # For docx we might need python-docx, but let's assume txt/md for base KB
                # or use the document_parser if needed.
                # For now keeping it simple as per audit requirement.
                if file_path.suffix.lower() == '.docx':
                    import docx
                    doc = docx.Document(file_path)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    if text.strip():
                        documents.append(text)
                        logger.info(f"Loaded {file_path.name}")
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                        if text.strip():
                            documents.append(text)
                            logger.info(f"Loaded {file_path.name}")
             except Exception as e:
                 logger.error(f"Failed to load {file_path}: {e}")
                 
    return documents

def build_index():
    """Build and save the FAISS index"""
    logger.info("Starting index build process...")
    
    # 1. Load documents
    docs = load_documents(settings.BRAND_KB_PATH)
    if not docs:
        logger.error("No documents found in knowledge base. Index build aborted.")
        return
    
    logger.info(f"Loaded {len(docs)} documents. Building index...")
    
    # 2. Build Index using IndexBuilder
    builder = IndexBuilder(model_name=settings.RAG_EMBEDDING_MODEL)
    
    # We might want to chunk them first if they are large
    # The IndexBuilder.build_from_documents takes full docs, 
    # but let's check if we should iterate and chunk.
    # IndexBuilder.build_from_file chunks, but build_from_documents does not.
    # Let's simple-chunk here or rely on small docs. 
    # For robustness, let's chunk.
    
    all_chunks = []
    for doc in docs:
        chunks = builder._chunk_text(doc, chunk_size=500)
        all_chunks.extend(chunks)
        
    logger.info(f"Created {len(all_chunks)} chunks from {len(docs)} documents.")
    
    if not all_chunks:
        logger.error("No text chunks generated.")
        return

    # 3. Create VectorStore
    vector_store = builder.build_from_documents(all_chunks)
    
    # 4. Save
    logger.info(f"Saving index to {settings.RAG_INDEX_PATH}...")
    vector_store.save(str(settings.RAG_INDEX_PATH), str(settings.RAG_DOCS_PATH))
    logger.info("✅ Index build complete!")

if __name__ == "__main__":
    build_index()
