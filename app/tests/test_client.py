import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.crud import Read
from app.database import init_models
from app.main import application, db_connection, translation
from app.models import Base
from app.pydantic_models import TranslateInput, TranslateOutput

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
    return (
        TranslateOutput(id=-1, translated_from="Cat", text="I am kitty"),
        TranslateInput(text="meow", translate_to_language="kitten"),
    )


application.dependency_overrides[translation] = override_chatgpt_translation
application.dependency_overrides[db_connection] = override_get_db


@pytest.mark.asyncio
async def test_create_language(get_session):
    await drop_tables(engine)
    await init_models(engine)
    session = await get_session
    read_obj = Read(session)
    assert await read_obj.get_language("Cat") is None

    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        response = await ac.post(
            "/api/v1/create_language",
            json={"language": "Cat"},
        )

    assert response.status_code == 201
    assert await read_obj.get_language("Cat") is not None


@pytest.mark.asyncio
async def test_create_language_conflict(get_session):
    await drop_tables(engine)
    await init_models(engine)
    session = await get_session
    read_obj = Read(session)
    assert await read_obj.get_language("Cat") is None

    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        await ac.post(
            "/api/v1/create_language",
            json={"language": "Cat"},
        )
        response = await ac.post(
            "/api/v1/create_language",
            json={"language": "Cat"},
        )

    assert response.status_code == 409
    assert await read_obj.get_language("Cat") is not None


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
async def test_get_languages():
    await drop_tables(engine)
    await init_models(engine)
    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        await ac.post(
            "/api/v1/create_translation",
            json={"text": "I am kitty", "translate_to_language": "kitten"},
        )
        response = await ac.get(
            "/api/v1/get_all_languages",
        )

    assert len(response.json()) == 2
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_language_translation():
    await drop_tables(engine)
    await init_models(engine)
    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        response = await ac.post(
            "/api/v1/create_translation",
            json={"text": "I am kitty", "translate_to_language": "kitten"},
        )
        id = response.json()["id"]
        response = await ac.get(f"/api/v1/get_translation?id={id}")
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["translated_text"] == "I am kitty"


@pytest.mark.asyncio
async def test_update_translation():
    await drop_tables(engine)
    await init_models(engine)
    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        response = await ac.post(
            "/api/v1/create_translation",
            json={"text": "I am kitty", "translate_to_language": "kitten"},
        )
        print(response.json())
        id = response.json()["id"]
        response = await ac.get(f"/api/v1/get_translation?id={id}")
        assert response.json()["translated_text"] == "I am kitty"
        response = await ac.put(
            "/api/v1/update_translation",
            json={"id": id, "new_translation": "new!"},
        )
        assert response.status_code == 200
        response = await ac.get(f"/api/v1/get_translation?id={id}")
        assert response.json()["translated_text"] == "new!"


@pytest.mark.asyncio
async def test_delete_language():
    await drop_tables(engine)
    await init_models(engine)
    async with AsyncClient(app=application, base_url="http://127.0.0.1") as ac:
        await ac.post(
            "/api/v1/create_language",
            json={"language": "Cat"},
        )
        response = await ac.get("api/v1/get_language?name=Cat")
        assert response.status_code == 200
        response = await ac.delete(
            "/api/v1/delete_language/Cat",
        )
        assert response.status_code == 200
        print(response.json())
        assert response.json()["status"] == "deleted"
        response = await ac.get("api/v1/get_language?name=Cat")
        assert response.status_code == 404
