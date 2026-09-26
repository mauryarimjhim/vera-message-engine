import threading
from typing import Dict, Any, Optional, Set
from app.models.state import ConversationState, ConversationTurn

class StateStore:
    """
    Thread-safe store for conversation states and suppression tracking.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._conversations: Dict[str, ConversationState] = {}
        self._suppressed_keys: Set[str] = set()
        self._suppression_fingerprints: Dict[str, str] = {}
        self._conversation_meta: Dict[str, Dict[str, Any]] = {}
        self._merchant_auto_reply_streak: Dict[str, int] = {}

    def get_or_create_conversation(self, conversation_id: str, merchant_id: str, customer_id: Optional[str] = None) -> ConversationState:
        with self._lock:
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = ConversationState(
                    conversation_id=conversation_id,
                    merchant_id=merchant_id,
                    customer_id=customer_id
                )
            return self._conversations[conversation_id]

    def get_conversation(self, conversation_id: str) -> Optional[ConversationState]:
        with self._lock:
            return self._conversations.get(conversation_id)

    def add_turn(self, conversation_id: str, turn: ConversationTurn):
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.turns.append(turn)

    def is_key_suppressed(self, suppression_key: str) -> bool:
        if not suppression_key:
            return False
        with self._lock:
            return suppression_key in self._suppressed_keys

    def suppress_key(self, suppression_key: str):
        if suppression_key:
            with self._lock:
                self._suppressed_keys.add(suppression_key)

    def get_suppression_fingerprint(self, suppression_key: str) -> Optional[str]:
        with self._lock:
            return self._suppression_fingerprints.get(suppression_key)

    def set_suppression_fingerprint(self, suppression_key: str, fingerprint: str):
        with self._lock:
            self._suppression_fingerprints[suppression_key] = fingerprint

    def set_conversation_meta(self, conversation_id: str, meta: Dict[str, Any]):
        with self._lock:
            self._conversation_meta[conversation_id] = meta

    def get_conversation_meta(self, conversation_id: str) -> Dict[str, Any]:
        with self._lock:
            return dict(self._conversation_meta.get(conversation_id, {}))

    def bump_merchant_auto_reply(self, merchant_id: str) -> int:
        with self._lock:
            n = self._merchant_auto_reply_streak.get(merchant_id, 0) + 1
            self._merchant_auto_reply_streak[merchant_id] = n
            return n

    def reset_merchant_auto_reply(self, merchant_id: str):
        with self._lock:
            self._merchant_auto_reply_streak.pop(merchant_id, None)

    def clear(self):
        with self._lock:
            self._conversations.clear()
            self._suppressed_keys.clear()
            self._suppression_fingerprints.clear()
            self._conversation_meta.clear()
            self._merchant_auto_reply_streak.clear()

state_store = StateStore()
