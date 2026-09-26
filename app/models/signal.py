from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class OpportunitySignal(BaseModel):
    signal_type: str  # e.g. "recent_search", "perf_dip", "research_digest", "recall_due", "ipl_match"
    identifier: str    # e.g. "dental_check_up", "calls_dip_50pct", "jida_oct_2026"
    strength: float = 5.0
    recency: float = 5.0
    business_relevance: float = 5.0
    actionability: float = 5.0
    offer_match: float = 5.0
    evidence: Dict[str, Any] = {}
    
    @property
    def priority_score(self) -> float:
        return (
            self.strength * 2.0 +
            self.recency * 1.5 +
            self.business_relevance * 1.5 +
            self.actionability * 1.5 +
            self.offer_match * 1.5
        )
