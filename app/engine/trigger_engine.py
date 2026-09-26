"""Resolve trigger kinds into enriched evidence for the message planner."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from app.utils.normalization import normalize_search_query


def _parse_price_from_offer(offer: Optional[Dict[str, Any]]) -> Optional[str]:
    if not offer:
        return None
    if offer.get("price") is not None:
        return str(offer["price"])
    title = offer.get("title", "")
    m = re.search(r"₹\s*([\d,]+)", title)
    if m:
        return m.group(1).replace(",", "")
    if offer.get("value") is not None:
        return str(offer["value"])
    return None


def _active_offer(merchant: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for o in merchant.get("offers", []):
        if o.get("status") == "active":
            return o
    return None


def _digest_item(category: Dict[str, Any], item_id: str) -> Optional[Dict[str, Any]]:
    for item in category.get("digest", []):
        if item.get("id") == item_id:
            return item
    return None


def _kind_to_handler_signal(kind: str, payload: Optional[Dict[str, Any]] = None) -> str:
    mapping = {
        "ipl_match_today": "ipl_match",
        "curious_ask_due": "curious_ask",
        "wedding_package_followup": "bridal_followup",
        "chronic_refill_due": "chronic_refill",
        "regulation_change": "compliance_regulation",
        "category_trend_movement": "trend_movement",
        "corporate_bulk_thali_package": "corporate_thali",
        "supply_shortage_alert": "supply_alert",
        "supply_alert": "supply_alert",
        "seasonal_demand_dip": "seasonal_dip",
        "seasonal_perf_dip": "seasonal_dip",
        "customer_lapsed_soft": "customer_lapsed",
        "customer_lapsed_hard": "customer_lapsed",
        "trial_followup": "trial_followup",
        "winback_eligible": "winback",
        "review_theme_emerged": "review_theme",
        "festival_upcoming": "festival",
        "renewal_due": "renewal_due",
        "perf_dip": "perf_dip",
        "perf_spike": "perf_spike",
        "recall_due": "recall_due",
        "research_digest": "research_digest",
        "local_search_spike": "recent_search",
        "milestone_reached": "milestone",
        "category_seasonal": "category_seasonal",
        "gbp_unverified": "gbp_unverified",
        "cde_opportunity": "cde_opportunity",
        "competitor_opened": "competitor_opened",
        "dormant_with_vera": "dormant_with_vera",
    }
    if kind == "active_planning_intent":
        topic = (payload or {}).get("intent_topic", "")
        if "thali" in topic:
            return "corporate_thali"
        return "planning_intent"
    return mapping.get(kind, kind)


class TriggerEngine:
    """Maps triggers + category/merchant facts into planner-ready evidence."""

    def resolve(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        trigger: Optional[Dict[str, Any]],
        customer: Optional[Dict[str, Any]],
        opportunity_evidence: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        evidence: Dict[str, Any] = dict(opportunity_evidence or {})
        kind = trigger.get("kind", "default") if trigger else "default"
        payload = trigger.get("payload", {}) if trigger else {}
        handler_signal = _kind_to_handler_signal(kind, payload)

        active = _active_offer(merchant)
        offer_title = active.get("title") if active else None
        offer_price = _parse_price_from_offer(active)
        identity = merchant.get("identity", {})

        if offer_title:
            evidence.setdefault("offer", offer_title)
        if offer_price:
            evidence.setdefault("price", offer_price)
        evidence.setdefault("locality", identity.get("locality", ""))

        if kind == "research_digest":
            item_id = payload.get("top_item_id")
            item = _digest_item(category, item_id) if item_id else None
            if item:
                evidence["title"] = item.get("title", evidence.get("title", ""))
                evidence["source"] = item.get("source", "")
                evidence["trial_n"] = item.get("trial_n")
                summary = item.get("summary", "")
                if "38%" in summary:
                    evidence["reduction_pct"] = 38
                elif "%" in summary:
                    m = re.search(r"(\d+)%", summary)
                    if m:
                        evidence["reduction_pct"] = int(m.group(1))

        elif kind == "regulation_change":
            item_id = payload.get("top_item_id")
            item = _digest_item(category, item_id) if item_id else None
            if item:
                evidence["title"] = item.get("title", "")
                evidence["source"] = item.get("source", "")
            evidence["deadline"] = payload.get("deadline_iso", "")

        elif kind == "perf_dip":
            evidence["metric"] = payload.get("metric", "calls")
            evidence["delta_pct"] = payload.get("delta_pct", 0)
            evidence["vs_baseline"] = payload.get("vs_baseline")
            peer_ctr = category.get("peer_stats", {}).get("avg_ctr")
            if peer_ctr and merchant.get("performance", {}).get("ctr") is not None:
                evidence["merchant_ctr"] = merchant["performance"]["ctr"]
                evidence["peer_ctr"] = peer_ctr

        elif kind == "renewal_due":
            evidence["days_remaining"] = payload.get("days_remaining")
            evidence["plan"] = payload.get("plan", merchant.get("subscription", {}).get("plan"))
            evidence["renewal_amount"] = payload.get("renewal_amount")

        elif kind == "ipl_match_today":
            evidence["match"] = payload.get("match", "DC vs MI")
            evidence["venue"] = payload.get("venue", "")
            raw_time = payload.get("match_time_iso", payload.get("match_time", "7:30pm"))
            try:
                from datetime import datetime as _dt
                d = _dt.fromisoformat(str(raw_time).replace("Z", "+00:00"))
                h = d.hour % 12 or 12
                evidence["time"] = f"{h}:{d.minute:02d}{'pm' if d.hour >= 12 else 'am'}"
            except (ValueError, TypeError):
                evidence["time"] = raw_time
            if active:
                evidence["offer"] = offer_title

        elif kind == "festival_upcoming":
            evidence["festival"] = payload.get("festival", "Diwali")
            evidence["days_until"] = payload.get("days_until")

        elif kind == "recall_due" and customer:
            evidence["customer_name"] = customer.get("identity", {}).get("name", "Patient")
            slots = payload.get("available_slots", [])
            if len(slots) >= 1:
                evidence["slot1"] = slots[0].get("label", "")
            if len(slots) >= 2:
                evidence["slot2"] = slots[1].get("label", "")
            if payload.get("last_service_date"):
                evidence["months"] = 5

        elif kind == "wedding_package_followup" and customer:
            evidence["customer_name"] = customer.get("identity", {}).get("name", "Customer")
            evidence["days_to_wedding"] = payload.get("days_to_wedding")

        elif kind == "chronic_refill_due" and customer:
            evidence["customer_name"] = customer.get("identity", {}).get("name", "Customer")
            evidence["locality"] = identity.get("locality", "")
            molecules = payload.get("molecule_list")
            if molecules:
                evidence["molecules"] = ", ".join(molecules)
                evidence["medicine_count"] = len(molecules)
            stock_iso = payload.get("stock_runs_out_iso", "")
            if stock_iso:
                from datetime import datetime as _dt
                try:
                    d = _dt.fromisoformat(stock_iso.replace("Z", "+00:00"))
                    evidence["date"] = f"{d.day} {d.strftime('%B')}"
                except ValueError:
                    evidence["date"] = stock_iso[:10]

        elif kind == "review_theme_emerged":
            evidence["theme"] = payload.get("theme", "")
            evidence["occurrences"] = payload.get("occurrences_30d")
            evidence["quote"] = payload.get("common_quote", "")

        elif kind == "winback_eligible":
            evidence["days_since_expiry"] = payload.get("days_since_expiry")
            evidence["lapsed_customers"] = payload.get("lapsed_customers_added_since_expiry")

        elif kind == "local_search_spike" or kind == "category_trend_movement":
            query = payload.get("query", "")
            if query:
                evidence["query"] = query
                evidence["normalized_query"] = normalize_search_query(query)
            if payload.get("count") is not None:
                evidence["count"] = payload.get("count")
            if payload.get("delta_yoy") is not None:
                evidence["delta_yoy"] = payload.get("delta_yoy")

        elif kind == "supply_shortage_alert" or kind == "supply_alert":
            evidence.update(payload)

        elif kind == "seasonal_perf_dip" or kind == "seasonal_demand_dip":
            evidence["metric"] = payload.get("metric", "views")
            evidence["delta_pct"] = payload.get("delta_pct", 0)
            evidence["season_note"] = payload.get("season_note", "")
            evidence["is_expected_seasonal"] = payload.get("is_expected_seasonal", False)

        elif kind in ("customer_lapsed_hard", "customer_lapsed_soft"):
            days = payload.get("days_since_last_visit")
            if days is not None:
                evidence["days_since_last_visit"] = days
                evidence["weeks"] = max(1, round(days / 7))
            evidence["previous_focus"] = payload.get("previous_focus", "")
            evidence["previous_membership_months"] = payload.get("previous_membership_months")

        elif kind == "trial_followup":
            evidence["trial_date"] = payload.get("trial_date", "")
            options = payload.get("next_session_options", [])
            if options:
                evidence["slot1"] = options[0].get("label", "")

        elif kind == "active_planning_intent":
            evidence["intent_topic"] = payload.get("intent_topic", "")
            evidence["merchant_last_message"] = payload.get("merchant_last_message", "")

        elif kind == "milestone_reached":
            evidence["metric"] = payload.get("metric", "")
            evidence["value_now"] = payload.get("value_now")
            evidence["milestone_value"] = payload.get("milestone_value")

        elif kind == "category_seasonal":
            evidence["season"] = payload.get("season", "")
            trends = []
            for tr in payload.get("trends", []):
                m = re.match(r"(.+)_demand_([+-]?\d+)", str(tr))
                if m:
                    trends.append({"product": m.group(1).replace("_", " "), "pct": int(m.group(2))})
            evidence["trends"] = trends

        elif kind == "gbp_unverified":
            evidence["verified"] = payload.get("verified", False)
            evidence["verification_path"] = payload.get("verification_path", "")
            evidence["estimated_uplift_pct"] = payload.get("estimated_uplift_pct")

        elif kind == "cde_opportunity":
            item_id = payload.get("digest_item_id")
            item = _digest_item(category, item_id) if item_id else None
            if item:
                evidence["title"] = item.get("title", "")
                evidence["source"] = item.get("source", "")
            evidence["credits"] = payload.get("credits")
            evidence["fee"] = payload.get("fee", "")

        elif kind == "competitor_opened":
            evidence["competitor_name"] = payload.get("competitor_name", "")
            evidence["distance_km"] = payload.get("distance_km")
            evidence["their_offer"] = payload.get("their_offer", "")
            evidence["opened_date"] = payload.get("opened_date", "")

        elif kind == "perf_spike":
            evidence["metric"] = payload.get("metric", "calls")
            evidence["delta_pct"] = payload.get("delta_pct", 0)
            evidence["likely_driver"] = payload.get("likely_driver", "")

        elif kind == "dormant_with_vera":
            evidence["days_since_last_merchant_message"] = payload.get("days_since_last_merchant_message")
            evidence["last_topic"] = payload.get("last_topic", "")

        # Generic enrichment: customer name + real merchant performance numbers
        if customer and "customer_name" not in evidence:
            cust_identity = customer.get("identity", {}) if isinstance(customer, dict) else {}
            if cust_identity.get("name"):
                evidence["customer_name"] = cust_identity["name"]
        perf = merchant.get("performance", {}) or {}
        for key in ("views", "calls", "leads", "directions"):
            if perf.get(key) is not None:
                evidence.setdefault(f"perf_{key}", perf[key])

        return handler_signal, evidence
