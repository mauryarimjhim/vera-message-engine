import hashlib
import json
from typing import Any, Dict

def compute_hash(data: Any) -> str:
    """Computes SHA256 hex digest of a Python object/dict for caching and deduplication."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()[:16]

def build_suppression_key(
    merchant_id: str,
    category_slug: str,
    signal_type: str,
    signal_identifier: str,
    action_type: str,
    version: int = 1
) -> str:
    """
    Builds a deterministic suppression key.
    Example: "dental:m_001:search:dental-check-up:promote_offer:v1"
    """
    clean_sig = signal_identifier.lower().replace(' ', '-').replace('_', '-')
    return f"{category_slug}:{merchant_id}:{signal_type}:{clean_sig}:{action_type}:v{version}"
