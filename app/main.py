from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Body, Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import Create, Delete, Read, Update
from app.database import engine, init_models, maker
from app.openai import ask_gpt3
from app.pydantic_models import (
    LanguageOutput,
    SpeechOutput,
    TranslateInput,
    TranslateOutput,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models(engine)
    yield


application = FastAPI(lifespan=lifespan)


async def db_connection():
    db = maker()
    try:
        yield db
    finally:
        await db.close()


async def animal_translation(text: str = Body(), wished_animal_language: str = Body()):
    animal, text = await ask_gpt3(text, wished_animal_language)
    return {"animal": animal, "text": text}


@application.post("/api/v1/create_animal")
async def create_animal():
    return {"Hello": "World"}


@application.post(
    "/api/v1/create_translation",
    status_code=status.HTTP_201_CREATED,
    description="Create animal translation",
    responses={
        status.HTTP_507_INSUFFICIENT_STORAGE: {"description": "Length too big"},
        status.HTTP_201_CREATED: {"model": TranslateOutput},
    },
)
async def create_translation(
    animal_translation: Annotated[dict, Depends(animal_translation)],
    session: AsyncSession = Depends(db_connection),
) -> TranslateOutput:
    if len(animal_translation["animal"]) > 30:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE, detail="Length too big"
        )

    translated_animal = TranslateOutput(
        id=-1,
        translated_from=animal_translation["animal"],
        text=animal_translation["text"],
    )
    create_unit = Create(session)
    translated_animal.id = await create_unit.register_translation(
        TranslateInput(
            translate_to_language=animal_translation["animal"],
            text=animal_translation["text"],
        ),
        translated_animal,
    )
    return translated_animal


@application.get(
    "/api/v1/get_animal",
    status_code=status.HTTP_200_OK,
    description="Get animal by id",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Animal not found"},
        status.HTTP_200_OK: {"model": LanguageOutput},
    },
)
async def get_animal(
    id: int, session: AsyncSession = Depends(db_connection)
) -> LanguageOutput:
    read_unit = Read(session)
    language = await read_unit.get_language(id)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found"
        )

    return LanguageOutput(id=language.id, language=language.name)


@application.get(
    "/api/v1/get_all_languages",
    status_code=status.HTTP_200_OK,
    description="Get all languages",
    responses={status.HTTP_200_OK: {"model": list[LanguageOutput]}},
)
async def get_all_animals(
    session: AsyncSession = Depends(db_connection),
) -> list[LanguageOutput]:
    read_unit = Read(session)
    languages = await read_unit.get_all_languages()
    animals_output: list[LanguageOutput] = [
        LanguageOutput(id=language.id, language=language.name) for language in languages
    ]
    return animals_output


@application.get("/api/v1/get_translation")
async def get_translate(
    id: int, session: AsyncSession = Depends(db_connection)
) -> SpeechOutput:
    read_unit = Read(session)
    translate = await read_unit.get_translation(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Translation not found")

    return SpeechOutput(
        id=translate.id,
        origin_language_id=translate.origin_animal_id,
        translated_language_id=translate.translated_animal_id,
        text=translate.text,
        translated_text=translate.translated_text,
    )


@application.put("/api/v1/delete_translation")
async def update_translate(id: int, session: AsyncSession = Depends(db_connection)):
    read_unit = Read(session)
    translate = await read_unit.get_translation(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translate


@application.put("/api/v1/delete_animal")
async def update_animal(id: int, session: AsyncSession = Depends(db_connection)):
    read_unit = Update(session)
    translate = await read_unit.update_animal(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Animal not found")
    return translate


@application.delete("/api/v1/delete_translation")
async def delete_translate(id: int, session: AsyncSession = Depends(db_connection)):
    delete_unit = Delete(session)
    deleted_id = await delete_unit.delete_animal_speech(id)
    if not deleted_id:
        raise HTTPException(status_code=404, detail="Translation not found")


@application.delete("/api/v1/delete_animal")
async def delete_animal(id: int, session: AsyncSession = Depends(db_connection)):
    delete_unit = Delete(session)
    deleted_id = await delete_unit.delete_animal(id)
    if not deleted_id:
        raise HTTPException(status_code=404, detail="Animal not found")
