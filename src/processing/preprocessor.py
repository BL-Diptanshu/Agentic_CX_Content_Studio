import re
from typing import Callable, List


def lowercase_text(text: str) -> str:
    return text.lower()


def normalize_whitespace(text: str) -> str:
    return ' '.join(text.split())


def remove_special_chars(text: str, keep_punctuation: bool = True) -> str:
    if keep_punctuation:
        pattern = r'[^a-zA-Z0-9\s.,!?-]'
    else:
        pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(pattern, '', text)


def remove_urls(text: str) -> str:
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_pattern, '', text)


def remove_extra_newlines(text: str) -> str:
    return re.sub(r'\n+', '\n', text)


def strip_text(text: str) -> str:
    return text.strip()


def preprocess_pipeline(text: str, steps: List[Callable[[str], str]]) -> str:
    for step in steps:
        text = step(text)
    return text
