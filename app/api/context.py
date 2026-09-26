from fastapi import APIRouter, Response, status
from app.models.context import ContextPushRequest, ContextPushResponse
from app.storage.context_store import context_store

router = APIRouter()

@router.post("/v1/context", response_model=ContextPushResponse)
async def push_context(body: ContextPushRequest, response: Response):
    valid_scopes = ["category", "merchant", "customer", "trigger"]
    if body.scope not in valid_scopes:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ContextPushResponse(
            accepted=False,
            reason="invalid_scope",
            details=f"Scope '{body.scope}' is invalid. Allowed: {valid_scopes}"
        )

    accepted, ack_or_reason, cur_ver = context_store.put_context(
        scope=body.scope,
        context_id=body.context_id,
        version=body.version,
        payload=body.payload
    )

    if not accepted:
        response.status_code = status.HTTP_409_CONFLICT
        return ContextPushResponse(
            accepted=False,
            reason="stale_version",
            current_version=cur_ver
        )

    return ContextPushResponse(
        accepted=True,
        ack_id=ack_or_reason,
        stored_at=context_store.get_context_entry(body.scope, body.context_id).get("updated_at")
    )
