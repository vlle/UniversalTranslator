from pydantic import BaseModel


class AnimalTranslateInput(BaseModel):
    wished_animal_language: str
    text: str


class AnimalTranslateOutput(BaseModel):
    animal: str
    text: str
