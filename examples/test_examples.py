"""Behavioral tests. Run from this directory: python -m unittest -v"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import http.client
import io
import json
import os
from pathlib import Path
import queue
import tempfile
import threading
import unittest
import algorithms as a
import concurrency as c
import inference_api as api
import messaging as m
import orders as o
import performance as p
import protocols as pr
import security as s
import incident_drill as incident


class AlgorithmTests(unittest.TestCase):
    def test_token_burst_and_refill(self):
        clock = a.FakeClock(); bucket = a.TokenBucket(5, 2, clock)
        self.assertEqual([bucket.allow() for _ in range(6)], [True] * 5 + [False])
        clock.advance(0.5); self.assertTrue(bucket.allow()); self.assertFalse(bucket.allow())

    def test_token_cost_and_cap(self):
        clock = a.FakeClock(); bucket = a.TokenBucket(5, 2, clock)
        self.assertFalse(bucket.allow(6)); clock.advance(100)
        self.assertTrue(bucket.allow(5)); self.assertFalse(bucket.allow())

    def test_cache_boundary_and_capacity(self):
        clock = a.FakeClock(); cache = a.TTLCache(clock, 1)
        cache.put("a", 1, 2); cache.put("b", 2, 2)
        self.assertIsNone(cache.get("a")); self.assertEqual(cache.get("b"), 2)
        clock.advance(2); self.assertIsNone(cache.get("b"))

    def test_breaker_opens_and_recovers(self):
        clock = a.FakeClock(); breaker = a.CircuitBreaker(clock, 1, 5)
        def fail(): raise TimeoutError()
        with self.assertRaises(TimeoutError): breaker.call(fail)
        with self.assertRaises(a.CircuitOpen): breaker.call(lambda: 1)
        clock.advance(5); self.assertEqual(breaker.call(lambda: 7), 7)
        self.assertEqual(breaker.state, "closed")

    def test_breaker_failed_probe_reopens(self):
        clock = a.FakeClock(); breaker = a.CircuitBreaker(clock, 1, 5)
        def fail(): raise ConnectionError()
        with self.assertRaises(ConnectionError): breaker.call(fail)
        clock.advance(5)
        with self.assertRaises(ConnectionError): breaker.call(fail)
        self.assertEqual(breaker.state, "open")

    def test_validation_error_does_not_trip_breaker(self):
        breaker = a.CircuitBreaker(a.FakeClock(), 1)
        def invalid(): raise ValueError()
        with self.assertRaises(ValueError): breaker.call(invalid)
        self.assertEqual(breaker.state, "closed")

    def test_jitter_windows(self):
        for delay, cap in zip(a.jitter_delays(), [0.1, 0.2, 0.4, 0.8]):
            self.assertGreaterEqual(delay, 0); self.assertLessEqual(delay, cap)

    def test_retry_success_and_deadline(self):
        clock = a.FakeClock(); attempts = []
        def operation(remaining):
            attempts.append(remaining)
            if len(attempts) == 1: raise ConnectionError()
            return "ok"
        self.assertEqual(a.retry_transient(operation, clock, 1, [0.1]), "ok")
        self.assertEqual(len(attempts), 2)
        def fail(_): raise ConnectionError()
        with self.assertRaises(TimeoutError): a.retry_transient(fail, clock, 0.15, [0.1])

    def test_round_robin_and_empty(self):
        self.assertEqual(a.round_robin(["a", "b"], 4), ["a", "b", "a", "b"])
        with self.assertRaises(ValueError): a.round_robin([], 1)

    def test_stale_projection_rejected(self):
        projection = {}; a.apply_newer(projection, "p", 3, "new")
        self.assertFalse(a.apply_newer(projection, "p", 2, "old"))
        self.assertEqual(projection["p"], (3, "new"))

    def test_quorum_and_stable_cohort(self):
        self.assertFalse(a.quorum_available(2, 5)); self.assertTrue(a.quorum_available(3, 5))
        self.assertEqual(a.enabled_for("tenant", 10), a.enabled_for("tenant", 10))


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.path = Path(self.temp.name) / "shop.db"
        o.initialize(self.path, stock=2)

    def tearDown(self): self.temp.cleanup()

    def test_concurrent_idempotency(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            ids = list(pool.map(lambda _: o.place_order(self.path, "a", "k"), range(8)))
        self.assertEqual(len(set(ids)), 1); self.assertEqual(o.counts(self.path)["orders"], 1)

    def test_payload_mismatch(self):
        o.place_order(self.path, "a", "k")
        with self.assertRaises(ValueError): o.place_order(self.path, "a", "k", quantity=2)

    def test_tenant_key_scope(self):
        self.assertNotEqual(o.place_order(self.path, "a", "k"), o.place_order(self.path, "b", "k"))

    def test_failed_transaction_rolls_back_all_effects(self):
        with self.assertRaises(RuntimeError): o.place_order(self.path, "a", "k", inject_failure=True)
        self.assertEqual(o.counts(self.path)["orders"], 0)
        o.place_order(self.path, "a", "k", quantity=2)

    def test_inventory_guard(self):
        o.place_order(self.path, "a", "k", quantity=2)
        with self.assertRaises(ValueError): o.place_order(self.path, "a", "next")
        self.assertEqual(o.counts(self.path)["outbox"], 1)

    def test_inbox_duplicate(self):
        order = o.place_order(self.path, "a", "k")
        self.assertTrue(o.consume_notification(self.path, 1, order))
        self.assertFalse(o.consume_notification(self.path, 1, order))
        self.assertEqual(o.counts(self.path)["notifications"], 1)

    def test_backup_restore(self):
        o.place_order(self.path, "a", "k")
        restored = Path(self.temp.name) / "copy.db"; o.backup(self.path, restored)
        self.assertEqual(o.counts(self.path), o.counts(restored))


class MessagingConcurrencyTests(unittest.TestCase):
    def test_dlq_and_duplicate(self):
        effects, done, dead = m.process_queue([m.Job("1", "ok"), m.Job("1", "ok"), m.Job("2", "poison")])
        self.assertEqual(effects, 1); self.assertEqual(dead[0].attempts, 3)

    def test_saga_unknown_retains_reservation(self):
        saga = m.OrderSaga(); saga.start("unknown")
        self.assertTrue(saga.reserved); self.assertEqual(saga.state, "reconcile-payment")
        with self.assertRaises(ValueError): saga.release()

    def test_saga_compensation_retry(self):
        saga = m.OrderSaga(); saga.start("declined", compensation_fails=True)
        self.assertTrue(saga.reserved); saga.release()
        self.assertFalse(saga.reserved); self.assertEqual(saga.state, "rejected")

    def test_pool_returns_after_exception_and_bounds_wait(self):
        pool = c.Pool(1)
        with self.assertRaises(RuntimeError):
            with pool.acquire(): raise RuntimeError()
        with pool.acquire():
            with self.assertRaises(queue.Empty):
                with pool.acquire(timeout=0.001): pass
        self.assertEqual(pool.available.qsize(), 1)

    def test_fencing_rejects_old_owner(self):
        ledger = c.FencedLedger(); ledger.write(9, "new")
        with self.assertRaises(ValueError): ledger.write(8, "old")
        self.assertEqual(ledger.value, "new")

    def test_deadlock_cycle_detection(self):
        self.assertTrue(c.has_cycle({"a": ["b"], "b": ["a"]}))
        self.assertFalse(c.has_cycle({"a": ["b"], "b": []}))

    def test_queue_conserves_work(self):
        result = c.queue_model(120, 100, 60, 1000)
        self.assertEqual(result["completed"] + result["backlog"] + result["rejected"], 7200)
        self.assertLessEqual(max(result["history"]), 1000)


class MeasurementSecurityProtocolTests(unittest.TestCase):
    def test_percentile_and_budget(self):
        self.assertEqual(p.percentile([20] * 980 + [2000] * 20, 0.99), 2000)
        self.assertAlmostEqual(p.budget(9900, 10000, 0.999)["burn_rate"], 10)

    def test_fanout(self): self.assertAlmostEqual(p.fanout_slow_probability(0.01, 100), 0.6339676587)

    def test_authorization_and_cors(self):
        self.assertFalse(s.authorize({"tenant": "a", "permissions": {"write"}}, {"tenant": "b"}, "write"))
        self.assertIsNone(s.cors_origin("https://app.example.attacker.test"))

    def test_csrf(self):
        self.assertFalse(s.csrf_valid("token", "")); self.assertFalse(s.csrf_valid("token", "wrong"))
        self.assertTrue(s.csrf_valid("token", "token"))
        self.assertFalse(s.csrf_valid("token", "caf\u00e9"))
        self.assertFalse(s.csrf_valid("token", 7))
        self.assertFalse(s.authorize({"permissions": {"read"}}, {}, "read"))

    def test_webhook_tamper_and_expiry(self):
        body = b'{"id":"1"}'; signature = s.sign_webhook(b"test", 1000, body)
        self.assertTrue(s.verify_webhook(b"test", 1000, body, signature, 1001))
        self.assertFalse(s.verify_webhook(b"test", 1000, body + b" ", signature, 1001))
        self.assertFalse(s.verify_webhook(b"test", 1000, body, signature, 1400))
        self.assertFalse(s.verify_webhook(b"test", 1000, body, "\u00e9" * 64, 1001))
        self.assertFalse(s.verify_webhook(b"test", True, body, signature, 1))

    def test_url_allowlist(self):
        self.assertTrue(s.allowed_partner_url("https://images.example/a"))
        for url in ["http://images.example/a", "https://images.example.evil.test", "https://u@images.example", "https://images.example:444/a", "https://127.0.0.1"]:
            self.assertFalse(s.allowed_partner_url(url))

    def test_parameter_binding(self):
        self.assertEqual(s.safe_name_search("O'Reilly"), [("O'Reilly",)])
        self.assertEqual(s.safe_name_search("' OR '1'='1"), [])

    def test_safe_logging(self):
        self.assertNotIn("secret", s.sanitized_log({"event": "ok", "password": "secret"}))

    def test_stream_partial_framing(self):
        wire = pr.encode_message({"a": 1}) + pr.encode_message({"b": 2})
        messages, pending = pr.take_messages(wire[:5]); self.assertEqual(messages, [])
        messages, pending = pr.take_messages(pending + wire[5:])
        self.assertEqual(messages, [{"a": 1}, {"b": 2}]); self.assertEqual(pending, b"")

    def test_cursor_expiry_and_schema(self):
        with self.assertRaises(ValueError): pr.events_after([], 1, 10)
        self.assertEqual(pr.read_order_v2({"amount_minor": 100})["currency"], "INR")

    def test_incident_recovery_includes_unknown_effects(self):
        self.assertFalse(incident.recovery_complete(True, True, 1))
        self.assertTrue(incident.recovery_complete(True, True, 0))


@unittest.skipUnless(os.environ.get("RUN_SOCKET_TESTS") == "1", "set RUN_SOCKET_TESTS=1 for loopback integration tests")
class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = api.make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(timeout=2)

    def request(self, path, data=None, key="local-test-key-only"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"X-API-Key": key, "Content-Type": "application/json"}
        connection.request("GET" if data is None else "POST", path, None if data is None else json.dumps(data), headers)
        response = connection.getresponse(); status, body = response.status, response.read()
        connection.close(); return status, body

    def test_health_and_auth(self):
        self.assertEqual(self.request("/ready")[0], 200)
        self.assertEqual(self.request("/v1/predict", {"features": [0]}, key="wrong")[0], 401)
        self.assertEqual(self.request("/v1/predict", {"features": [0]}, key="caf\u00e9")[0], 401)

    def test_prediction_and_cache(self):
        status, body = self.request("/v1/predict", {"features": [0, 0]})
        self.assertEqual(status, 200); self.assertEqual(json.loads(body)["score"], 0.5)
        status, body = self.request("/v1/predict", {"features": [0, 0]})
        self.assertTrue(json.loads(body)["cached"])

    def test_invalid_input(self):
        self.assertEqual(self.request("/v1/predict", {"features": [True]})[0], 400)
        self.assertEqual(self.request("/v1/predict", {"features": []})[0], 400)

    def test_metrics(self): self.assertEqual(self.request("/metrics")[0], 200)


class MemoryAPITests(APITests):
    """Exercise actual HTTP parsing and handlers without a network connection."""
    __unittest_skip__ = False
    __unittest_skip_why__ = ""

    @classmethod
    def setUpClass(cls):
        cls.server = api.make_server(port=0)

    @classmethod
    def tearDownClass(cls):
        cls.server.server_close()

    def request(self, path, data=None, key="local-test-key-only"):
        body = b"" if data is None else json.dumps(data).encode()
        method = "GET" if data is None else "POST"
        raw = (f"{method} {path} HTTP/1.0\r\nHost: localhost\r\nX-API-Key: {key}\r\n"
               f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n").encode() + body
        class MemorySocket:
            def __init__(self): self.output = bytearray()
            def makefile(self, *_): return io.BytesIO(raw)
            def sendall(self, value): self.output.extend(value)
            def settimeout(self, _): pass
        connection = MemorySocket()
        self.server.RequestHandlerClass(connection, ("127.0.0.1", 12345), self.server)
        head, result = bytes(connection.output).split(b"\r\n\r\n", 1)
        return int(head.split(b" ")[1]), result


if __name__ == "__main__":
    unittest.main()
