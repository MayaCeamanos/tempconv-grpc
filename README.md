# TempConv gRPC – Protocol Buffers

This project implements a simple distributed system using **gRPC** and **Protocol Buffers**.

The service provides two remote procedures:
- Convert Celsius to Fahrenheit
- Convert Fahrenheit to Celsius

The project is implemented in Python and runs locally without any cloud infrastructure.

---
## Requirements

- Python 3.11 or newer
- Virtual environment (recommended)

---

## Setup

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate

## Install dependencies:

python -m pip install --upgrade pip
pip install -r requirements.txt

## Generate gRPC Code from Protocol Buffers

python -m grpc_tools.protoc \
  -I proto \
  --python_out=. \
  --grpc_python_out=. \
  proto/tempconv.proto

## This generates:

tempconv_pb2.py
tempconv_pb2_grpc.py

## Run the gRPC Server
From the project root:

python -m server.server
The server will start on port 50051.

## Run the Client (Test)
Open a second terminal, activate the virtual environment, and run:

python -m client.client

Expected output:

0 °C = 32.0 °F
100 °F = 37.77777777777778 °C

## Notes
This project demonstrates basic gRPC communication.
No Docker or Kubernetes is required.
The service runs locally and can be extended or deployed if needed.

