import time
from fastapi import APIRouter
from app.storage.context_store import context_store

router = APIRouter()
START_TIME = time.time()

@router.get("/v1/healthz")
async def get_healthz():
    uptime = int(time.time() - START_TIME)
    counts = context_store.get_counts()
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "contexts_loaded": counts
    }
