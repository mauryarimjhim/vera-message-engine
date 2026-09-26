from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ConversationTurn(BaseModel):
    turn_number: int
    from_role: str
    message: str
    timestamp: str

class ConversationState(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    category_slug: str = "dentists"
    current_state: str = "IDLE"  # IDLE, AWAITING_REPLY, POSITIVE_INTENT, NEGATIVE_INTENT, DEFERRED, QUESTION, OBJECTION, NEW_INTENT, AUTO_REPLY_ENDED, HOSTILE_ENDED
    last_trigger_id: Optional[str] = None
    last_suppression_key: Optional[str] = None
    last_sent_body: Optional[str] = None
    last_sent_cta: Optional[str] = None
    auto_reply_count: int = 0
    turns: List[ConversationTurn] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)
