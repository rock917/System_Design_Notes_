"""Failure-oriented, in-memory messaging and Saga simulations. No real broker.
Run: python messaging.py. Process loss discards these model objects.
"""
from collections import deque
from dataclasses import dataclass


@dataclass
class Job:
    event_id: str
    payload: str
    attempts: int = 0


def process_queue(jobs, max_attempts=3):
    queue, completed, dead = deque(jobs), set(), []
    effect_count = 0
    while queue:
        job = queue.popleft()
        if job.event_id in completed:
            continue
        job.attempts += 1
        if job.payload == "poison":
            if job.attempts < max_attempts:
                queue.append(job)
            else:
                dead.append(job)
            continue
        effect_count += 1
        completed.add(job.event_id)
    return effect_count, completed, dead


class OrderSaga:
    """Persist these fields in a real workflow store. Provider outcome is simulated."""
    def __init__(self):
        self.state = "new"
        self.reserved = False
        self.history = ["new"]

    def transition(self, state):
        self.state = state
        self.history.append(state)

    def start(self, payment_outcome, compensation_fails=False):
        if self.state != "new":
            return self.state
        self.reserved = True
        self.transition("reserved")
        if payment_outcome == "confirmed":
            self.transition("confirmed")
        elif payment_outcome == "unknown":
            self.transition("reconcile-payment")
        elif payment_outcome == "declined":
            self.transition("compensating")
            if compensation_fails:
                self.transition("compensation-pending")
            else:
                self.release()
        else:
            raise ValueError("invalid provider outcome")
        return self.state

    def release(self):
        if self.state not in {"compensating", "compensation-pending"}:
            raise ValueError("cannot release before a known failure decision")
        self.reserved = False
        self.transition("rejected")


def settle_once(completed_periods, business_date):
    """Set model only: a real scheduler needs a durable unique constraint."""
    if business_date in completed_periods:
        return False
    completed_periods.add(business_date)
    return True


def demo():
    effects, completed, dead = process_queue([Job("a", "receipt"), Job("a", "receipt"), Job("b", "poison")])
    print("effects:", effects, "completed:", sorted(completed))
    print("DLQ:", [(job.event_id, job.attempts) for job in dead])
    for outcome in ["confirmed", "declined", "unknown"]:
        saga = OrderSaga()
        saga.start(outcome)
        print("Saga", outcome, ":", " -> ".join(saga.history), "reserved:", saga.reserved)
    runs = set()
    print("same scheduled period:", settle_once(runs, "2026-10-18"), settle_once(runs, "2026-10-18"))


if __name__ == "__main__":
    demo()
