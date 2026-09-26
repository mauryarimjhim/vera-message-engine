from typing import Dict, Any, Optional
from app.models.signal import OpportunitySignal
from app.engine.trigger_engine import TriggerEngine

class MessagePlanner:
    """
    Synthesizes facts and builds structured plans for natural language generation.
    Decides WHAT Vera says.
    """
    def __init__(self):
        self.trigger_engine = TriggerEngine()

    def create_plan(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        opportunity: OpportunitySignal,
        trigger: Optional[Dict[str, Any]] = None,
        customer: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        category_slug = category.get("slug", "dentists")
        merchant_name = merchant.get("identity", {}).get("name", "Merchant")
        owner_name = merchant.get("identity", {}).get("owner_first_name")
        locality = merchant.get("identity", {}).get("locality", "")
        
        # Active offer match
        offers = merchant.get("offers", [])
        active_offer = next((o for o in offers if o.get("status") == "active"), None)
        offer_title = active_offer.get("title") if active_offer else None
        offer_price = active_offer.get("price") if active_offer else None

        # Determine send_as
        is_customer = (trigger and trigger.get("scope") == "customer") or (customer is not None)
        send_as = "merchant_on_behalf" if is_customer else "vera"

        handler_signal, evidence = self.trigger_engine.resolve(
            category, merchant, trigger, customer, opportunity.evidence
        )
        sig_type = handler_signal if trigger else opportunity.signal_type

        plan = {
            "category_slug": category_slug,
            "merchant_name": merchant_name,
            "owner_name": owner_name,
            "locality": locality,
            "send_as": send_as,
            "signal_type": sig_type,
            "evidence": evidence,
            "offer_title": offer_title,
            "offer_price": offer_price,
            "cta_type": "binary_yes_no"
        }

        # Fine-tune cta_type & objective per signal
        if sig_type in ["research_digest", "supply_alert", "curious_ask", "corporate_thali", "planning_intent"]:
            plan["cta_type"] = "open_ended"
        elif sig_type == "recall_due":
            plan["cta_type"] = "multi_choice_slot"
        elif sig_type == "chronic_refill_due":
            plan["cta_type"] = "binary_confirm_cancel"

        return plan
