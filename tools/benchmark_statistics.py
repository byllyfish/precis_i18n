"""Measure latency and summarize matched workload samples."""

import gc
import math
import random
import statistics
import time


QUANTILES = ("p50_ns", "p95_ns", "p99_ns")


def _check(actual, expected, name):
    if actual != expected:
        raise ValueError("Unexpected preparation or rejection result for {}".format(name))


def _percentile(ordered, fraction):
    return ordered[math.ceil(fraction * len(ordered)) - 1]


def measure(operation, expected, name, count, warmups):
    """Measure one operation at a time, with outcome checks outside the timer."""
    for _ in range(warmups):
        _check(operation(), expected, name)
    gc.collect()
    clock = time.perf_counter_ns
    samples = [0] * count
    cpu_start = time.process_time_ns()
    for index in range(count):
        started = clock()
        result = operation()
        samples[index] = clock() - started
        _check(result, expected, name)
        del result
    cpu = time.process_time_ns() - cpu_start
    ordered = sorted(samples)
    total = sum(samples)
    return {
        "observations": count,
        "warmups": warmups,
        "p50_ns": statistics.median(ordered),
        "p95_ns": _percentile(ordered, .95),
        "p99_ns": _percentile(ordered, .99),
        "throughput_per_second": count * 1e9 / total if total else None,
        "loop_process_cpu_ns": cpu,
    }


def _bootstrap_median_interval(values):
    rng = random.Random(413785)
    draws = sorted(statistics.median(rng.choices(values, k=len(values))) for _ in range(4000))
    return [_percentile(draws, .025), _percentile(draws, .975)]


def compare_paired(upstream, candidate):
    """Resolve a paired P50 difference only beyond the practical noise floor."""
    if not all(upstream):
        raise ValueError("Timer resolution is too coarse to compare this workload.")
    changes = [new - old for old, new in zip(upstream, candidate)]
    percentages = [100 * (new / old - 1) for old, new in zip(upstream, candidate)]
    low, high = _bootstrap_median_interval(changes)
    floor = max(50, statistics.median(upstream) * .02)
    verdict = "within uncertainty"
    if all(change < 0 for change in changes) and high < -floor:
        verdict = "faster"
    elif all(change > 0 for change in changes) and low > floor:
        verdict = "slower"
    return {
        "median_delta_percent": statistics.median(percentages),
        "bootstrap_95_percent_interval": _bootstrap_median_interval(percentages),
        "bootstrap_95_ns_interval": [low, high],
        "paired_delta_percent": percentages,
        "tolerance_ns": floor,
        "verdict": verdict,
    }


def workload_summary(upstream, candidate):
    """Report medians of the per-process quantiles and the paired P50 change."""
    groups = {"upstream": upstream, "candidate": candidate}
    return {
        "quantiles": {
            name: {key: statistics.median(row[key] for row in group) for key in QUANTILES}
            for name, group in groups.items()
        },
        "p50_change": compare_paired([row["p50_ns"] for row in upstream],
                                    [row["p50_ns"] for row in candidate]),
    }
