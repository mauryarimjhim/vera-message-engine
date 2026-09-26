from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any

class TickAction(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    send_as: Literal["vera", "merchant_on_behalf"] = "vera"
    trigger_id: str
    template_name: Optional[str] = "vera_default_v1"
    template_params: Optional[List[str]] = []
    body: str
    cta: str = "open_ended"
    suppression_key: str
    rationale: str

class TickRequest(BaseModel):
    now: str
    available_triggers: List[str] = []

class TickResponse(BaseModel):
    actions: List[TickAction] = []

class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: Literal["merchant", "customer"] = "merchant"
    message: str
    received_at: Optional[str] = None
    turn_number: int = 1

class ReplyResponse(BaseModel):
    action: Literal["send", "wait", "end"]
    body: Optional[str] = None
    cta: Optional[str] = None
    wait_seconds: Optional[int] = None
    rationale: str
