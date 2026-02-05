import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import grpc

import tempconv_pb2
import tempconv_pb2_grpc
from server.server import TempConvServicer  # reutilizamos tu servicer gRPC
from concurrent import futures


def start_grpc_server():
    """Start gRPC server on an internal port (not exposed publicly)."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tempconv_pb2_grpc.add_TempConvServicer_to_server(TempConvServicer(), server)

    grpc_port = "50051"
    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    print(f"✅ gRPC server running on port {grpc_port} (internal)")
    server.wait_for_termination()


HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>TempConv (gRPC + HTTP gateway)</title>
  <style>
    body { font-family: sans-serif; max-width: 720px; margin: 40px auto; }
    input, select, button { font-size: 16px; padding: 8px; margin: 6px 0; }
    .row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    pre { background: #f4f4f4; padding: 12px; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>TempConv (gRPC + HTTP gateway)</h1>
  <p>This page calls an HTTP endpoint that internally calls the gRPC service.</p>

  <div class="row">
    <input id="value" type="number" step="any" value="0" />
    <select id="from">
      <option value="C">Celsius</option>
      <option value="F">Fahrenheit</option>
    </select>
    <span>→</span>
    <select id="to">
      <option value="F">Fahrenheit</option>
      <option value="C">Celsius</option>
    </select>
    <button onclick="convert()">Convert</button>
  </div>

  <pre id="out">{}</pre>

  <script>
    async function convert(){
      const value = document.getElementById("value").value;
      const from = document.getElementById("from").value;
      const to = document.getElementById("to").value;
      const url = `/convert?value=${encodeURIComponent(value)}&from=${from}&to=${to}`;
      const res = await fetch(url);
      const txt = await res.text();
      document.getElementById("out").textContent = txt;
    }
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        # CORS (por si lo pruebas desde otro sitio)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/health":
            self._send_json({"status": "ok"})
            return

        if parsed.path == "/convert":
            qs = parse_qs(parsed.query)
            try:
                value = float(qs.get("value", [""])[0])
                frm = (qs.get("from", [""])[0] or "").upper()
                to = (qs.get("to", [""])[0] or "").upper()
            except Exception:
                self._send_json({"error": "Invalid query params"}, status=400)
                return

            if frm not in ("C", "F") or to not in ("C", "F") or frm == to:
                self._send_json({"error": "Use from=C|F and to=C|F and from!=to"}, status=400)
                return

            # Call gRPC locally
            channel = grpc.insecure_channel("127.0.0.1:50051")
            stub = tempconv_pb2_grpc.TempConvStub(channel)

            req = tempconv_pb2.TemperatureRequest(value=value)
            if frm == "C" and to == "F":
                resp = stub.CelsiusToFahrenheit(req)
            else:
                resp = stub.FahrenheitToCelsius(req)

            self._send_json({
                "input": {"value": value, "from": frm, "to": to},
                "result": resp.value
            })
            return

        self._send_json({"error": "Not found"}, status=404)


def main():
    # Start gRPC in background
    t = threading.Thread(target=start_grpc_server, daemon=True)
    t.start()

    # HTTP server listens on Render's PORT (or 8080 locally)
    port = int(os.environ.get("PORT", "8080"))
    httpd = HTTPServer(("0.0.0.0", port), Handler)
    print(f"✅ HTTP gateway running on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
