"""Replay the published PRECIS benchmarks on two local source checkouts."""

import argparse
from collections import Counter
from functools import partial
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import sysconfig
import unicodedata


TOOLS = Path(__file__).resolve().parent
# A worker invoked with -I starts without the script directory on sys.path.
sys.path.insert(0, str(TOOLS))
from benchmark_statistics import measure, workload_summary
from benchmark_workloads import DIFFERING_OUTCOMES, LONG_WORKLOAD_SAMPLES, cases, execute


ORDERS = (("upstream", "candidate"), ("candidate", "upstream")) * 3


def runtime_identity():
    return {
        "implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "implementation_version": ".".join(map(str, sys.implementation.version[:3])),
        "architecture": platform.machine(),
        "host": platform.platform(),
        "unicode": unicodedata.unidata_version,
        "gil_enabled": getattr(sys, "_is_gil_enabled", lambda: True)(),
    }


def exact_outcome(profile, value):
    try:
        return {"value": profile.enforce(value)}
    except UnicodeEncodeError as error:
        return {"error": type(error).__name__, "encoding": error.encoding, "object": error.object,
                "start": error.start, "end": error.end, "reason": error.reason}


def worker(checkout, lane, seed, comparable):
    checkout = Path(checkout).resolve()
    sys.path.insert(0, str(checkout))
    import precis_i18n

    if Path(precis_i18n.__file__).resolve() != checkout / "precis_i18n" / "__init__.py":
        raise ValueError("The worker imported PRECIS from a different checkout.")
    fixtures = cases()
    profiles = {name: precis_i18n.get_profile(name) for name in sorted({case.profile for case in fixtures})}
    outcomes = {}
    for case in fixtures:
        profile = profiles[case.profile]
        expected = case.old if lane == "upstream" else case.expected
        outcome = exact_outcome(profile, case.value)
        compact = outcome.get("value")
        if "error" in outcome:
            reason = outcome["reason"]
            prefix = "DISALLOWED/"
            compact = ("reject", reason[len(prefix):] if reason.startswith(prefix) else reason)
        if compact != expected:
            raise ValueError("Unexpected {} result for {}".format(lane, case.name))
        outcomes[case.name] = outcome
    record = {"runtime": runtime_identity(), "outcomes": outcomes}
    if comparable is None:
        return record

    random.Random(seed).shuffle(fixtures)
    timings = {}
    for case in fixtures:
        if case.name in comparable:
            expected = case.old if lane == "upstream" else case.expected
            operation = partial(execute, profiles[case.profile], case.value)
            count = LONG_WORKLOAD_SAMPLES.get(case.name, 10000)
            warmups = 64 if case.name in LONG_WORKLOAD_SAMPLES else 512
            timings[case.name] = measure(operation, expected, case.name, count, warmups)
    record.update(timings=timings, order=list(timings),
                  timer=measure(lambda: None, None, "timer overhead", 30000, 512))
    return record


def run_worker(checkout, lane, seed=0, comparable=None):
    options = []
    if sysconfig.get_config_var("Py_GIL_DISABLED"):
        options = ["-X", "gil={}".format(int(runtime_identity()["gil_enabled"]))]
    command = [sys.executable, "-IB", *options, __file__, "_worker", str(checkout), lane,
               str(seed), json.dumps(comparable)]
    environment = {**os.environ, "LC_ALL": "C", "TZ": "UTC"}
    return json.loads(subprocess.check_output(command, text=True, env=environment))


def run_benchmark(upstream, candidate, check_only):
    locations = {"upstream": upstream, "candidate": candidate}
    probes = {lane: run_worker(path, lane) for lane, path in locations.items()}
    baseline, revised = probes["upstream"], probes["candidate"]
    if baseline["runtime"] != revised["runtime"] or baseline["runtime"] != runtime_identity():
        raise ValueError("The two worker processes reported different runtime configurations.")
    differences = {name for name, outcome in baseline["outcomes"].items()
                   if revised["outcomes"][name] != outcome}
    if differences != DIFFERING_OUTCOMES:
        raise ValueError("Unexpected differences in benchmark outcomes: {}".format(sorted(differences)))
    comparable = sorted(set(baseline["outcomes"]) - differences)
    report = {
        "runtime": baseline["runtime"],
        "checkouts": {lane: str(path) for lane, path in locations.items()},
        "comparable": comparable,
        "excluded": sorted(differences | {"concurrent-shared-profiles"}),
        "outcomes": {lane: probe["outcomes"] for lane, probe in probes.items()},
    }
    if check_only:
        return report

    pairs = []
    for index, order in enumerate(ORDERS):
        seed = 892981 + index
        pair = {lane: run_worker(locations[lane], lane, seed, comparable) for lane in order}
        for lane, record in pair.items():
            if record["runtime"] != baseline["runtime"] or record["outcomes"] != probes[lane]["outcomes"]:
                raise ValueError("Worker configuration or outcome changed during timing.")
        if pair["upstream"]["order"] != pair["candidate"]["order"]:
            raise ValueError("Paired workers ran workloads in different orders.")
        pairs.append({"order": order, "seed": seed, "lanes": pair})
        print("Completed pair {}/{}".format(index + 1, len(ORDERS)), file=sys.stderr, flush=True)

    workloads = {
        name: workload_summary(*[[pair["lanes"][lane]["timings"][name] for pair in pairs]
                                  for lane in locations])
        for name in comparable
    }
    verdicts = Counter(row["p50_change"]["verdict"] for row in workloads.values())
    report.update(
        pairs=pairs, workloads=workloads,
        verdicts={key: verdicts[key] for key in ("faster", "within uncertainty", "slower")},
        median_p50_change_percent=statistics.median(row["p50_change"]["median_delta_percent"]
                                                  for row in workloads.values()),
    )
    return report


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "_worker":
        checkout, lane, seed, comparable = sys.argv[2:]
        print(json.dumps(worker(checkout, lane, int(seed), json.loads(comparable))))
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True, help="path to the upstream PRECIS checkout")
    parser.add_argument("--candidate", type=Path, default=TOOLS.parent, help="path to the contribution checkout")
    parser.add_argument("--output", type=Path, required=True, help="write a JSON report to this path")
    parser.add_argument("--check", action="store_true", help="check the fixtures and runtime without timing")
    args = parser.parse_args()
    report = run_benchmark(args.upstream.resolve(), args.candidate.resolve(), args.check)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Verified {} comparable workloads. Report: {}".format(len(report["comparable"]), args.output))


if __name__ == "__main__":
    main()
