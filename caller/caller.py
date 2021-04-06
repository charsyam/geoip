from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from exceptions import UnicornException

from prometheus_fastapi_instrumentator import Instrumentator, metrics

import logging
import asyncio
import grpc

import geoip_pb2
import geoip_pb2_grpc
import time
import http3
import json


app = FastAPI()
client = http3.AsyncClient()
channel = grpc.aio.insecure_channel('localhost:50051')


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


async def call_api(ip: str):
    url = f"http://localhost:8000/geoip/{ip}"
    r = await client.get(url)
    return r.text


@app.get("/grpc/{ip}")
async def call_grpc(ip: str):
    t = time.process_time()
    try:
        elapsed_time = time.process_time() - t
        stub = geoip_pb2_grpc.GeoIpServiceStub(channel)
        resp = await stub.getCountry(geoip_pb2.GeoIpRequest(ip=ip))
        return {"code": 0, "type": "grpc", "ip": ip, "country": resp.country, "latency": elapsed_time}
    except Exception as e:
        raise UnicornException(status=400, code=-20000, message=str(e))

@app.get("/http/{ip}")
async def call_http(ip: str):
    client = http3.AsyncClient()
    t = time.process_time()
    try:
        body = await call_api(ip)
        resp = json.loads(body)
        elapsed_time = time.process_time() - t
        return {"code": 0, "type": "http", "ip": ip, "country": resp["country"], "latency": elapsed_time}
    except Exception as e:
        raise UnicornException(status=400, code=-20000, message=str(e))
