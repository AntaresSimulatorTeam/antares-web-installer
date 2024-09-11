"""
Simulate AntaREST server for testing purposes.
"""

import asyncio
import contextlib
import os
import signal
import typing as t

from fastapi import FastAPI

MAX_DELAY = 10


async def stop_server():
    """Kill the server after a delay to avoid blocking the tests."""
    await asyncio.sleep(MAX_DELAY)
    os.kill(os.getpid(), signal.SIGTERM)


@contextlib.asynccontextmanager
async def lifespan(_unused_app: FastAPI) -> t.AsyncGenerator[None, None]:
    """Context manager to stop the server after a delay."""
    # noinspection PyAsyncCall
    asyncio.create_task(stop_server())
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    """
    Endpoint to check that the server is ready.
    It reproduces the behavior of the `/health` endpoint of the AntaREST server.
    """
    return {"status": "available"}
