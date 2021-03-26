import asyncio
import logging
import grpc
import geoip_pb2
import geoip_pb2_grpc

import geoip2.database
import geoip2


def get_city(ip: str):
    try:
        resp = reader.city(ip)
        return {"code": 0,  "ip": ip,
                "country": resp.country.iso_code, "city": resp.city.name,
                "latitude": resp.location.latitude, "longitude": resp.location.longitude}
    except geoip2.errors.AddressNotFoundError:
        raise UnicornException(status=404, code=-20000, message=str(e))
    except Exception as e:
        raise UnicornException(status=400, code=-20000, message=str(e))


class GeoIpServiceServicer(geoip_pb2_grpc.GeoIpServiceServicer):
    def __init__(self):
        self.reader = geoip2.database.Reader('../mmdb/geo2lite.mmdb')

    def getCity(self, request, context):
        resp = self.reader.city(request.ip)
        return geoip_pb2.GeoIpResponse(ip=request.ip,
                                       country=resp.country.iso_code,
                                       city=resp.city.name,
                                       latitude=resp.location.latitude,
                                       longitude=resp.location.longitude)
            

async def serve() -> None:
    server = grpc.aio.server()
    geoip_pb2_grpc.add_GeoIpServiceServicer_to_server(GeoIpServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        await server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    asyncio.run(serve())
