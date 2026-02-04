"""
Setup RAG: Ingest Brand Guidelines and create FAISS index.
"""
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# Paths
DATA_DIR = "data"
GUIDELINES_FILE = os.path.join(DATA_DIR, "brand_guidelines.txt")
INDEX_FILE = os.path.join(DATA_DIR, "brand_index.bin")
DOCS_FILE = os.path.join(DATA_DIR, "brand_docs.pkl")

def setup_rag():
    print(" Starting RAG Setup...")
    
    # 1. Load Data
    if not os.path.exists(GUIDELINES_FILE):
        print(f" Error: {GUIDELINES_FILE} not found!")
        return
        
    print(f"📄 Reading {GUIDELINES_FILE}...")
    with open(GUIDELINES_FILE, "r", encoding="utf-8") as f:
        text = f.read()
        
    # 2. Chunking (Simple splitting by newlines or paragraphs)
    # Removing empty lines and very short lines
    chunks = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
    print(f"✂️  Created {len(chunks)} chunks.")
    
    # 3. Create Embeddings
    print("🧠 Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    
    # 4. Create FAISS Index
    print("🗂️  Creating FAISS index...")
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings).astype('float32'))
    
    # 5. Save Index and Chunks
    print(f"💾 Saving index to {INDEX_FILE}...")
    faiss.write_index(index, INDEX_FILE)
    
    print(f"💾 Saving documents to {DOCS_FILE}...")
    with open(DOCS_FILE, "wb") as f:
        pickle.dump(chunks, f)
        
    print("✅ RAG Setup Complete!")

if __name__ == "__main__":
    setup_rag()
