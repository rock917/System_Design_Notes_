"""Safe, local defensive demonstrations. No offensive network requests.
Run: python security.py. HMAC is a webhook example, NOT a home-made JWT system.
"""
from contextlib import closing
import hashlib
import hmac
import html
import json
import sqlite3
from urllib.parse import urlsplit


def authorize(principal, resource, action):
    tenant = principal.get("tenant")
    return (isinstance(tenant, str) and bool(tenant)
            and tenant == resource.get("tenant")
            and action in principal.get("permissions", set()))


def csrf_valid(expected, supplied):
    return (isinstance(expected, str) and isinstance(supplied, str)
            and bool(expected and supplied)
            and hmac.compare_digest(expected.encode('utf-8'), supplied.encode('utf-8')))


def cors_origin(origin):
    return origin if origin in {"https://app.example", "https://admin.example"} else None


def sign_webhook(secret, timestamp, body):
    message = str(timestamp).encode() + b"." + body
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def verify_webhook(secret, timestamp, body, signature, now, tolerance=300):
    if type(timestamp) is not int or abs(now - timestamp) > tolerance:
        return False
    expected = sign_webhook(secret, timestamp, body)
    return (isinstance(signature, str) and len(signature) == 64
            and hmac.compare_digest(expected.encode('ascii'), signature.encode('utf-8')))


def allowed_partner_url(url):
    """Parsing allowlist ONLY. No fetching, DNS-rebinding or actual-IP defense here.
    A real fetcher additionally restricts egress, redirects, resolved/connected IPs,
    credentials, response size, and time. This example accepts one fixed partner.
    """
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == "https" and parsed.hostname == "images.example"
                and parsed.port in (None, 443) and not parsed.username
                and not parsed.password and not parsed.fragment)
    except (ValueError, TypeError):
        return False


def safe_name_search(name):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE people(id INTEGER PRIMARY KEY, name TEXT)")
        db.executemany("INSERT INTO people(name) VALUES (?)", [("O'Reilly",), ("Alice",)])
        return db.execute("SELECT name FROM people WHERE name = ?", (name,)).fetchall()


def sanitized_log(record):
    """Allowlist beats a blacklist for this small event contract."""
    allowed = {key: record[key] for key in ("event", "trace_id", "order_id", "status") if key in record}
    return json.dumps(allowed, sort_keys=True)


def demo():
    print("bound apostrophe query:", safe_name_search("O'Reilly"))
    print("SQL-looking text returns:", safe_name_search("' OR '1'='1"))
    print("HTML text encoding:", html.escape('<b>review</b>'))
    secret, body, timestamp = b"local-test-secret-only", b'{"event_id":"e1"}', 1000
    signature = sign_webhook(secret, timestamp, body)
    print("valid/tampered webhook:", verify_webhook(secret, timestamp, body, signature, 1001),
          verify_webhook(secret, timestamp, body + b" ", signature, 1001))
    print("partner/lookalike:", allowed_partner_url("https://images.example/a.png"),
          allowed_partner_url("https://images.example.attacker.test/a.png"))
    print("cross-tenant authorization:", authorize({"tenant": "a", "permissions": {"write"}},
                                                   {"tenant": "b"}, "write"))
    print("safe log:", sanitized_log({"event": "order.accepted", "order_id": 1, "token": "not-logged"}))


if __name__ == "__main__":
    demo()
