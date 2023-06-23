from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import ForeignKey


class Base(DeclarativeBase):
    pass


class Language(Base):
    __tablename__ = "language"

    name: Mapped[str] = mapped_column(String(55), primary_key=True)
    translations: Mapped[List["Translation"]] = relationship(
        cascade="all, delete", foreign_keys="Translation.origin_language"
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)


class Translation(Base):
    __tablename__ = "translation"

    id: Mapped[int] = mapped_column(primary_key=True)
    origin_language: Mapped[int] = mapped_column(ForeignKey("language.name"))
    translated_language: Mapped[int] = mapped_column(ForeignKey("language.name"))
    text: Mapped[str] = mapped_column(String(512))
    translated_text: Mapped[str] = mapped_column(String(512))
