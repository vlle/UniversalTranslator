import random

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Animal, AnimalSpeech
from app.pydantic_models import AnimalInput, AnimalTranslateInput, AnimalTranslateOutput


class CRUDManager:
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize a CRUDManager object.

        Args:
            session (AsyncSession): The async SQLAlchemy session.
        """
        self.session = session


class Create(CRUDManager):
    async def register_animal(self, animal: AnimalInput):
        """
        Register an animal.

        This method is used to register an animal in the database.

        Returns:
            None
        """

        animal_obj = Animal(name=animal.name, language=animal.language)
        async with self.session, self.session.begin():
            self.session.add(animal_obj)

    async def register_animal_translation(
        self, animal_inp: AnimalTranslateInput, animal_out: AnimalTranslateOutput
    ) -> int:
        """
        Register an animal translation.

        This method is used to register an animal translation in the database.

        Args:
            animal_inp (AnimalTranslateInput): The input data for animal translation.
            animal_out (AnimalTranslateOutput): The output data for animal translation.

        Returns:
            int: The ID of the registered animal translation.
        """
        animal_received = Animal(name=animal_out.animal, language=animal_out.animal)
        animal_result = Animal(
            name=animal_inp.wished_animal_language,
            language=animal_inp.wished_animal_language,
        )

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
            await self.session.commit()
            return animal_translation.id


class Read(CRUDManager):
    async def get_animal(self, id: int):
        """
        Get an animal by ID.

        This method retrieves an animal from the database based on its ID.

        Args:
            id (int): The ID of the animal.

        Returns:
            Animal: The retrieved animal object.
        """
        async with self.session, self.session.begin():
            return await self.session.get(Animal, id)

    async def get_all_animals(self):
        """
        Get all animals.

        This method retrieves all animals from the database.

        Returns:
            List[Animal]: A list of all animal objects.
        """
        stmt = select(Animal).where(Animal.id > 0)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_all_animal_speech(self):
        """
        Get all animal speeches.

        This method retrieves all animal speeches from the database.

        Returns:
            List[AnimalSpeech]: A list of all animal speech objects.
        """
        stmt = select(AnimalSpeech).where(Animal.id > 0)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_animal_speech(self, id: int):
        """
        Get an animal speech by ID.

        This method retrieves an animal speech from the database based on its ID.

        Args:
            id (int): The ID of the animal speech.

        Returns:
            AnimalSpeech: The retrieved animal speech object.
        """
        async with self.session, self.session.begin():
            return await self.session.get(AnimalSpeech, id)


class Update(CRUDManager):
    async def update_animal(self, id: int):
        """
        Update an animal.

        This method is used to update an existing animal in the database.

        Args:
            id (int): The ID of the animal

        Returns:
            Animal: The retrieved animal object.
        """
        async with self.session, self.session.begin():
            pass

    async def update_animal_speech(self, id: int):
        """
        Update an animal speech.

        This method is used to update an existing animal speech in the database.

        Returns:
            None
        """
        async with self.session, self.session.begin():
            pass


class Delete(CRUDManager):
    async def delete_animal(self, id: int):
        """
        Delete an animal.

        This method is used to delete an animal from the database.

        Returns:
            id (int): The ID of deleted animal (or None)
        """
        stmt = delete(Animal).where(Animal.id == id).returning(Animal.id)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).one_or_none()

    async def delete_animal_speech(self, id: int):
        """
        Delete an animal speech.

        This method is used to delete an animal speech from the database.

        Returns:
            id (int): The ID of deleted animal (or None)
        """
        stmt = (
            delete(AnimalSpeech).where(AnimalSpeech.id == id).returning(AnimalSpeech.id)
        )
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).one_or_none()
