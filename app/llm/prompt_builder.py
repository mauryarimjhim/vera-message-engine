import json
from typing import Dict, Any, Optional

class PromptBuilder:
    """
    Builds strict prompts for LLM Natural Language Layer.
    Forces deterministic outputs (temp=0) and enforces context grounding.
    """
    SYSTEM_PROMPT = """You are Vera, magicpin's merchant growth assistant in India.
Your job is to compose the NEXT BEST WhatsApp message for a merchant or customer.

CRITICAL RULES:
1. Grounded: Use ONLY facts, numbers, dates, and prices provided in the context. DO NOT fabricate.
2. Voice match: Tone MUST match the category (Dentists = peer clinical, Salons = warm practical, Restaurants = operator-to-operator, Gyms = coaching, Pharmacies = trustworthy precise).
3. Specificity: Anchor on concrete numbers, dates, source citations, or offer prices.
4. Single Primary CTA: Exactly one clear call-to-action in the final sentence.
5. Concise & Natural: Keep message short, conversational, and direct. Avoid generic marketing jargon.
6. NO URLs: Never output HTTP or HTTPS URLs.
7. Return JSON ONLY with keys "body", "cta", "send_as", "suppression_key", "rationale".
"""

    def build_prompt(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        plan: Dict[str, Any],
        trigger: Optional[Dict[str, Any]] = None,
        customer: Optional[Dict[str, Any]] = None
    ) -> str:
        prompt_dict = {
            "category": category.get("slug"),
            "merchant": merchant.get("identity", {}).get("name"),
            "owner": merchant.get("identity", {}).get("owner_first_name"),
            "locality": merchant.get("identity", {}).get("locality"),
            "signal_type": plan.get("signal_type"),
            "evidence": plan.get("evidence"),
            "active_offer": plan.get("offer_title"),
            "offer_price": plan.get("offer_price"),
            "send_as": plan.get("send_as"),
            "target_cta": plan.get("cta_type"),
            "trigger_payload": trigger.get("payload") if trigger else None,
            "customer_name": customer.get("identity", {}).get("name") if customer else None
        }
        return f"COMPOSE MESSAGE FROM THIS PLAN:\n{json.dumps(prompt_dict, indent=2)}"
