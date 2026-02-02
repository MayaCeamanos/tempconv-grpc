import grpc

import tempconv_pb2
import tempconv_pb2_grpc



def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = tempconv_pb2_grpc.TempConvStub(channel)

    # Celsius → Fahrenheit
    c_request = tempconv_pb2.TemperatureRequest(value=0.0)
    c_response = stub.CelsiusToFahrenheit(c_request)
    print(f"0 °C = {c_response.value} °F")

    # Fahrenheit → Celsius
    f_request = tempconv_pb2.TemperatureRequest(value=100.0)
    f_response = stub.FahrenheitToCelsius(f_request)
    print(f"100 °F = {f_response.value} °C")


if __name__ == "__main__":
    run()
