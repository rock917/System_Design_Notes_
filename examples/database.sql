-- PostgreSQL 16+ teaching lab. Run only in a disposable database you own.
-- psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database.sql
-- Creates the isolated handbook_lab schema; does not drop existing data.
-- A second run fails intentionally if the schema already exists.
CREATE SCHEMA handbook_lab;
SET search_path TO handbook_lab;
CREATE TABLE customers (
  id bigint PRIMARY KEY,
  name text NOT NULL
);
CREATE TABLE orders (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id bigint NOT NULL REFERENCES customers(id),
  total_minor bigint NOT NULL CHECK (total_minor >= 0),
  currency char(3) NOT NULL DEFAULT 'INR',
  status text NOT NULL DEFAULT 'pending',
  created_at timestamptz NOT NULL DEFAULT now(),
  version bigint NOT NULL DEFAULT 1
);
INSERT INTO customers SELECT g, 'Customer ' || g FROM generate_series(1,1000) g;
INSERT INTO orders(customer_id,total_minor,created_at)
SELECT (g % 1000)+1, 1000+(g % 5000),
       timestamptz '2026-01-01 00:00:00+00' + g * interval '1 minute'
FROM generate_series(1,100000) g;
ANALYZE orders;
-- ANALYZE executes this SELECT. Use caution with mutating statements.
EXPLAIN (ANALYZE, BUFFERS)
SELECT id,total_minor FROM orders WHERE customer_id=7 ORDER BY created_at DESC LIMIT 20;
CREATE INDEX orders_customer_time ON orders(customer_id,created_at DESC);
ANALYZE orders;
EXPLAIN (ANALYZE, BUFFERS)
SELECT id,total_minor FROM orders WHERE customer_id=7 ORDER BY created_at DESC LIMIT 20;

-- One join or two bounded queries replace a query inside each order loop.
SELECT o.id,c.name,o.total_minor FROM orders o JOIN customers c ON c.id=o.customer_id
WHERE o.customer_id=7 ORDER BY o.created_at DESC LIMIT 20;

-- Optimistic concurrency: second execution with version=1 affects zero rows.
UPDATE orders SET status='confirmed',version=version+1 WHERE id=1 AND version=1 RETURNING id,version;
UPDATE orders SET status='confirmed',version=version+1 WHERE id=1 AND version=1 RETURNING id,version;

CREATE TABLE inventory(sku text PRIMARY KEY, stock integer NOT NULL CHECK(stock>=0));
INSERT INTO inventory VALUES ('book',1),('pen',10);
-- A guarded update atomically enforces this single-row stock invariant.
BEGIN;
UPDATE inventory SET stock=stock-1 WHERE sku='book' AND stock>0 RETURNING stock;
COMMIT;

-- Short pessimistic critical section. Never call a payment provider while holding this lock.
BEGIN;
SET LOCAL lock_timeout='1s';
SELECT stock FROM inventory WHERE sku='pen' FOR UPDATE;
UPDATE inventory SET stock=stock-1 WHERE sku='pen';
COMMIT;

-- Partitioning stays inside this database; it does not create independent shards.
CREATE TABLE events (
  occurred_at timestamptz NOT NULL,
  id bigint NOT NULL,
  payload jsonb NOT NULL,
  PRIMARY KEY(occurred_at,id)
) PARTITION BY RANGE(occurred_at);
CREATE TABLE events_oct PARTITION OF events
FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-11-01 00:00:00+00');
CREATE TABLE events_nov PARTITION OF events
FOR VALUES FROM ('2026-11-01 00:00:00+00') TO ('2026-12-01 00:00:00+00');
INSERT INTO events VALUES ('2026-10-18 10:00:00+00',1,'{"type":"OrderPlaced"}');
EXPLAIN SELECT * FROM events WHERE occurred_at>='2026-10-01' AND occurred_at<'2026-11-01';

-- Expand phase. Keep old column through all supported code and rollback windows.
ALTER TABLE customers ADD COLUMN display_name text;
UPDATE customers SET display_name=name WHERE id BETWEEN 1 AND 100 AND display_name IS NULL;
-- Production backfill: commit bounded key ranges, checkpoint, observe locks/lag, then continue.
-- Contract phase is deliberately not executed: do not drop name until compatibility is proven.

-- Transactional outbox skeleton for application use.
CREATE TABLE outbox (
  event_id uuid PRIMARY KEY,
  aggregate_id bigint NOT NULL,
  schema_version integer NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz
);
-- Order changes and this INSERT must share a transaction. Relay publication may repeat.
-- A separate consumer database uses an inbox primary key in the same transaction as its local effect.
SELECT count(*) AS order_count FROM orders;
