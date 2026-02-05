from typing import List


def chunk_by_section(text: str, header_markers: List[str] = None) -> List[str]:
    if header_markers is None:
        header_markers = ['##', '#']
    
    chunks = []
    current_chunk = []
    
    for line in text.split('\n'):
        line = line.strip()
        is_header = any(line.startswith(marker) for marker in header_markers)
        
        if is_header and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
        elif line:
            current_chunk.append(line)
        elif current_chunk and len(current_chunk) > 1:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    chunks = [c for c in chunks if len(c.strip()) > 20]
    return chunks


def chunk_by_token_limit(text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        
        chunks = []
        start = 0
        while start < len(tokens):
            end = start + max_tokens
            chunk_tokens = tokens[start:end]
            chunks.append(encoding.decode(chunk_tokens))
            start = end - overlap
        
        return chunks
    except ImportError:
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_tokens - overlap):
            chunk = ' '.join(words[i:i + max_tokens])
            chunks.append(chunk)
        return chunks


def chunk_by_sentences(text: str, sentences_per_chunk: int = 5) -> List[str]:
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = ' '.join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)
    
    return chunks
