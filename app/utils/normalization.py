import re
import string

def normalize_search_query(query: str) -> str:
    """
    Normalizes a search query for comparison:
    - Lowercase
    - Replace hyphens and punctuation with spaces
    - Strip excess whitespace
    Example: "DENTAL CHECK-UP" -> "dental check up"
    """
    if not query:
        return ""
    q = query.lower()
    # Replace hyphens and punctuation with space
    q = re.sub(r'[\-_/\\,.:;!?()]', ' ', q)
    # Strip excess whitespace
    q = ' '.join(q.split())
    return q

def normalize_text(text: str) -> str:
    """Normalizes whitespace in general text strings."""
    if not text:
        return ""
    return ' '.join(text.split())
