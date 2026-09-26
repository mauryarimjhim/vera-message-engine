"""
magicpin AI Challenge — Candidate Bot Entrypoint (bot.py)
=========================================================
Exposes the canonical composition function and multi-turn respondent.
"""

from typing import Dict, Any, Optional
from app.engine.composer import compose as core_compose
from app.engine.intent_engine import IntentEngine
from app.engine.state_machine import StateMachine

intent_engine = IntentEngine()
state_machine = StateMachine()

def compose(category: Dict[str, Any], merchant: Dict[str, Any], trigger: Dict[str, Any], customer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Canonical composition entrypoint for magicpin evaluation.
    Returns dict with keys: body, cta, send_as, suppression_key, rationale.
    """
    res = core_compose(category, merchant, trigger, customer)
    if not res:
        return {
            "body": "",
            "cta": "none",
            "send_as": "vera",
            "suppression_key": trigger.get("suppression_key", "suppressed"),
            "rationale": "No actionable opportunity or message suppressed.",
        }
    return res

def respond(state: Dict[str, Any], merchant_message: str) -> Dict[str, Any]:
    """
    Multi-turn conversation respondent entrypoint.
    """
    conv_id = state.get("conversation_id", "conv_default")
    merchant_id = state.get("merchant_id", "m_default")
    customer_id = state.get("customer_id")
    turns = state.get("turns", [])
    turn_num = len(turns) + 1

    intent = intent_engine.classify_intent(merchant_message, turns)
    return state_machine.process_reply(
        conversation_id=conv_id,
        merchant_id=merchant_id,
        customer_id=customer_id,
        from_role="merchant",
        message=merchant_message,
        intent=intent,
        turn_number=turn_num
    )
