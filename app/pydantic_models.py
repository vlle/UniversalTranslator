from pydantic import BaseModel


class AnimalInput(BaseModel):
    language: str
    name: str


class AnimalOutput(BaseModel):
    id: int
    language: str
    name: str


class AnimalTranslateInput(BaseModel):
    wished_animal_language: str
    text: str


class AnimalTranslateOutput(BaseModel):
    id: int
    animal: str
    text: str
