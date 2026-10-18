"""Local transactional checkout/outbox model. Standard-library SQLite, not PostgreSQL.

Run: python orders.py. All demo data is in a temporary directory.
SQLite serializes writers here; PostgreSQL locking and isolation differ.
No real payment provider is contacted. See database.sql for PostgreSQL patterns.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory


def connect(path):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def initialize(path, stock=3):
    with closing(connect(path)) as db, db:
        db.executescript("""
        CREATE TABLE inventory(sku TEXT PRIMARY KEY, stock INTEGER NOT NULL CHECK(stock>=0));
        CREATE TABLE orders(id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, sku TEXT NOT NULL,
                            quantity INTEGER NOT NULL CHECK(quantity>0));
        CREATE TABLE operations(tenant TEXT NOT NULL, key TEXT NOT NULL, fingerprint TEXT NOT NULL,
                                order_id INTEGER NOT NULL REFERENCES orders(id),
                                PRIMARY KEY(tenant,key));
        CREATE TABLE outbox(id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id),
                            event_type TEXT NOT NULL, published INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE inbox(event_id INTEGER PRIMARY KEY);
        CREATE TABLE notifications(order_id INTEGER PRIMARY KEY, status TEXT NOT NULL);
        """)
        db.execute("INSERT INTO inventory VALUES (?,?)", ("book", stock))


def place_order(path, tenant, key, sku="book", quantity=1, inject_failure=False):
    if not tenant or not key or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("tenant, operation key, and positive integer quantity required")
    payload = json.dumps({"sku": sku, "quantity": quantity}, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(payload.encode()).hexdigest()
    with closing(connect(path)) as db:
        try:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT fingerprint,order_id FROM operations WHERE tenant=? AND key=?",
                             (tenant, key)).fetchone()
            if old:
                if old[0] != fingerprint:
                    raise ValueError("idempotency key reused with different payload")
                db.commit()
                return old[1]
            result = db.execute("UPDATE inventory SET stock=stock-? WHERE sku=? AND stock>=?",
                                (quantity, sku, quantity))
            if result.rowcount != 1:
                raise ValueError("insufficient inventory or unknown SKU")
            order_id = db.execute("INSERT INTO orders(tenant,sku,quantity) VALUES (?,?,?)",
                                  (tenant, sku, quantity)).lastrowid
            db.execute("INSERT INTO operations VALUES (?,?,?,?)", (tenant, key, fingerprint, order_id))
            db.execute("INSERT INTO outbox(order_id,event_type) VALUES (?,?)", (order_id, "OrderPlaced"))
            if inject_failure:
                raise RuntimeError("simulated crash before commit")
            db.commit()
            return order_id
        except BaseException:
            db.rollback()
            raise


def consume_notification(path, event_id, order_id):
    """Inbox and LOCAL effect share one transaction. External email is not atomic here."""
    with closing(connect(path)) as db, db:
        inserted = db.execute("INSERT OR IGNORE INTO inbox VALUES (?)", (event_id,)).rowcount
        if not inserted:
            return False
        db.execute("INSERT INTO notifications VALUES (?,?)", (order_id, "ready-to-send"))
        return True


def counts(path):
    with closing(connect(path)) as db:
        return {name: db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                for name in ("orders", "operations", "outbox", "inbox", "notifications")}


def backup(path, target):
    with closing(connect(path)) as source, closing(connect(target)) as destination:
        source.backup(destination)


def demo():
    with TemporaryDirectory() as folder:
        path = Path(folder) / "shop.db"
        initialize(path)
        with ThreadPoolExecutor(max_workers=4) as pool:
            result = list(pool.map(lambda _: place_order(path, "tenant-a", "checkout-1"), range(4)))
        print("concurrent replay order IDs:", result)
        print("first event:", consume_notification(path, 1, result[0]))
        print("duplicate event:", consume_notification(path, 1, result[0]))
        print("row counts:", counts(path))
        restored = Path(folder) / "restored.db"
        backup(path, restored)
        print("backup restores same counts:", counts(path) == counts(restored))


if __name__ == "__main__":
    demo()
