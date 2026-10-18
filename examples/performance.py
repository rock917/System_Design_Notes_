"""Reproducible arithmetic, not hardware benchmarks. Run: python performance.py."""
import math
import statistics


def percentile(samples, quantile):
    if not samples or not 0 < quantile <= 1:
        raise ValueError("nonempty samples and quantile in (0,1] required")
    ordered = sorted(samples)
    return ordered[max(0, math.ceil(len(ordered) * quantile) - 1)]


def budget(good, eligible, target):
    if not 0 <= good <= eligible or eligible <= 0 or not 0 < target < 1:
        raise ValueError("invalid SLO inputs")
    allowed_bad = eligible * (1 - target)
    bad = eligible - good
    return {"success_ratio": good / eligible, "allowed_bad": allowed_bad,
            "remaining_bad": allowed_bad - bad, "burn_rate": (bad / eligible) / (1 - target)}


def fanout_slow_probability(slow_probability, branches):
    if not 0 <= slow_probability <= 1 or branches < 0:
        raise ValueError("invalid probability model")
    return 1 - (1 - slow_probability) ** branches


def critical_path(graph, durations, node):
    """DAG only: a duration per node plus maximum child path; shared work not double-counted."""
    return durations[node] + max((critical_path(graph, durations, child)
                                  for child in graph.get(node, [])), default=0)


def capacity(arrival_rate, average_seconds):
    if arrival_rate < 0 or average_seconds < 0:
        raise ValueError("negative workload")
    return arrival_rate * average_seconds


def demo():
    samples = [20] * 980 + [2000] * 20
    print("mean ms:", statistics.mean(samples))
    print("P50/P95/P99 ms:", *(percentile(samples, q) for q in (0.5, 0.95, 0.99)))
    print("100-branch slow chance:", round(fanout_slow_probability(0.01, 100), 4))
    print("in-flight at 500/s and 0.2s:", capacity(500, 0.2))
    print("SLO:", {key: round(value, 4) for key, value in budget(9900, 10000, 0.999).items()})
    graph = {"gateway": ["catalog", "recommendation"], "catalog": ["database"]}
    durations = {"gateway": 10, "catalog": 20, "database": 50, "recommendation": 100}
    print("parallel critical path ms:", critical_path(graph, durations, "gateway"))


if __name__ == "__main__":
    demo()
