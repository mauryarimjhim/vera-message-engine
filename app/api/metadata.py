from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/metadata")
async def get_metadata():
    return {
        "team_name": "Team Vera Architect",
        "team_members": ["Senior Backend Architect & AI Systems Specialist"],
        "model": "rule-guided-llm-hybrid",
        "approach": "Stateful Decision Engine: Python Opportunity & Suppression Engine + Category-Aware Composer + Grounding Validator",
        "contact_email": "vera-submission@magicpin.in",
        "version": "1.0.0",
        "submitted_at": "2026-04-26T08:00:00Z"
    }
