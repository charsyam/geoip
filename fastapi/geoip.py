from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from exceptions import UnicornException
from models import CityEntity

import geoip2.database
import geoip2


reader = geoip2.database.Reader('../mmdb/geo2lite.mmdb')
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status,
        content={"code": exc.code, "message": exc.message},
    )


@app.get("/geoip/{ip}", response_model=CityEntity)
async def read_item(ip: str):
    try:
        resp = reader.city(ip)
        return {"code": 0,  "ip": ip,
                "country": resp.country.iso_code, "city": resp.city.name,
                "latitude": resp.location.latitude, "longitude": resp.location.longitude}
    except geoip2.errors.AddressNotFoundError:
        raise UnicornException(status=404, code=-20000, message=str(e))
    except Exception as e:
        raise UnicornException(status=400, code=-20000, message=str(e))
