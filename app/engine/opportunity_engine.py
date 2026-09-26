from typing import Dict, Any, List, Optional
from app.models.signal import OpportunitySignal
from app.engine.signal_engine import SignalEngine

class OpportunityEngine:
    """
    Ranks extracted signals and selects the SINGLE dominant opportunity.
    Philosophy: Python/Rules decide WHAT + WHEN.
    """
    def __init__(self):
        self.signal_engine = SignalEngine()

    def select_dominant_opportunity(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        trigger: Optional[Dict[str, Any]] = None,
        customer: Optional[Dict[str, Any]] = None
    ) -> Optional[OpportunitySignal]:
        signals = self.signal_engine.extract_signals(category, merchant, trigger, customer)
        if not signals:
            return None

        # Sort by priority score descending
        sorted_signals = sorted(signals, key=lambda s: s.priority_score, reverse=True)
        return sorted_signals[0]
