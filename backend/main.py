"""RaceControl FastAPI application entry point."""

import logging
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config import settings

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


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


@app.on_event("startup")
async def startup_event() -> None:
    """Log startup."""
    logger.info(f"Starting {settings.title} v{settings.version}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log shutdown."""
    logger.info(f"Shutting down {settings.title}")


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
