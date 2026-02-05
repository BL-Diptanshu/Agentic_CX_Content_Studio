# build_embeds.py
import os
import pickle
import faiss
import sys
# Add project root to path
sys.path.append(os.getcwd())

from sentence_transformers import SentenceTransformer
from src.core.brand_kb_loader import get_kb_loader

def build_index():
    print("Starting index build...")
    # 1. Load Data
    loader = get_kb_loader()
    
    docs = []
    
    # Process Tone
    print("Loading tone profile...")
    try:
        tone_profile = loader.load_tone_profile()
        if tone_profile:
            if 'required_tone' in tone_profile:
                docs.append(f"Brand Key Requirements: {', '.join(tone_profile.get('required_tone', []))}")
            if 'disallowed_tone' in tone_profile:
                docs.append(f"Brand Tone Constraints (Disallowed): {', '.join(tone_profile.get('disallowed_tone', []))}")
            if 'writing_style' in tone_profile:
                docs.append(f"Brand Writing Style Guide: {', '.join(tone_profile.get('writing_style', []))}")
    except Exception as e:
        print(f"Error loading tone profile: {e}")

    # Process Forbidden Language
    print("Loading forbidden language...")
    try:
        forbidden = loader.load_forbidden_language()
        for category, terms in forbidden.items():
            docs.append(f"Forbidden Language Policy ({category}): {', '.join(terms)}")
    except Exception as e:
        print(f"Error loading forbidden language: {e}")

    # Process Allowed Language
    print("Loading allowed language...")
    try:
        allowed = loader.load_allowed_language()
        for category, terms in allowed.items():
            docs.append(f"Encouraged Language ({category}): {', '.join(terms)}")
    except Exception as e:
        print(f"Error loading allowed language: {e}")

    print(f"Extracted {len(docs)} documents for indexing.")
    
    if not docs:
        print("No documents to index. Exiting.")
        return

    # 2. Embed
    print("Generating embeddings using modular Embedder...")
    try:
        from src.rag.embedder import Embedder
        embedder = Embedder()
        embeddings = embedder.embed_documents(docs)
    except Exception as e:
        print(f"Error initializing Embedder or generating embeddings: {e}")
        return

    # 3. Index
    print("Building FAISS index...")
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)

    # 4. Save
    output_dir = os.path.join("data", "vectordb", "faiss")
    os.makedirs(output_dir, exist_ok=True)
    
    index_path = os.path.join(output_dir, "brand_index.bin")
    docs_path = os.path.join(output_dir, "brand_docs.pkl")
    
    faiss.write_index(index, index_path)
    with open(docs_path, "wb") as f:
        pickle.dump(docs, f)
        
    print(f"Index built and saved to {output_dir}")

if __name__ == "__main__":
    build_index()
