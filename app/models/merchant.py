from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Identity(BaseModel):
    name: str
    city: str
    locality: str
    place_id: Optional[str] = None
    verified: bool = True
    languages: List[str] = ["en", "hi"]
    owner_first_name: Optional[str] = None

class Subscription(BaseModel):
    status: str
    plan: str
    days_remaining: Optional[int] = 0

class Performance(BaseModel):
    window_days: int = 30
    views: int = 0
    calls: int = 0
    directions: int = 0
    ctr: float = 0.0
    delta_7d: Optional[Dict[str, float]] = None

class MerchantOffer(BaseModel):
    id: str
    title: str
    status: str = "active"
    price: Optional[str] = None

class CustomerAggregate(BaseModel):
    total_unique_ytd: int = 0
    lapsed_180d_plus: Optional[int] = 0
    retention_6mo_pct: Optional[float] = 0.0
    high_risk_adult_count: Optional[int] = 0

class MerchantContextModel(BaseModel):
    merchant_id: str
    category_slug: str
    identity: Identity
    subscription: Optional[Subscription] = None
    performance: Optional[Performance] = None
    offers: List[MerchantOffer] = []
    signals: List[str] = []
    customer_aggregate: Optional[CustomerAggregate] = None
