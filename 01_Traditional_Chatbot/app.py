"""Local browser server using Python's standard library; no external AI calls."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from bot import get_response

PAGE = Path(__file__).with_name("index.html")


class Handler(BaseHTTPRequestHandler):
    def send_data(self, status, data, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def reply_json(self, status, payload):
        self.send_data(status, json.dumps(payload).encode())

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_data(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        else:
            self.reply_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/chat":
            return self.reply_json(404, {"error": "Not found"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 8192:
                return self.reply_json(400, {"error": "Request must contain 1-8192 bytes."})
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("Expected an object")
        except (ValueError, UnicodeDecodeError):
            return self.reply_json(400, {"error": "Send a JSON object with a message field."})
        self.reply_json(200, get_response(payload.get("message")))

    def log_message(self, format, *args):
        # Log request metadata only, not the user's message.
        super().log_message(format, *args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Campus Help Bot running at http://127.0.0.1:{args.port}", flush=True)
    print("Press Control+C to stop. Demo information only; no AI service used.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
