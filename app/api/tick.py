from fastapi import APIRouter
from typing import List
from app.models.message import TickRequest, TickResponse, TickAction
from app.storage.context_store import context_store
from app.storage.state_store import state_store
from app.engine.composer import composer

router = APIRouter()
MAX_ACTIONS_PER_TICK = 20

@router.post("/v1/tick", response_model=TickResponse)
async def handle_tick(body: TickRequest):
    actions: List[TickAction] = []

    for trg_id in body.available_triggers:
        if len(actions) >= MAX_ACTIONS_PER_TICK:
            break
        # Load trigger context
        trg_entry = context_store.get_context_entry("trigger", trg_id)
        if not trg_entry:
            continue
        trigger = trg_entry["payload"]
        context_ver = trg_entry.get("version", 1)

        merchant_id = trigger.get("merchant_id")
        customer_id = trigger.get("customer_id")

        if not merchant_id:
            continue

        # Load merchant context
        m_entry = context_store.get_context_entry("merchant", merchant_id)
        if not m_entry:
            continue
        merchant = m_entry["payload"]

        # Load category context
        cat_slug = merchant.get("category_slug", "dentists")
        c_entry = context_store.get_context_entry("category", cat_slug)
        category = c_entry["payload"] if c_entry else {"slug": cat_slug}

        # Load optional customer context
        customer = None
        if customer_id:
            cust_entry = context_store.get_context_entry("customer", customer_id)
            if cust_entry:
                customer = cust_entry["payload"]

        # Compose message via Vera Decision Engine
        composed = composer.compose(
            category=category,
            merchant=merchant,
            trigger=trigger,
            customer=customer,
            context_version=context_ver
        )

        if composed:
            conv_id = f"conv_{merchant_id}_{trg_id}"
            actions.append(TickAction(
                conversation_id=conv_id,
                merchant_id=merchant_id,
                customer_id=customer_id,
                send_as=composed.get("send_as", "vera"),
                trigger_id=trg_id,
                template_name="vera_opportunity_v1",
                template_params=[merchant.get("identity", {}).get("name", ""), "opportunity"],
                body=composed.get("body", ""),
                cta=composed.get("cta", "binary_yes_no"),
                suppression_key=composed.get("suppression_key", f"supp_{trg_id}"),
                rationale=composed.get("rationale", "Composed from Vera decision engine.")
            ))
            active_offer = next((o for o in merchant.get("offers", []) if o.get("status") == "active"), None)
            state_store.set_conversation_meta(conv_id, {
                "merchant_id": merchant_id,
                "trigger_id": trg_id,
                "last_signal_type": trigger.get("kind"),
                "offer_price": active_offer.get("title", "").split("₹")[-1].strip() if active_offer and "₹" in active_offer.get("title", "") else "299",
            })

    return TickResponse(actions=actions)
