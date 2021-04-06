import asyncio
import logging
import grpc
import geoip_pb2
import geoip_pb2_grpc

import geoip2.database
import geoip2


class GeoIpServiceServicer(geoip_pb2_grpc.GeoIpServiceServicer):
    def __init__(self):
        self.reader = geoip2.database.Reader('../mmdb/GeoLite2-Country.mmdb')

    def getCountry(self, request, context):
        resp = self.reader.country(request.ip)
        return geoip_pb2.GeoIpResponse(ip=request.ip,
                                       country=resp.country.iso_code)
            

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
