from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from exceptions import UnicornException
from models import CountryEntity

import geoip2.database
import geoip2

from prometheus_fastapi_instrumentator import Instrumentator, metrics

reader = geoip2.database.Reader('./GeoLite2-Country.mmdb')
app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
)


instrumentator.add(
    metrics.request_size(
        should_include_handler=True,
        should_include_method=False,
        should_include_status=True,
        metric_namespace="a",
        metric_subsystem="b",
    )
).add(
    metrics.response_size(
        should_include_handler=True,
        should_include_method=False,
        should_include_status=True,
        metric_namespace="namespace",
        metric_subsystem="subsystem",
    )
)

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status,
        content={"code": exc.code, "message": exc.message},
    )


@app.get("/geoip/{ip}", response_model=CountryEntity)
async def read_item(ip: str):
    try:
        resp = reader.country(ip)
        return {"code": 0,  "ip": ip,
                "country": resp.country.iso_code}
    except geoip2.errors.AddressNotFoundError:
        raise UnicornException(status=404, code=-20000, message=str(e))
    except Exception as e:
        raise UnicornException(status=400, code=-20000, message=str(e))
