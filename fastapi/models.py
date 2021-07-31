from pydantic import BaseModel


class BaseEntity(BaseModel):
    pass


class CountryEntity(BaseEntity):
    ip: str
    country: str


class CityEntity(BaseEntity):
    city: str
    latitude: float
    longitude: float
