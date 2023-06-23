from pydantic import BaseModel


class LanguageInput(BaseModel):
    language: str


class LanguageOutput(BaseModel):
    language: str


class TranslateInput(BaseModel):
    text: str
    translate_to_language: str


class TranslateOutput(BaseModel):
    id: int
    translated_from: str
    text: str


class SpeechOutput(BaseModel):
    id: int
    origin_language: str
    translated_language: str
    text: str
    translated_text: str
