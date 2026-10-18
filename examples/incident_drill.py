"""Offline incident decision exercise. Run: python incident_drill.py."""
EVIDENCE = [
    ("09:00", "Release B reaches 25% of checkout traffic."),
    ("09:04", "B P99 rises; database CPU remains low; pool acquisition wait rises."),
    ("09:06", "Traces show B holds a DB connection while awaiting the payment provider."),
    ("09:08", "Feature flag disables the new path; no schema contraction occurred."),
    ("09:12", "Success and latency recover; 14 payment outcomes remain unknown."),
    ("09:20", "Provider operation-ID reconciliation resolves all 14 outcomes."),
]


def recovery_complete(success_restored, queue_fresh, unknown_payments):
    return success_restored and queue_fresh and unknown_payments == 0


def demo():
    for timestamp, event in EVIDENCE:
        print(timestamp, event)
    print("At 09:12 complete:", recovery_complete(True, True, 14))
    print("At 09:20 complete:", recovery_complete(True, True, 0))
    print("Action: add a test proving DB connections are released before provider I/O.")
    print("Owner: checkout team. Verification: failure-injected integration test plus rollout telemetry.")


if __name__ == "__main__":
    demo()
