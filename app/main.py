from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, metadata, context, tick, reply

app = FastAPI(
    title="Vera — AI Merchant Growth Message Engine",
    description="Stateful AI Message Engine for magicpin merchant engagement.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router)
app.include_router(metadata.router)
app.include_router(context.router)
app.include_router(tick.router)
app.include_router(reply.router)

@app.get("/")
async def root():
    return {
        "service": "Vera AI Message Engine",
        "status": "online",
        "documentation": "/docs"
    }
