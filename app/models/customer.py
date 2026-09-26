from pydantic import BaseModel
from typing import List, Optional

class CustomerIdentity(BaseModel):
    name: str
    phone_redacted: Optional[str] = "<phone>"
    language_pref: Optional[str] = "en"
    age_band: Optional[str] = None

class Relationship(BaseModel):
    first_visit: Optional[str] = None
    last_visit: Optional[str] = None
    visits_total: int = 1
    services_received: List[str] = []

class CustomerContextModel(BaseModel):
    customer_id: str
    merchant_id: str
    identity: CustomerIdentity
    relationship: Optional[Relationship] = None
    state: str = "active"
