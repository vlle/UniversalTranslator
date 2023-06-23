import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.crud import Delete, Read
from app.database import init_models
from app.main import application, db_connection, translation
from app.models import Base
from app.pydantic_models import TranslateOutput

# Here I am creating test database in memory and overriding the db_connection and animal_translation
# I know that SQLite3 doesn't support async operations, but for testing measures this should be ok.

TEST_DB_URL = "sqlite+aiosqlite://"

engine = create_async_engine(TEST_DB_URL, echo=False)
maker = async_sessionmaker(engine, expire_on_commit=False)


async def drop_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    db = maker()
    try:
        yield db
    finally:
        await db.close()


@pytest.fixture
async def get_session():
    obj = override_get_db()
    session = await anext(obj)
    return session


async def override_chatgpt_translation():
    return (TranslateOutput(id=-1, translated_from="Cat", text="I am kitty"), "kitten")


application.dependency_overrides[translation] = override_chatgpt_translation
application.dependency_overrides[db_connection] = override_get_db


# @pytest.mark.asyncio
# async def test_create_language():
#    await init_models(engine)


@pytest.mark.asyncio
async def test_create_translation(get_session):
    await drop_tables(engine)
    await init_models(engine)
    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        response = await ac.post(
            "/api/v1/create_translation",
            json={"text": "I am kitty", "translate_to_language": "kitten"},
        )

    assert response.status_code == 201
    session = await get_session
    read_obj = Read(session)
    assert response.json()["translated_from"] == "Cat"
    assert response.json()["text"] == "I am kitty"
    assert await read_obj.get_language("Cat") is not None
    assert await read_obj.get_language("kitten") is not None


@pytest.mark.asyncio
async def test_get_language():
    await drop_tables(engine)
    await init_models(engine)
    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        response = await ac.post(
            "/api/v1/create_translation",
            json={"text": "I am kitty", "translate_to_language": "kitten"},
        )
        language = response.json()["translated_from"]
        response = await ac.get(f"/api/v1/get_language?name={language}")
    assert response.status_code == 200
    assert response.json()["language"] == "Cat"


@pytest.mark.asyncio
async def test_get_language_translation():
    await drop_tables(engine)
    await init_models(engine)
    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        response = await ac.post("/api/v1/create_translation")
        id = response.json()["id"]
        response = await ac.get(f"/api/v1/get_translation?id={id}")
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["translated_text"] == "I am kitty"


# def test_update_animal():
#     pass
#
#
# def test_update_animal_translation():
#     pass
#
#
# def test_delete_animal():
#     pass
#
#
# def test_delete_animal_translation():
#     pass
