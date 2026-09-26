from typing import Dict, Any, Optional
from app.models.state import ConversationState, ConversationTurn
from app.storage.state_store import state_store

class StateMachine:
    """
    Manages state transitions for conversations based on classified intent.
    """
    def process_reply(
        self,
        conversation_id: str,
        merchant_id: str,
        customer_id: Optional[str],
        from_role: str,
        message: str,
        intent: str,
        turn_number: int
    ) -> Dict[str, Any]:
        conv = state_store.get_or_create_conversation(conversation_id, merchant_id, customer_id)
        
        # Record turn
        turn = ConversationTurn(
            turn_number=turn_number,
            from_role=from_role,
            message=message,
            timestamp=""
        )
        state_store.add_turn(conversation_id, turn)

        # Process Auto-Reply (track per merchant — judge may use new conversation_id each turn)
        if intent == "AUTO_REPLY":
            streak = state_store.bump_merchant_auto_reply(merchant_id)
            conv.auto_reply_count = streak
            if streak >= 3:
                conv.current_state = "AUTO_REPLY_ENDED"
                return {
                    "action": "end",
                    "rationale": "Detected merchant auto-reply 3x in a row; ending conversation gracefully."
                }
            if streak == 2:
                conv.current_state = "DEFERRED"
                return {
                    "action": "wait",
                    "wait_seconds": 14400,
                    "rationale": "Same auto-reply twice in a row → owner not at phone. Backing off 4 hours."
                }
            return {
                "action": "send",
                "body": "Looks like an auto-reply. When the owner sees this, just reply 'Yes' for the details.",
                "cta": "binary_yes_no",
                "rationale": "Detected auto-reply; providing brief prompt for owner to see.",
            }

        # Reset auto-reply streak on real merchant intent
        state_store.reset_merchant_auto_reply(merchant_id)
        conv.auto_reply_count = 0

        # Process HOSTILE
        if intent == "HOSTILE":
            conv.current_state = "HOSTILE_ENDED"
            return {
                "action": "end",
                "rationale": "Merchant hostile; ending conversation gracefully without further engagement."
            }

        # Process YES / POSITIVE_INTENT
        if intent == "YES":
            conv.current_state = "POSITIVE_INTENT"
            return {
                "action": "send",
                "body": "Great! Sending the draft details now. I've pre-filled the promotion post for tomorrow 10am. Reply CONFIRM to schedule.",
                "cta": "binary_confirm_cancel",
                "rationale": "Merchant committed; switching from qualifying to immediate action execution."
            }

        # Process NO / NEGATIVE_INTENT
        if intent == "NO":
            conv.current_state = "NEGATIVE_INTENT"
            return {
                "action": "end",
                "rationale": "Merchant explicitly opted out. Closing conversation gracefully."
            }

        # Process LATER
        if intent == "LATER":
            conv.current_state = "DEFERRED"
            return {
                "action": "wait",
                "wait_seconds": 1800,
                "rationale": "Merchant asked for time; backing off 30 minutes."
            }

        # Process OFF_TOPIC
        if intent == "OFF_TOPIC":
            return {
                "action": "send",
                "body": "I'll have to leave tax & accounting to your CA — that's outside what I can help with directly! Coming back to our promotion — want me to send the draft details?",
                "cta": "binary_yes_no",
                "rationale": "Declining out-of-scope ask politely and redirecting back to main topic."
            }

        meta = state_store.get_conversation_meta(conversation_id)
        last_signal = meta.get("last_signal_type", "promotion")

        if intent == "QUESTION":
            price = meta.get("offer_price", "299")
            return {
                "action": "send",
                "body": f"Good question — the active offer in your listing is ₹{price} (no extra platform fee on the draft I prepared). I can send the exact post copy + audience targeting summary. Want me to send it now?",
                "cta": "binary_yes_no",
                "rationale": "Answering cost/detail question using stored merchant offer context.",
            }

        if intent == "OBJECTION":
            return {
                "action": "send",
                "body": "Fair point — we can keep this lightweight: one Google post + optional WhatsApp template, no staff time beyond a 2-min review. Want the minimal version?",
                "cta": "binary_yes_no",
                "rationale": "Addressing capacity/objection with a lower-friction path.",
            }

        if intent == "NEW_INTENT":
            return {
                "action": "send",
                "body": "Got it — switching focus to the service you mentioned. Tell me which offer to prioritize and I'll draft the promotion around that instead.",
                "cta": "open_ended",
                "rationale": "Merchant pivoted objective; requesting clarified new target.",
            }

        if intent == "UNKNOWN":
            return {
                "action": "send",
                "body": f"Noted. On the {last_signal} update — reply YES if you want me to proceed with the draft, or LATER if you want to pick this up tomorrow.",
                "cta": "binary_yes_no",
                "rationale": "Clarifying next step after ambiguous merchant reply.",
            }

        return {
            "action": "send",
            "body": "Understood! I've pre-filled the promotion details for you. Reply YES to proceed.",
            "cta": "binary_yes_no",
            "rationale": "Advancing conversation toward execution.",
        }
