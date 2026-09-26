from typing import Dict, Any, Optional
from app.models.signal import OpportunitySignal
from app.storage.state_store import state_store
from app.utils.hashing import build_suppression_key

class SuppressionEngine:
    """
    Suppression Engine determines if a proactive message should be sent or suppressed.
    Prevents repetitive nudging on identical context ticks.
    """
    def should_suppress(
        self,
        merchant_id: str,
        category_slug: str,
        opportunity: OpportunitySignal,
        trigger: Optional[Dict[str, Any]] = None,
        context_version: int = 1
    ) -> tuple[bool, str, str]:
        """
        Returns (should_suppress: bool, suppression_key: str, reason: str).
        """
        # Determine suppression key: use explicit trigger suppression_key if present
        if trigger and trigger.get("suppression_key"):
            key = trigger["suppression_key"]
        else:
            key = build_suppression_key(
                merchant_id=merchant_id,
                category_slug=category_slug,
                signal_type=opportunity.signal_type,
                signal_identifier=opportunity.identifier,
                action_type="outreach",
                version=context_version
            )

        fingerprint = self._fingerprint(opportunity, context_version)

        if state_store.is_key_suppressed(key):
            prev = state_store.get_suppression_fingerprint(key)
            if prev == fingerprint:
                return True, key, f"Opportunity key '{key}' already messaged; no material context change."
            # Material change (e.g. search count) — allow re-send with versioned key
            key = f"{key}:fp{fingerprint}"

        if state_store.is_key_suppressed(key):
            return True, key, f"Opportunity key '{key}' already messaged."

        state_store.set_suppression_fingerprint(key, fingerprint)
        return False, key, "New actionable opportunity detected."

    def _fingerprint(self, opportunity: OpportunitySignal, context_version: int) -> str:
        ev = opportunity.evidence or {}
        count = ev.get("count", ev.get("current_count", ""))
        delta = ev.get("delta_pct", "")
        return f"v{context_version}:c{count}:d{delta}:{opportunity.identifier}"
