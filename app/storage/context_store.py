import threading
from datetime import datetime, timezone
from typing import Dict, Tuple, Any, Optional

class ContextStore:
    """
    Thread-safe stateful Context Store for Vera.
    Stores context payloads keyed by (scope, context_id).
    Supports versioning, atomic updates, and retrieval.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._contexts: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def put_context(self, scope: str, context_id: str, version: int, payload: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Pushes or updates context.
        Returns (accepted: bool, ack_or_reason: str, current_version: int).
        """
        with self._lock:
            key = (scope, context_id)
            existing = self._contexts.get(key)
            if existing:
                cur_ver = existing["version"]
                if cur_ver == version:
                    # Idempotent re-post of same version
                    return True, f"ack_{context_id}_v{version}", cur_ver
                elif cur_ver > version:
                    # Stale lower version
                    return False, "stale_version", cur_ver

            self._contexts[key] = {
                "version": version,
                "payload": payload,
                "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
            ack_id = f"ack_{context_id}_v{version}"
            return True, ack_id, version

    def get_context(self, scope: str, context_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            entry = self._contexts.get((scope, context_id))
            return entry["payload"] if entry else None

    def get_context_entry(self, scope: str, context_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._contexts.get((scope, context_id))

    def get_all_by_scope(self, scope: str) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            res = {}
            for (s, cid), data in self._contexts.items():
                if s == scope:
                    res[cid] = data["payload"]
            return res

    def get_counts(self) -> Dict[str, int]:
        with self._lock:
            counts = {"category": 0, "merchant": 0, "customer": 0, "trigger": 0}
            for (scope, _), _ in self._contexts.items():
                counts[scope] = counts.get(scope, 0) + 1
            return counts

    def clear(self):
        with self._lock:
            self._contexts.clear()

# Global singleton
context_store = ContextStore()
