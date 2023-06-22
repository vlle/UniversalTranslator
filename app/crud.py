from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Animal, AnimalSpeech


class CRUDManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class Create(CRUDManager):
    async def register_animal(self):
        async with self.session:
            pass


class Read(CRUDManager):
    async def get_animal(self, id: int):
        async with self.session, self.session.begin():
            return await self.session.get(Animal, id)

    async def get_all_animals(self):
        stmt = select(Animal).where(Animal.id > 0)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_all_animal_speech(self):
        stmt = select(AnimalSpeech).where(Animal.id > 0)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_animal_speech(self, id: int):
        async with self.session, self.session.begin():
            return await self.session.get(AnimalSpeech, id)


class Update(CRUDManager):
    async def update_animal(self):
        async with self.session, self.session.begin():
            pass

    async def update_animal_speech(self):
        async with self.session, self.session.begin():
            pass


class Delete(CRUDManager):
    async def delete_animal(self):
        async with self.session, self.session.begin():
            pass

    async def delete_animal_speech(self):
        async with self.session, self.session.begin():
            pass
