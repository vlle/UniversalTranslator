import os
from contextlib import asynccontextmanager
from typing import Annotated, Union

from fastapi import Body, Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import Create, Read
from app.database import engine, init_models, maker
from app.openai import ask_gpt3
from app.pydantic_models import (
    AnimalOutput,
    AnimalTranslateInput,
    AnimalTranslateOutput,
)


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


async def animal_translation(text: str = Body(), wished_animal_language: str = Body()):
    animal, text = await ask_gpt3(text, wished_animal_language)
    return {"animal": animal, "text": text}


@app.post("/api/v1/create_animal")
async def create_animal():
    return {"Hello": "World"}


@app.post("/api/v1/create_translation")
async def create_translation(
    animal_translation: Annotated[dict, Depends(animal_translation)],
    session: AsyncSession = Depends(db_connection),
) -> AnimalTranslateOutput:
    if len(animal_translation["animal"]) > 30:
        raise HTTPException(status_code=500, detail="Length too big")

    translated_animal = AnimalTranslateOutput(
        id=-1, animal=animal_translation["animal"], text=animal_translation["text"]
    )
    create_unit = Create(session)
    translated_animal.id = await create_unit.register_animal_translation(
        AnimalTranslateInput(
            wished_animal_language=animal_translation["animal"],
            text=animal_translation["text"],
        ),
        translated_animal,
    )
    return translated_animal


@app.get("/api/v1/get_animal")
async def get_animal(id: int, session: AsyncSession = Depends(db_connection)):
    read_unit = Read(session)
    animal = await read_unit.get_animal(id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal


@app.get("/api/v1/get_all_animals")
async def get_all_animals(session: AsyncSession = Depends(db_connection)):
    read_unit = Read(session)
    animals = await read_unit.get_all_animals()
    animals_output: list[AnimalOutput] = [
        AnimalOutput(id=animal.id, language=animal.language, name=animal.name)
        for animal in animals
    ]
    return animals_output


@app.get("/api/v1/get_translation")
async def get_translate(id: int, session: AsyncSession = Depends(db_connection)):
    read_unit = Read(session)
    translate = await read_unit.get_animal_speech(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translate


@app.delete("/api/v1/delete_translation")
async def delete_translate(id: int, session: AsyncSession = Depends(db_connection)):
    read_unit = Read(session)
    translate = await read_unit.get_animal_speech(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translate


@app.delete("/api/v1/delete_animal")
async def delete_animal(id: int, session: AsyncSession = Depends(db_connection)):
    read_unit = Read(session)
    translate = await read_unit.get_animal_speech(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translate
