from pydantic import BaseModel
from typing import Dict, Any, Optional, Literal

class TriggerContextModel(BaseModel):
    id: str
    scope: Literal["merchant", "customer"]
    kind: str
    source: Literal["external", "internal"]
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    payload: Dict[str, Any] = {}
    urgency: int = 1
    suppression_key: Optional[str] = None
    expires_at: Optional[str] = None
