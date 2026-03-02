from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from auth.router import router as auth_router
from events.router import router as events_router
from clubs.router import router as clubs_router
from registrations.router import router as registrations_router

import os

app = FastAPI(
    title="Multi-Club College Event Portal",
    description="Centralized event discovery and registration for college clubs.",
    version="1.0.0",
)

# CORS — allow local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(clubs_router)
app.include_router(registrations_router)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# Serve the static frontend from /frontend relative to this file's parent
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": str(exc)},
    )
