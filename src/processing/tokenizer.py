from typing import Optional


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        import tiktoken
        model_encodings = {
            "gpt-3.5-turbo": "cl100k_base",
            "gpt-4": "cl100k_base",
            "llama-3.1-8b-instant": "cl100k_base",
            "text-embedding-ada-002": "cl100k_base"
        }
        encoding_name = model_encodings.get(model, "cl100k_base")
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except ImportError:
        words = len(text.split())
        return int(words / 0.75)


def estimate_cost(text: str, model: str = "llama-3.1-8b-instant", price_per_1k_tokens: float = 0.0001) -> float:
    tokens = count_tokens(text, model)
    return (tokens / 1000) * price_per_1k_tokens


def truncate_to_token_limit(text: str, max_tokens: int, model: str = "gpt-3.5-turbo") -> str:
    try:
        import tiktoken
        encoding_name = "cl100k_base"
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return encoding.decode(truncated_tokens)
    except ImportError:
        words = text.split()
        estimated_words = int(max_tokens * 0.75)
        return ' '.join(words[:estimated_words])


def split_by_token_budget(text: str, budget: int, model: str = "gpt-3.5-turbo", overlap: int = 0) -> list:
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        
        chunks = []
        start = 0
        while start < len(tokens):
            end = start + budget
            chunk_tokens = tokens[start:end]
            chunks.append(encoding.decode(chunk_tokens))
            start = end - overlap
        return chunks
    except ImportError:
        words = text.split()
        word_budget = int(budget * 0.75)
        overlap_words = int(overlap * 0.75)
        
        chunks = []
        for i in range(0, len(words), word_budget - overlap_words):
            chunk = ' '.join(words[i:i + word_budget])
            chunks.append(chunk)
        return chunks


def get_token_info(text: str, model: str = "gpt-3.5-turbo") -> dict:
    return {
        "token_count": count_tokens(text, model),
        "character_count": len(text),
        "word_count": len(text.split()),
        "lines": text.count('\n') + 1
    }
