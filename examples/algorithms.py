"""Deterministic teaching models. Python 3.11+, standard library only.

Run: python algorithms.py
These models do not implement distributed storage, consensus, or a production proxy.
"""
from dataclasses import dataclass
import hashlib
import random


@dataclass
class FakeClock:
    now: float = 0.0

    def advance(self, seconds):
        if seconds < 0:
            raise ValueError("monotonic time cannot go backward")
        self.now += seconds


class TokenBucket:
    """Single-threaded model; a real shared limiter needs atomic synchronization."""
    def __init__(self, capacity, rate, clock):
        if capacity <= 0 or rate <= 0:
            raise ValueError("capacity and refill rate must be positive")
        self.capacity, self.rate, self.clock = capacity, rate, clock
        self.tokens, self.updated = float(capacity), clock.now

    def allow(self, cost=1):
        if cost <= 0:
            raise ValueError("cost must be positive")
        now = self.clock.now
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now
        if cost > self.tokens:
            return False
        self.tokens -= cost
        return True


class TTLCache:
    """Bounded, local, non-concurrent cache with deterministic insertion eviction."""
    def __init__(self, clock, max_entries=100):
        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        self.clock, self.max_entries, self.entries = clock, max_entries, {}

    def put(self, key, value, ttl):
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.entries.pop(key, None)
        if len(self.entries) >= self.max_entries:
            self.entries.pop(next(iter(self.entries)))
        self.entries[key] = (value, self.clock.now + ttl)

    def get(self, key):
        item = self.entries.get(key)
        if item is None:
            return None
        value, expiry = item
        if self.clock.now >= expiry:
            del self.entries[key]
            return None
        return value


class CircuitOpen(Exception):
    pass


class CircuitBreaker:
    """Consecutive-failure, sequential-call demo; no concurrent probe arbitration."""
    def __init__(self, clock, threshold=3, cooldown=5):
        if threshold < 1 or cooldown <= 0:
            raise ValueError("invalid breaker policy")
        self.clock, self.threshold, self.cooldown = clock, threshold, cooldown
        self.state, self.failures, self.opened = "closed", 0, None

    def call(self, function):
        if self.state == "open":
            if self.clock.now - self.opened < self.cooldown:
                raise CircuitOpen("dependency temporarily rejected")
            self.state = "half-open"
        try:
            result = function()
        except (TimeoutError, ConnectionError):
            self.failures += 1
            if self.state == "half-open" or self.failures >= self.threshold:
                self.state, self.opened = "open", self.clock.now
            raise
        else:
            self.state, self.failures = "closed", 0
            return result


def jitter_delays(attempts=4, base=0.1, cap=0.8, seed=7):
    if attempts < 0 or base <= 0 or cap <= 0:
        raise ValueError("invalid retry policy")
    rng, window = random.Random(seed), min(base, cap)
    result = []
    for _ in range(attempts):
        result.append(rng.uniform(0, window))
        window = min(cap, window * 2)
    return result


def retry_transient(operation, clock, deadline, delays):
    """Fake-time scheduler: operation itself must honor its passed remaining budget."""
    waits = iter(delays)
    while True:
        remaining = deadline - clock.now
        if remaining <= 0:
            raise TimeoutError("total deadline exhausted")
        try:
            return operation(remaining)
        except (ConnectionError, TimeoutError):
            try:
                delay = next(waits)
            except StopIteration:
                raise
            if clock.now + delay >= deadline:
                raise TimeoutError("no budget for another attempt")
            clock.advance(delay)


def round_robin(backends, requests):
    if not backends:
        raise ValueError("no healthy backends")
    return [backends[index % len(backends)] for index in range(requests)]


def shard_for(key, shards):
    """Modulo-hash example. Resizing changes ownership; not consistent hashing."""
    if shards <= 0:
        raise ValueError("positive shard count required")
    digest = hashlib.sha256(str(key).encode()).digest()
    return int.from_bytes(digest[:8], "big") % shards


def enabled_for(subject, percentage):
    if not 0 <= percentage <= 100:
        raise ValueError("percentage outside range")
    return shard_for(subject, 100) < percentage


def apply_newer(projection, entity, version, value):
    old = projection.get(entity)
    if old is None or version > old[0]:
        projection[entity] = (version, value)
        return True
    return False


def quorum_available(reachable, cluster_size):
    """Arithmetic only: not a leader-election/consensus implementation."""
    return reachable >= cluster_size // 2 + 1


def demo():
    clock = FakeClock()
    bucket = TokenBucket(5, 2, clock)
    print("initial admission:", [bucket.allow() for _ in range(6)])
    clock.advance(0.5)
    print("after 0.5s:", bucket.allow())
    cache = TTLCache(clock)
    cache.put("product:42:v1", "book", 2)
    print("cache hit:", cache.get("product:42:v1"))
    clock.advance(2)
    print("expired:", cache.get("product:42:v1"))
    breaker = CircuitBreaker(clock)
    def fail():
        raise TimeoutError("simulated provider failure")
    for _ in range(3):
        try:
            breaker.call(fail)
        except TimeoutError:
            pass
    print("breaker after failures:", breaker.state)
    clock.advance(5)
    print("probe:", breaker.call(lambda: "recovered"), breaker.state)
    print("jitter seconds:", [round(x, 4) for x in jitter_delays()])
    print("routing:", round_robin(["A", "B", "C"], 6))
    projection = {}
    for version in [1, 3, 2]:
        apply_newer(projection, "product", version, f"value-{version}")
    print("projection:", projection)
    print("five-node quorum, reachable 2/3:", quorum_available(2, 5), quorum_available(3, 5))


if __name__ == "__main__":
    demo()
