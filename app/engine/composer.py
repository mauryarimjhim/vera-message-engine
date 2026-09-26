from typing import Dict, Any, Optional
from app.engine.opportunity_engine import OpportunityEngine
from app.engine.suppression_engine import SuppressionEngine
from app.engine.message_planner import MessagePlanner
from app.engine.validator import ResponseValidator
from app.llm.client import LLMClient
from app.storage.state_store import state_store

class VeraComposer:
    """
    Core composer pipeline for Vera:
    Structured Context -> Opportunity Engine -> Suppression Engine -> Message Planner -> LLM/Fallback Layer -> Response Validator
    """
    def __init__(self):
        self.opportunity_engine = OpportunityEngine()
        self.suppression_engine = SuppressionEngine()
        self.message_planner = MessagePlanner()
        self.llm_client = LLMClient()
        self.validator = ResponseValidator()

    def compose(
        self,
        category: Dict[str, Any],
        merchant: Dict[str, Any],
        trigger: Optional[Dict[str, Any]] = None,
        customer: Optional[Dict[str, Any]] = None,
        context_version: int = 1
    ) -> Optional[Dict[str, Any]]:
        merchant_id = merchant.get("merchant_id", "m_unknown")
        category_slug = category.get("slug", "dentists")

        # 1. Select Dominant Opportunity
        opportunity = self.opportunity_engine.select_dominant_opportunity(
            category, merchant, trigger, customer
        )
        if not opportunity:
            return None

        # 2. Check Suppression Engine
        should_suppress, supp_key, supp_reason = self.suppression_engine.should_suppress(
            merchant_id=merchant_id,
            category_slug=category_slug,
            opportunity=opportunity,
            trigger=trigger,
            context_version=context_version
        )
        if should_suppress:
            return None

        # 3. Create Message Plan
        plan = self.message_planner.create_plan(
            category, merchant, opportunity, trigger, customer
        )

        # 4. Generate Natural Language
        composed = self.llm_client.compose_message(
            category, merchant, plan, trigger, customer
        )

        # 5. Validate Response
        is_valid, validation_errors = self.validator.validate(
            body=composed.get("body", ""),
            cta=composed.get("cta", "binary_yes_no"),
            category_slug=category_slug,
            context_facts={}
        )

        if not is_valid:
            # Fall back to deterministic fallback
            fallback_res = self.llm_client.fallback_engine.generate(
                category, merchant, trigger, customer, plan
            )
            composed["body"] = fallback_res["body"]
            composed["cta"] = fallback_res["cta"]
            composed["rationale"] = f"Validated fallback used (validation note: {', '.join(validation_errors)})"

        composed["suppression_key"] = supp_key
        composed["send_as"] = plan.get("send_as", "vera")
        composed["rationale"] = composed.get(
            "rationale",
            f"Proactive outreach for {plan.get('signal_type')} grounded in merchant + trigger context.",
        )

        # 6. Record suppression key
        state_store.suppress_key(supp_key)

        return composed

composer = VeraComposer()

def compose(category: Dict[str, Any], merchant: Dict[str, Any], trigger: Optional[Dict[str, Any]] = None, customer: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Canonical compose function conforming to Challenge Brief §7.1."""
    return composer.compose(category, merchant, trigger, customer)
