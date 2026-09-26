from typing import Dict, Any, List, Optional
import re
from app.models.signal import OpportunitySignal
from app.utils.normalization import normalize_search_query


def _offer_search_match(merchant: Dict[str, Any], normalized_query: str) -> float:
    """Score 0-10 for how well an active offer matches a normalized search query."""
    if not normalized_query:
        return 0.0
    best = 0.0
    for offer in merchant.get("offers", []):
        if offer.get("status") != "active":
            continue
        title = normalize_search_query(offer.get("title", ""))
        if not title:
            continue
        if normalized_query in title or title in normalized_query:
            best = max(best, 10.0)
            continue
        q_tokens = set(normalized_query.split())
        t_tokens = set(re.sub(r"[^\w\s]", " ", title).split())
        overlap = len(q_tokens & t_tokens)
        if overlap >= 2:
            best = max(best, 8.0 + min(2.0, overlap * 0.5))
    return best


class SignalEngine:
    """
    Extracts normalized signals from structured Category, Merchant, Customer, and Trigger contexts.
    """
    def extract_signals(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        trigger: Optional[Dict[str, Any]] = None,
        customer: Optional[Dict[str, Any]] = None
    ) -> List[OpportunitySignal]:
        signals: List[OpportunitySignal] = []

        # 1. Trigger Signal (highest recency if active)
        if trigger:
            kind = trigger.get("kind", "unknown")
            urgency = float(trigger.get("urgency", 1))
            payload = trigger.get("payload", {})
            sig = OpportunitySignal(
                signal_type=kind,
                identifier=trigger.get("suppression_key", trigger.get("id", kind)),
                strength=urgency * 2.0,
                recency=9.0,
                business_relevance=8.0,
                actionability=9.0,
                offer_match=8.0,
                evidence=payload
            )
            signals.append(sig)

        # 2. Recent Search Signals (if present in merchant or trigger payload)
        recent_searches = merchant.get("recent_searches") or (trigger.get("payload", {}).get("recent_searches") if trigger else None)
        if recent_searches and isinstance(recent_searches, list):
            for s in recent_searches:
                raw_q = s.get("query", "")
                norm_q = normalize_search_query(raw_q)
                count = s.get("count", 0)
                offer_match = _offer_search_match(merchant, norm_q) or 5.0
                sig = OpportunitySignal(
                    signal_type="recent_search",
                    identifier=norm_q,
                    strength=min(10.0, 5.0 + (count / 50.0)),
                    recency=10.0,
                    business_relevance=9.0,
                    actionability=9.0 if count >= 30 else 6.0,
                    offer_match=offer_match,
                    evidence={"query": raw_q, "normalized_query": norm_q, "count": count, "location": s.get("location")}
                )
                signals.append(sig)

        # 3. Performance Signals (Dip / Spike)
        perf = merchant.get("performance", {})
        delta_7d = perf.get("delta_7d", {}) if perf else {}
        calls_pct = delta_7d.get("calls_pct", 0)
        views_pct = delta_7d.get("views_pct", 0)

        if calls_pct <= -0.25:
            signals.append(OpportunitySignal(
                signal_type="perf_dip",
                identifier="calls_drop",
                strength=8.0,
                recency=8.0,
                business_relevance=9.0,
                actionability=8.0,
                evidence={"metric": "calls", "delta_pct": calls_pct}
            ))

        # 4. Merchant Active Signals
        for m_sig in merchant.get("signals", []):
            signals.append(OpportunitySignal(
                signal_type="merchant_signal",
                identifier=m_sig,
                strength=6.0,
                recency=7.0,
                business_relevance=8.0,
                actionability=7.0,
                evidence={"signal_raw": m_sig}
            ))

        # 5. Customer Recall / Refill Signal
        if customer and customer.get("state") in ["lapsed_soft", "lapsed_hard"]:
            signals.append(OpportunitySignal(
                signal_type="customer_lapse",
                identifier=f"customer_{customer.get('customer_id')}",
                strength=7.5,
                recency=9.0,
                business_relevance=8.5,
                actionability=9.0,
                evidence={"customer": customer}
            ))

        return signals
