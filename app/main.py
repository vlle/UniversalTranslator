import os
from contextlib import asynccontextmanager
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, init_models, maker

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models(engine)
    yield


async def db_connection():
    db = maker()
    try:
        yield db
    finally:
        await db.close()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# register animal
# translate animal to human
# translate animal to another animal
# translate human to animal
