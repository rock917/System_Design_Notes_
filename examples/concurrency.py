"""Bounded-resource and concurrency models, Python standard library.
Run: python concurrency.py. Deliberate schedules replace flaky timing-based demos.
"""
from contextlib import contextmanager
import math
import queue
import tracemalloc


class Pool:
    """Toy pool of tokens, NOT database connections."""
    def __init__(self, size):
        if size <= 0:
            raise ValueError("positive size required")
        self.available = queue.Queue(maxsize=size)
        for number in range(size):
            self.available.put(number)

    @contextmanager
    def acquire(self, timeout=0.1):
        token = self.available.get(timeout=timeout)
        try:
            yield token
        finally:
            self.available.put(token)


class FencedLedger:
    """Resource-side enforcement model; token issuance must be safe elsewhere."""
    def __init__(self):
        self.last_token, self.value = -1, None

    def write(self, token, value):
        if token < self.last_token:
            raise ValueError("stale fencing token")
        self.last_token, self.value = token, value


def queue_model(arrivals_per_second, service_per_second, seconds, capacity):
    backlog, rejected, completed = 0, 0, 0
    history = []
    for _ in range(seconds):
        # Discrete-time model: arrivals admitted before service in each one-second tick.
        accepted = min(arrivals_per_second, max(0, capacity - backlog))
        rejected += arrivals_per_second - accepted
        backlog += accepted
        served = min(backlog, service_per_second)
        completed += served
        backlog -= served
        history.append(backlog)
    return {"backlog": backlog, "rejected": rejected, "completed": completed, "history": history}


def desired_workers(arrival_rate, rate_per_worker, target_utilization=0.7):
    if arrival_rate < 0 or rate_per_worker <= 0 or not 0 < target_utilization <= 1:
        raise ValueError("invalid capacity model")
    return math.ceil(arrival_rate / (rate_per_worker * target_utilization))


def lost_update_schedule():
    stock = 1
    read_a, read_b = stock, stock
    stock = read_a - 1
    stock = read_b - 1
    return {"sales": 2, "final_stock": stock}


def has_cycle(graph):
    visiting, finished = set(), set()
    def visit(node):
        if node in visiting:
            return True
        if node in finished:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, [])):
            return True
        visiting.remove(node)
        finished.add(node)
        return False
    return any(visit(node) for node in graph)


def retention_demo():
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    retained = [bytearray(1024) for _ in range(2000)]
    during = tracemalloc.get_traced_memory()[0]
    retained.clear()
    after = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return {"grew": during > before + 1_000_000, "released": after < during / 2}


def demo():
    pool = Pool(1)
    try:
        with pool.acquire():
            raise RuntimeError("simulated query error")
    except RuntimeError:
        pass
    print("pool token returned:", pool.available.qsize() == 1)
    ledger = FencedLedger()
    ledger.write(9, "new owner")
    try:
        ledger.write(8, "paused old owner")
    except ValueError as error:
        print("fencing:", str(error))
    result = queue_model(120, 100, 60, 1000)
    print("bounded queue:", {key: value for key, value in result.items() if key != "history"})
    print("workers at 70% target:", desired_workers(150, 25))
    print("lost update:", lost_update_schedule())
    print("deadlock cycle:", has_cycle({"T1": ["T2"], "T2": ["T1"]}))
    print("retention:", retention_demo())


if __name__ == "__main__":
    demo()
