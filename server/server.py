from concurrent import futures
import time
import grpc

import tempconv_pb2
import tempconv_pb2_grpc



class TempConvServicer(tempconv_pb2_grpc.TempConvServicer):
    def CelsiusToFahrenheit(self, request, context):
        c = request.value
        f = (c * 9.0 / 5.0) + 32.0
        return tempconv_pb2.TemperatureResponse(value=f)

    def FahrenheitToCelsius(self, request, context):
        f = request.value
        c = (f - 32.0) * 5.0 / 9.0
        return tempconv_pb2.TemperatureResponse(value=c)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tempconv_pb2_grpc.add_TempConvServicer_to_server(TempConvServicer(), server)

    port = "50051"
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"✅ gRPC server running on port {port}...")

    try:
        while True:
            time.sleep(86400)  # 1 día
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server.stop(0)


if __name__ == "__main__":
    serve()
