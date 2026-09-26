from typing import Dict, Any, Optional
from app.categories import get_category_handler

class DeterministicFallbackEngine:
    """
    Produces category-specific, grounded fallback messages whenever LLM is unavailable or fails validation.
    Ensures 100% operational uptime and strict determinism.
    """
    def generate(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        trigger: Optional[Dict[str, Any]],
        customer: Optional[Dict[str, Any]],
        plan: Dict[str, Any]
    ) -> Dict[str, str]:
        category_slug = category.get("slug", "dentists")
        handler = get_category_handler(category_slug)

        merchant_name = merchant.get("identity", {}).get("name", "Merchant")
        owner_name = merchant.get("identity", {}).get("owner_first_name")
        signal_type = plan.get("signal_type", "default")
        evidence = plan.get("evidence", {})

        # Enrich evidence with active offer if available
        if "price" not in evidence and plan.get("offer_price"):
            evidence["price"] = plan.get("offer_price")
        if "offer" not in evidence and plan.get("offer_title"):
            evidence["offer"] = plan.get("offer_title")

        # Specific trigger payload extractions
        if trigger and trigger.get("payload"):
            trg_pay = trigger["payload"]
            if "query" in trg_pay: evidence["query"] = trg_pay["query"]
            if "count" in trg_pay: evidence["count"] = trg_pay["count"]
            if "title" in trg_pay: evidence["title"] = trg_pay["title"]
            if "source" in trg_pay: evidence["source"] = trg_pay["source"]

        if customer and customer.get("identity"):
            evidence["customer_name"] = customer["identity"].get("name", "Patient")

        res = handler.generate_fallback_message(
            merchant_name=merchant_name,
            owner_name=owner_name,
            signal_type=signal_type,
            evidence=evidence,
            cta_type=plan.get("cta_type", "binary_yes_no")
        )
        return res
