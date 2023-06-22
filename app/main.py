import os
from contextlib import asynccontextmanager
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, init_models, maker
from app.openai import ask_gpt3


class AnimalTranslateInput(BaseModel):
    animal: str
    text: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models(engine)
    yield


app = FastAPI(lifespan=lifespan)


async def db_connection():
    db = maker()
    try:
        yield db
    finally:
        await db.close()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/api/v1/create_animal")
async def receive_animal():
    return {"Hello": "World"}


@app.post("/api/v1/get_animal_translate")
async def receive_animal_speech(received_animal: AnimalTranslateInput):
    answer = await ask_gpt3(received_animal.text, received_animal.animal)
    return answer


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# register animal
# translate animal to human
# translate animal to another animal
# translate human to animal
