from contextlib import asynccontextmanager
from typing import Annotated, Any, Tuple

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


async def translation(input: TranslateInput):
    language, text = await ask_gpt3(input.text, input.translate_to_language)
    return (
        TranslateOutput(id=-1, translated_from=language, text=text),
        input.translate_to_language,
    )


@application.post("/api/v1/create_language")
async def create_language():
    return {"Hello": "World"}


@application.post(
    "/api/v1/create_translation",
    status_code=status.HTTP_201_CREATED,
    description="Create language translation",
    responses={
        status.HTTP_507_INSUFFICIENT_STORAGE: {"description": "Length too big"},
        status.HTTP_201_CREATED: {"model": TranslateOutput},
    },
)
async def create_translation(
    translation_data: Tuple[TranslateOutput, Any] = Depends(translation),
    session: AsyncSession = Depends(db_connection),
) -> TranslateOutput:
    translation, translated_to = translation_data[0], translation_data[1]
    if len(translation.translated_from) > 30:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE, detail="Length too big"
        )

    create_unit = Create(session)
    translation.id = await create_unit.register_translation(
        TranslateInput(
            translate_to_language=translated_to,
            text=translation.text,
        ),
        translation,
    )
    return translation


@application.get(
    "/api/v1/get_language",
    status_code=status.HTTP_200_OK,
    description="Get language by id",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Language not found"},
        status.HTTP_200_OK: {"model": LanguageOutput},
    },
)
async def get_language(
    id: int, session: AsyncSession = Depends(db_connection)
) -> LanguageOutput:
    read_unit = Read(session)
    language = await read_unit.get_language(id)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Language not found"
        )

    return LanguageOutput(id=language.id, language=language.name)


@application.get(
    "/api/v1/get_all_languages",
    status_code=status.HTTP_200_OK,
    description="Get all languages",
    responses={status.HTTP_200_OK: {"model": list[LanguageOutput]}},
)
async def get_all_languages(
    session: AsyncSession = Depends(db_connection),
) -> list[LanguageOutput]:
    read_unit = Read(session)
    languages = await read_unit.get_all_languages()
    languages_output: list[LanguageOutput] = [
        LanguageOutput(id=language.id, language=language.name) for language in languages
    ]
    return languages_output


@application.get(
    "/api/v1/get_translation",
    status_code=status.HTTP_200_OK,
    description="Get translation by id",
    responses={
        status.HTTP_200_OK: {"model": SpeechOutput},
        status.HTTP_404_NOT_FOUND: {"description": "Translation not found"},
    },
)
async def get_translate(
    id: int, session: AsyncSession = Depends(db_connection)
) -> SpeechOutput:
    read_unit = Read(session)
    translate = await read_unit.get_translation(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Translation not found")

    return SpeechOutput(
        id=translate.id,
        origin_language_id=translate.origin_language,
        translated_language_id=translate.translated_language,
        text=translate.text,
        translated_text=translate.translated_text,
    )


@application.put(
    "/api/v1/update_translation",
    status_code=status.HTTP_200_OK,
    description="Update translation by id",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "translation not found"},
        status.HTTP_200_OK: {"status": "updated"},
    },
)
async def update_translate(id: int, session: AsyncSession = Depends(db_connection)):
    update_unit = Update(session)
    # translate = await update_unit.get_translation(id)
    # if not translate:
    #    raise HTTPException(status_code=404, detail="Translation not found")
    return {"status": "updated"}


@application.put("/api/v1/update_language")
async def update_language(id: int, session: AsyncSession = Depends(db_connection)):
    read_unit = Update(session)
    translate = await read_unit.update_animal(id)
    if not translate:
        raise HTTPException(status_code=404, detail="Language not found")
    return {"status": "updated"}


@application.delete("/api/v1/delete_translation")
async def delete_translate(id: int, session: AsyncSession = Depends(db_connection)):
    delete_unit = Delete(session)
    deleted_id = await delete_unit.delete_animal_speech(id)
    if not deleted_id:
        raise HTTPException(status_code=404, detail="Translation not found")
    return {"status": "deleted"}


@application.delete("/api/v1/delete_language")
async def delete_language(id: int, session: AsyncSession = Depends(db_connection)):
    delete_unit = Delete(session)
    deleted_id = await delete_unit.delete_animal(id)
    if not deleted_id:
        raise HTTPException(status_code=404, detail="Language not found")
    return {"status": "deleted"}
