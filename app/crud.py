import sqlalchemy
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import exc

from app.models import Language, Translation
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

        language_obj = Language(name=language.language)
        async with self.session, self.session.begin():
            self.session.add(language_obj)

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
            try:
                self.session.add(language_received)
            except exc.IntegrityError:
                pass
            try:
                self.session.add(language_result)
            except exc.IntegrityError:
                pass

            await self.session.flush()
            translation = Translation(
                origin_language=language_received.name,
                translated_language=language_result.name,
                text=inp.text,
                translated_text=out.text,
            )
            self.session.add(translation)
            await self.session.commit()
            return translation.id


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
        Get all languages.

        This method retrieves all languages from the database.

        Returns:
            List[Language]: A list of all language objects.
        """
        stmt = select(Language)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_all_translations(self):
        """
        Get all language speeches.

        This method retrieves all languages speeches from the database.

        Returns:
            List[AnimalSpeech]: A list of all languages speech objects.
        """
        stmt = select(Translation)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).all()

    async def get_translation(self, id: int) -> Translation | None:
        """
        Get an translation by ID.

        This method retrieves an translation from the database based on its ID.

        Args:
            id (int): The ID of the translation.

        Returns:
            Translation: The retrieved translation object.
        """
        async with self.session, self.session.begin():
            return await self.session.get(Translation, id)


class Update(CRUDManager):
    async def update_language(self, id: int):
        """
        Update an language.

        This method is used to update an existing language in the database.

        Args:
            id (int): The ID of the language

        Returns:
            Animal: The retrieved language object.
        """
        async with self.session, self.session.begin():
            pass

    async def update_translation(self, id: int):
        """
        Update an translation.

        This method is used to update an existing translation in the database.

        Returns:
            None
        """
        async with self.session, self.session.begin():
            pass


class Delete(CRUDManager):
    async def delete_language(self, name: int):
        """
        Delete an language.

        This method is used to delete an language from the database.

        Returns:
            id (int): The ID of deleted language (or None)
        """
        stmt = delete(Language).where(Language.name == name).returning(Language.name)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).one_or_none()

    async def delete_translate(self, id: int):
        """
        Delete an translation.

        This method is used to delete an translation from the database.

        Returns:
            id (int): The ID of deleted translation (or None)
        """
        stmt = delete(Translation).where(Translation.id == id).returning(Translation.id)
        async with self.session, self.session.begin():
            return (await self.session.scalars(stmt)).one_or_none()
