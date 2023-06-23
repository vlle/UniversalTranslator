from contextlib import asynccontextmanager
from typing import Annotated, Tuple

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import Create, Delete, Read, Update
from app.database import engine, init_models, maker
from app.openai import ask_gpt3
from app.pydantic_models import (
    LanguageInput,
    LanguageOutput,
    SpeechOutput,
    TranslateInput,
    TranslateOutput,
    TranslateUpdate,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
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
        input,
    )


@application.post(
    "/api/v1/create_language",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "language already exists"},
        status.HTTP_201_CREATED: {"model": LanguageOutput},
    },
)
async def create_language(
    language: LanguageInput,
    session: AsyncSession = Depends(db_connection),
):
    create_unit = Create(session)
    try:
        await create_unit.register_language(language)
        return LanguageOutput(language=language.language)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Language already exists"
        )


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
    translation_data: Annotated[
        Tuple[TranslateOutput, TranslateInput], Depends(translation)
    ],
    session: AsyncSession = Depends(db_connection),
) -> TranslateOutput:
    translation, origin = translation_data[0], translation_data[1]
    if len(translation.translated_from) > 30:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE, detail="Length too big"
        )

    create_unit = Create(session)
    try:
        await create_unit.register_language(
            LanguageInput(language=origin.translate_to_language)
        )
    except IntegrityError:
        pass
    try:
        await create_unit.register_language(
            LanguageInput(language=translation.translated_from)
        )
    except IntegrityError:
        pass
    translation.id = await create_unit.register_translation(
        origin,
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
    name: str, session: AsyncSession = Depends(db_connection)
) -> LanguageOutput:
    read_unit = Read(session)
    language = await read_unit.get_language(name)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Language not found"
        )

    return LanguageOutput(language=language.name)


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
        LanguageOutput(language=language.name) for language in languages
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
        origin_language=translate.origin_language,
        translated_language=translate.translated_language,
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
async def update_translate(
    new_translation: TranslateUpdate, session: AsyncSession = Depends(db_connection)
):
    update_unit = Update(session)
    read_unit = Read(session)
    is_there_translation = await read_unit.get_translation(new_translation.id)
    if not is_there_translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    await update_unit.update_translation(
        new_translation.id, new_translation.new_translation
    )
    return {"status": "updated"}


@application.delete(
    "/api/v1/delete_translation/{id}",
    status_code=status.HTTP_200_OK,
    description="Delete translation by id",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Translation not found"},
        status.HTTP_200_OK: {"status": "deleted"},
    },
)
async def delete_translate(id: int, session: AsyncSession = Depends(db_connection)):
    delete_unit = Delete(session)
    deleted_id = await delete_unit.delete_translate(id)
    if not deleted_id:
        raise HTTPException(status_code=404, detail="Translation not found")
    return {"status": "deleted"}


@application.delete(
    "/api/v1/delete_language/{name}",
    status_code=status.HTTP_200_OK,
    description="Delete language by name",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Language not found"},
        status.HTTP_200_OK: {"status": "deleted"},
    },
)
async def delete_language(name: str, session: AsyncSession = Depends(db_connection)):
    delete_unit = Delete(session)
    read_unit = Read(session)
    is_there_language = await read_unit.get_language(name)
    if not is_there_language:
        raise HTTPException(status_code=404, detail="Language not found")
    await delete_unit.delete_language(name)
    return {"status": "deleted"}
