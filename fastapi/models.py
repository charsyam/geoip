from pydantic import BaseModel

class BaseEntity:
    pass

class CountryEntity(BaseEntity):
    ip: str
    country: str


class CityEntity(BaseEntity):
    city: str
    latitude: float
    longitude: float
