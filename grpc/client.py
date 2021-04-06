import logging
import asyncio
import grpc

import geoip_pb2
import geoip_pb2_grpc

import sys

ip = sys.argv[1]

async def run() -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        for i in range(1000):
            stub = geoip_pb2_grpc.GeoIpServiceStub(channel)
            resp = await stub.getCountry(geoip_pb2.GeoIpRequest(ip=ip))
            print(f"geoip: ip: {resp.ip} country: {resp.country}")


if __name__ == '__main__':
    logging.basicConfig()
    asyncio.run(run())
