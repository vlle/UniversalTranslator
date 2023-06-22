import os
from contextlib import asynccontextmanager
from typing import Union

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import Create
from app.database import engine, init_models, maker
from app.openai import ask_gpt3
from app.pydantic_models import AnimalTranslateInput, AnimalTranslateOutput


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
async def receive_animal_speech(
    received_animal: AnimalTranslateInput,
    session: AsyncSession = Depends(db_connection),
) -> AnimalTranslateOutput:
    animal, text = await ask_gpt3(
        received_animal.text, received_animal.wished_animal_language
    )
    if len(animal) > 30:
        raise HTTPException(status_code=500, detail="Length too big")
    translated_animal = AnimalTranslateOutput(animal=animal, text=text)
    create_object = Create(session)
    await create_object.register_animal_translation(received_animal, translated_animal)
    return translated_animal


@app.get("/api/v1/get_animal")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/api/v1/get_translate")
async def read(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# register animal
# translate animal to human
# translate animal to another animal
# translate human to animal
