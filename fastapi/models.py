from pydantic import BaseModel


class CodeEntity(BaseModel):
    code: int


class CityEntity(CodeEntity):
    ip: str
    country: str
    city: str
    latitude: float
    longitude: float
