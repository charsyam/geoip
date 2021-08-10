from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from exceptions import UnicornException
from models import CountryEntity

import geoip2.database
import geoip2
import socket

from prometheus_fastapi_instrumentator import Instrumentator, metrics


self_ip = socket.gethostbyname(socket.gethostname())


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    self_ip = s.getsockname()[0]
    s.close()
    return self_ip


self_ip = get_local_ip()

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


@app.get("/health_check")
async def health_check():
    return "ok"


@app.get("/api/v1/geoip/{ip}", response_model=CountryEntity)
async def read_item(ip: str):
    try:
        resp = reader.country(ip)
        iso_code = ""
        if resp.country.iso_code:
            iso_code = resp.country.iso_code

        return {"ip": ip, "country": iso_code, "self": self_ip, "ctype": "green"}
    except geoip2.errors.AddressNotFoundError as e:
        raise UnicornException(status=404, code=-20001, message=str(e))
    except Exception as e:
        raise UnicornException(status=400, code=-20000, message=str(e))
