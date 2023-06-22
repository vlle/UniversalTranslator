import random

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Animal, AnimalSpeech
from app.pydantic_models import AnimalTranslateInput, AnimalTranslateOutput


class CRUDManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class Create(CRUDManager):
    async def register_animal(self):
        async with self.session:
            pass

    async def register_animal_translation(
        self, animal_inp: AnimalTranslateInput, animal_out: AnimalTranslateOutput
    ):
        possible_names = [
            "Lovely ",
            "Little ",
            "Beatiful ",
            "Weird ",
            "Unusual ",
            "Strong ",
        ]
        random_number_1 = "№ " + str(random.randint(0, 10000))
        random_number_2 = "№ " + str(random.randint(0, 10000))
        name_1 = random.choice(possible_names) + animal_out.animal + random_number_1
        name_2 = (
            random.choice(possible_names)
            + animal_inp.wished_animal_language
            + random_number_2
        )

        animal_received = Animal(name=name_1, language=animal_out.animal)
        animal_result = Animal(name=name_2, language=animal_inp.wished_animal_language)

        async with self.session, self.session.begin():
            self.session.add(animal_received)
            self.session.add(animal_result)
            await self.session.flush()
            animal_translation = AnimalSpeech(
                origin_animal_id=animal_received.id,
                translated_animal_id=animal_result.id,
                text=animal_inp.text,
                translated_text=animal_out.text,
            )
            self.session.add(animal_translation)


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
