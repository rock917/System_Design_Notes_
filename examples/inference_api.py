"""Educational local HTTP inference API, Python 3.11+ with no third-party packages.

PowerShell: $env:DEMO_API_KEY='local-demo-key-change-me'; python inference_api.py
Bash: DEMO_API_KEY=local-demo-key-change-me python inference_api.py
Bind is localhost by default. This is NOT a production HTTP server or real ML model.
The deterministic score illustrates serving mechanics, not predictive accuracy.
"""
import argparse
from collections import Counter
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
import threading
import time
from algorithms import TokenBucket, TTLCache

MODEL_VERSION = "toy-linear-v1"


class Clock:
    @property
    def now(self):
        return time.monotonic()


def validate_features(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 32:
        raise ValueError("features must contain 1 to 32 numbers")
    if any(isinstance(x, bool) or not isinstance(x, (int, float))
           or not math.isfinite(x) or abs(x) > 100 for x in value):
        raise ValueError("features must be finite numbers between -100 and 100")
    return [float(x) for x in value]


def predict(features):
    mean = sum(features) / len(features)
    return round(1 / (1 + math.exp(-mean)), 6)


class State:
    def __init__(self, key):
        if len(key) < 16:
            raise ValueError("demo API key must contain at least 16 characters")
        self.key = key
        self.clock = Clock()
        self.lock = threading.Lock()
        self.limiter = TokenBucket(20, 5, self.clock)
        self.cache = TTLCache(self.clock, max_entries=256)
        self.slots = threading.BoundedSemaphore(4)
        self.counters = Counter()
        self.ready = True

    def count(self, name):
        with self.lock:
            self.counters[name] += 1


def make_server(host="127.0.0.1", port=8000, key="local-test-key-only"):
    state = State(key)
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *_):
            # No request bodies, credentials, or arbitrary client text in logs.
            pass

        def send(self, status, payload, content_type="application/json"):
            data = (json.dumps(payload).encode() if content_type == "application/json" else payload.encode())
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/live":
                return self.send(200, {"live": True})
            if self.path == "/ready":
                return self.send(200 if state.ready else 503, {"ready": state.ready, "model": MODEL_VERSION})
            if self.path == "/metrics":
                with state.lock:
                    body = "\n".join(f"demo_{name}_total {count}" for name, count in sorted(state.counters.items())) + "\n"
                return self.send(200, body, "text/plain; version=0.0.4")
            return self.send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/v1/predict":
                return self.send(404, {"error": "not found"})
            supplied = self.headers.get("X-API-Key", "")
            if not hmac.compare_digest(supplied.encode('utf-8'), state.key.encode('utf-8')):
                state.count("unauthorized")
                return self.send(401, {"error": "invalid credentials"})
            if self.headers.get("Transfer-Encoding"):
                return self.send(400, {"error": "transfer encoding unsupported in this demo"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 8192:
                    return self.send(413, {"error": "body must be 1 to 8192 bytes"})
                if self.headers.get_content_type() != "application/json":
                    return self.send(415, {"error": "application/json required"})
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise ValueError("incomplete body")
                payload = json.loads(raw)
                if not isinstance(payload, dict):
                    raise ValueError("object required")
                features = validate_features(payload.get("features"))
            except (ValueError, UnicodeError, TimeoutError):
                state.count("invalid")
                return self.send(400, {"error": "invalid bounded feature payload"})
            with state.lock:
                admitted = state.limiter.allow()
            if not admitted:
                state.count("rate_limited")
                return self.send(429, {"error": "rate limit exceeded", "retry_after_seconds": 1})
            if not state.slots.acquire(blocking=False):
                state.count("overloaded")
                return self.send(503, {"error": "inference capacity busy"})
            try:
                # One fixed demo tenant. Multi-tenant serving must include tenant and policy context.
                key_material = json.dumps([MODEL_VERSION, features], separators=(",", ":"))
                cache_key = hashlib.sha256(key_material.encode()).hexdigest()
                with state.lock:
                    score = state.cache.get(cache_key)
                cached = score is not None
                if not cached:
                    score = predict(features)
                    with state.lock:
                        state.cache.put(cache_key, score, ttl=30)
                state.count("cache_hit" if cached else "cache_miss")
                state.count("completed")
                return self.send(200, {"score": score, "model_version": MODEL_VERSION, "cached": cached})
            finally:
                state.slots.release()
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.state = state
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    key = os.environ.get("DEMO_API_KEY", "")
    server = make_server(args.host, args.port, key)
    print(f"Local teaching API at http://{args.host}:{args.port}; model={MODEL_VERSION}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
