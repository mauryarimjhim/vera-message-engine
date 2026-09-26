from fastapi import APIRouter
from app.models.message import ReplyRequest, ReplyResponse
from app.engine.intent_engine import IntentEngine
from app.engine.state_machine import StateMachine

router = APIRouter()
intent_engine = IntentEngine()
state_machine = StateMachine()

@router.post("/v1/reply", response_model=ReplyResponse)
async def handle_reply(body: ReplyRequest):
    intent = intent_engine.classify_intent(body.message)
    res = state_machine.process_reply(
        conversation_id=body.conversation_id,
        merchant_id=body.merchant_id or "m_unknown",
        customer_id=body.customer_id,
        from_role=body.from_role,
        message=body.message,
        intent=intent,
        turn_number=body.turn_number
    )

    return ReplyResponse(
        action=res["action"],
        body=res.get("body"),
        cta=res.get("cta"),
        wait_seconds=res.get("wait_seconds"),
        rationale=res.get("rationale", "Processed reply turn.")
    )
