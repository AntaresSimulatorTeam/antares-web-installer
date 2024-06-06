"""
This script simulates the behavior of an application and return its current version.
Support script for Windows systems
"""
import asyncio
import contextlib
import os
import signal

from fastapi import FastAPI

TIMEOUT = 10  # duration in seconds of server execution


async def timer(duration: int):
    await asyncio.sleep(duration)
    os.kill(os.getpid(), signal.SIGTERM)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # noinspection PyAsyncCall
    asyncio.create_task(timer(TIMEOUT))  # launch server timeout
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index():
    return {"response": "Successfully running"}
