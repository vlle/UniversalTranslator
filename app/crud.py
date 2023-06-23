from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnimalSpeech, Language
from app.pydantic_models import LanguageInput, TranslateInput, TranslateOutput


class CRUDManager:
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize a CRUDManager object.

        Args:
            session (AsyncSession): The async SQLAlchemy session.
        """
        self.session = session


class Create(CRUDManager):
    async def register_language(self, language: LanguageInput):
        """
        Register an language.

        This method is used to register an language in the database.

        Returns:
            None
        """

        animal_obj = Language(name=language.language)
        async with self.session, self.session.begin():
            self.session.add(animal_obj)

    async def register_translation(
        self, inp: TranslateInput, out: TranslateOutput
    ) -> int:
        """
        Register an translation.

        This method is used to register an translation in the database.

        Args:
            inp (TranslateInput): The input data for translation.
            out (TranslateOutput): The output data for translation.

        Returns:
            int: The ID of the registered translation.
        """
        language_received = Language(name=out.translated_from)
        language_result = Language(
            name=inp.translate_to_language,
        )

        async with self.session, self.session.begin():
            self.session.add(language_received)
            self.session.add(language_result)
            await self.session.flush()
            animal_translation = AnimalSpeech(
                origin_animal_id=language_received.id,
                translated_animal_id=language_result.id,
                text=inp.text,
                translated_text=out.text,
            )
            self.session.add(animal_translation)
            await self.session.commit()
            return animal_translation.id


class Read(CRUDManager):
    async def get_language(self, id: int) -> Language | None:
        """
        Get an language by ID.

        This method retrieves an language from the database based on its ID.

        Args:
            id (int): The ID of the language.

        Returns:
            Animal: The retrieved language object | None.
        """
        async with self.session, self.session.begin():
            return await self.session.get(Language, id)

    async def get_all_languages(self):
        """
        Get all animals.

        This method retrieves all animals from the database.

        Returns:
            List[Language]: A list of all language objects.
        """
        stmt = select(Language).where(Language.id > 0)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_all_translations(self):
        """
        Get all language speeches.

        This method retrieves all animal speeches from the database.

        Returns:
            List[AnimalSpeech]: A list of all animal speech objects.
        """
        stmt = select(AnimalSpeech).where(Language.id > 0)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_translation(self, id: int) -> AnimalSpeech | None:
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
        stmt = delete(Language).where(Language.id == id).returning(Language.id)
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
