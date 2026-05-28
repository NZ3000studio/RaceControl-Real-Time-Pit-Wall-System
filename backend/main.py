"""RaceControl FastAPI application entry point."""

import asyncio
import logging
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from app.websocket.server import telemetry_websocket_handler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
)

# Configure CORS for frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for telemetry streaming.

    Path: ws://localhost:8000/ws/telemetry
    """
    await telemetry_websocket_handler(websocket)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize services on startup."""
    logger.info(f"Starting {settings.title} v{settings.version}")

    # Start telemetry broadcaster
    from app.websocket.broadcaster import get_broadcaster

    broadcaster = await get_broadcaster()
    await broadcaster.start()

    # Start telemetry pipeline (reads AC shared memory)
    from app.telemetry.pipeline import get_pipeline

    pipeline = await get_pipeline()
    # Note: Pipeline starts in background, doesn't block
    asyncio.create_task(pipeline.start())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up services on shutdown."""
    logger.info(f"Shutting down {settings.title}")

    # Stop telemetry broadcaster
    from app.websocket.broadcaster import get_broadcaster

    try:
        broadcaster = await get_broadcaster()
        await broadcaster.stop()
    except Exception as e:
        logger.error(f"Error stopping broadcaster: {e}")

    # Stop telemetry pipeline
    from app.telemetry.pipeline import get_pipeline

    try:
        pipeline = await get_pipeline()
        await pipeline.stop()
    except Exception as e:
        logger.error(f"Error stopping pipeline: {e}")


def main() -> None:
    """Run the application."""
    logger.info(
        f"Starting uvicorn server on {settings.host}:{settings.port} "
        f"(reload={settings.reload})"
    )
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
