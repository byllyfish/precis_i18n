# PRECIS preparation benchmarks

These measurements compare upstream PRECIS-i18n with the implementation in this contribution.

- Upstream commit `865faedc9d3e4f3a0adb15bba29f1dfe630eec2c`.
- Candidate `precis_i18n/` Git tree `c20d3d07a370e02e985c23bd5adf81fa85b3d7a1`.
- Host macOS 15.4.1. The architecture column identifies each interpreter build.
- Each row compares the same native Unicode configuration and interpreter build on both sides.

## Method

- Each interpreter ran six balanced pairs of fresh processes, with each revision going first in
  three pairs. The two processes in a pair ran workloads in the same shuffled order.
- A workload is comparable when both revisions return the same value or reject with the same
  exception type, encoding, rejected text, offsets, and reason.
- Ordinary workloads used 512 warmups and 10,000 timed calls per process. Long workloads
  used 64 warmups and the sample counts below. Each timing covers one preparation or class
  admission call, including the benchmark wrapper.
- Each reported latency quantile is the median of the six per-process quantiles. Time values
  are in microseconds. Timer overhead is reported separately and included in the timings.
- The P50 change is the median of the six paired percentage changes. The 95% interval is a
  descriptive bootstrap interval over those six changes. A verdict requires all six paired
  absolute changes to have the same sign and their 95% bootstrap interval to clear
  `max(50 ns, 2% of the upstream P50)`. Other comparisons are within uncertainty.

The Kelvin-sign and uppercase middle-dot cases were excluded because preparation outcomes changed.
The aggregate shared-profile batch was excluded because it includes those inputs.

| Long workload | Timed calls per process |
| --- | ---: |
| `password-combining-1025` | 1,200 |
| `context-katakana-16` | 2,400 |
| `context-katakana-64` | 512 |
| `context-katakana-256` | 192 |
| `context-arabic-64` | 1,200 |
| `context-extended-arabic-64` | 1,200 |
| `context-joiners-127` | 1,200 |

## Summary

| Runtime | Architecture | Unicode | Faster | Within uncertainty | Slower | Median P50 change | Timer overhead upstream / candidate (ns) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| CPython 3.7.17 | x86_64 | 11.0.0 | 27 | 0 | 0 | -52.7% | 125.0 / 125.0 |
| CPython 3.8.20 | arm64 | 12.1.0 | 27 | 0 | 0 | -54.0% | 42.0 / 42.0 |
| CPython 3.9.25 | arm64 | 13.0.0 | 27 | 0 | 0 | -52.0% | 42.0 / 42.0 |
| CPython 3.10.22 | arm64 | 13.0.0 | 27 | 0 | 0 | -52.5% | 42.0 / 42.0 |
| CPython 3.11.17 | arm64 | 14.0.0 | 27 | 0 | 0 | -43.6% | 42.0 / 42.0 |
| CPython 3.12.15 | arm64 | 15.0.0 | 25 | 1 | 1 | -40.5% | 42.0 / 42.0 |
| CPython 3.13.16 | arm64 | 15.1.0 | 26 | 1 | 0 | -46.5% | 42.0 / 42.0 |
| CPython 3.14.8 | arm64 | 16.0.0 | 25 | 2 | 0 | -43.6% | 42.0 / 42.0 |
| CPython 3.15.2 | arm64 | 17.0.0 | 26 | 1 | 0 | -44.1% | 42.0 / 42.0 |
| PyPy 3.10.16 (PyPy 7.3.19) | arm64 | 13.0.0 | 13 | 3 | 11 | -14.1% | 0.0 / 0.0 |
| PyPy 3.11.15 (PyPy 7.3.23) | arm64 | 14.0.0 | 13 | 3 | 11 | -10.8% | 42.0 / 42.0 |
| CPython 3.14.8 (GIL disabled) | arm64 | 16.0.0 | 26 | 1 | 0 | -42.5% | 42.0 / 42.0 |

The median change above gives each comparable workload equal weight.
Negative changes indicate lower latency. PyPy timings reflect the same warmup budget as CPython.

## Reproduce the benchmark

From the contribution checkout, make a local worktree at the upstream commit
listed above. Use the Python executable of the runtime you want to measure.

```sh
git worktree add --detach /tmp/precis-upstream 865faedc9d3e4f3a0adb15bba29f1dfe630eec2c
python -IB tools/benchmark_precis.py \
  --upstream /tmp/precis-upstream \
  --output /tmp/precis-benchmark.json
```

The runner uses its own checkout as the candidate by default. Supply another
checkout with `--candidate /path/to/checkout`. Add `--check` to verify the
runtime and all fixture outcomes without collecting timings. The JSON output
includes the per-process quantiles, paired P50 changes, and resolved verdicts.

The same runner is available through the Nox matrix.

```sh
nox -s benchmark-3.10 -- --upstream /tmp/precis-upstream --output /tmp/precis-3.10.json
```

Use one report path per runtime. For free-threaded CPython, launch the runner
with `python3.14t -X gil=0 -IB` to keep the GIL disabled in each worker process.

## Workload inputs

Each input is shown as a Python string literal or expression.

| Workload | Profile | Input |
| --- | --- | --- |
| `username-ascii` | `UsernameCaseMapped` | `"User-42"` |
| `username-unicode` | `UsernameCaseMapped` | `"\u00c9lise-\u6f22\u5b57"` |
| `username-width` | `UsernameCaseMapped` | `"\uff35\uff53\uff45\uff52\uff14\uff12"` |
| `username-katakana-width` | `UsernameCaseMapped` | `"\uff76\uff9e"` |
| `username-lowercase` | `UsernameCaseMapped` | `"STRA\u1e9eE"` |
| `username-tolower-alias` | `UsernameCaseMapped:ToLower` | `"STRA\u1e9eE"` |
| `username-casefold` | `UsernameCaseMapped:CaseFold` | `"Stra\u00dfe"` |
| `username-preserved` | `UsernameCasePreserved` | `"Stra\u00dfe"` |
| `username-nfc` | `UsernameCasePreserved` | `"E\u0301clair"` |
| `username-mixed-script` | `UsernameCaseMapped` | `"\u0391lpha\u6f22\u5b57"` |
| `password-opaque` | `OpaqueString` | `"\uff21\u00a0Passe\u0301"` |
| `password-combining-1025` | `OpaqueString` | `"x" + "\u0315\u0300" * 512` |
| `nickname-mapped` | `NicknameCaseMapped` | `"  \uff21nna\u00a0  M.  "` |
| `nickname-tolower-alias` | `NicknameCaseMapped:ToLower` | `"Stra\u00dfe"` |
| `nickname-casefold` | `NicknameCaseMapped:CaseFold` | `"Stra\u00dfe"` |
| `nickname-preserved` | `NicknameCasePreserved` | `" \uff21nna  M.\u3000"` |
| `nickname-alias` | `Nickname` | `"  \uff21nna\u00a0  M.  "` |
| `identifier-class` | `IdentifierClass` | `"Code-42"` |
| `freeform-class` | `FreeFormClass` | `"User name"` |
| `reject-bidi` | `UsernameCaseMapped` | `"a\u05d0"` |
| `reject-password-control` | `OpaqueString` | `"a\u0000"` |
| `context-katakana-16` | `IdentifierClass` | `"\u30fb" * 15 + "\u30ab"` |
| `context-katakana-64` | `IdentifierClass` | `"\u30fb" * 63 + "\u30ab"` |
| `context-katakana-256` | `IdentifierClass` | `"\u30fb" * 255 + "\u30ab"` |
| `context-arabic-64` | `IdentifierClass` | `"\u0661" * 64` |
| `context-extended-arabic-64` | `IdentifierClass` | `"\u06f1" * 64` |
| `context-joiners-127` | `IdentifierClass` | `"\u0628\u200c" * 63 + "\u0628"` |

## Detailed results

### CPython 3.7.17

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 15.521 / 16.459 / 24.938 | 2.375 / 2.541 / 2.646 | -84.6% [-85.1%, -84.3%] | faster |
| `username-unicode` | 26.666 / 28.416 / 50.042 | 14.521 / 15.479 / 20.729 | -45.6% [-48.0%, -44.0%] | faster |
| `username-width` | 18.250 / 19.334 / 32.980 | 3.125 / 3.292 / 3.500 | -82.8% [-83.3%, -82.4%] | faster |
| `username-katakana-width` | 12.396 / 13.291 / 18.125 | 10.667 / 11.354 / 15.979 | -14.5% [-16.0%, -12.0%] | faster |
| `username-lowercase` | 13.479 / 14.333 / 17.730 | 8.666 / 9.271 / 11.958 | -36.5% [-38.8%, -33.1%] | faster |
| `username-tolower-alias` | 13.541 / 14.312 / 18.333 | 8.666 / 9.250 / 11.896 | -35.5% [-38.4%, -33.5%] | faster |
| `username-casefold` | 15.104 / 15.917 / 21.166 | 4.875 / 5.167 / 5.542 | -67.6% [-69.3%, -66.5%] | faster |
| `username-preserved` | 13.041 / 13.812 / 16.938 | 4.209 / 4.479 / 4.729 | -67.6% [-68.7%, -66.7%] | faster |
| `username-nfc` | 16.834 / 17.855 / 27.875 | 5.375 / 5.750 / 6.104 | -68.1% [-69.4%, -67.2%] | faster |
| `username-mixed-script` | 25.271 / 27.041 / 49.459 | 15.791 / 16.750 / 25.021 | -37.4% [-41.2%, -35.8%] | faster |
| `password-opaque` | 20.250 / 21.542 / 35.458 | 12.354 / 13.125 / 17.250 | -38.5% [-41.3%, -37.7%] | faster |
| `password-combining-1025` | 5,667.542 / 5,911.875 / 6,215.208 | 1,489.521 / 1,585.292 / 1,648.521 | -73.7% [-74.1%, -73.3%] | faster |
| `nickname-mapped` | 19.646 / 20.896 / 39.062 | 12.188 / 13.021 / 18.688 | -37.7% [-40.1%, -36.8%] | faster |
| `nickname-tolower-alias` | 13.813 / 14.708 / 18.791 | 10.896 / 11.542 / 14.688 | -21.1% [-24.3%, -18.6%] | faster |
| `nickname-casefold` | 14.875 / 15.771 / 21.791 | 8.979 / 9.584 / 12.959 | -39.6% [-42.3%, -38.5%] | faster |
| `nickname-preserved` | 19.084 / 20.396 / 39.292 | 11.541 / 12.292 / 17.396 | -39.1% [-41.3%, -37.9%] | faster |
| `nickname-alias` | 19.625 / 20.896 / 38.000 | 12.146 / 13.000 / 18.604 | -38.0% [-40.5%, -36.4%] | faster |
| `identifier-class` | 6.688 / 7.104 / 7.396 | 1.000 / 1.042 / 1.125 | -84.8% [-85.3%, -84.5%] | faster |
| `freeform-class` | 11.688 / 12.354 / 14.791 | 0.979 / 1.042 / 1.105 | -91.7% [-92.2%, -91.4%] | faster |
| `reject-bidi` | 5.896 / 6.333 / 7.104 | 4.729 / 5.000 / 5.479 | -20.4% [-23.5%, -18.4%] | faster |
| `reject-password-control` | 9.312 / 9.854 / 11.979 | 4.354 / 4.687 / 8.271 | -52.7% [-55.2%, -52.3%] | faster |
| `context-katakana-16` | 274.927 / 325.771 / 372.854 | 36.354 / 38.958 / 63.001 | -86.8% [-87.2%, -86.3%] | faster |
| `context-katakana-64` | 4,370.594 / 4,544.292 / 4,701.042 | 136.656 / 161.583 / 196.833 | -96.8% [-96.9%, -96.7%] | faster |
| `context-katakana-256` | 68,041.188 / 69,691.500 / 75,176.333 | 553.812 / 630.625 / 704.000 | -99.2% [-99.2%, -99.2%] | faster |
| `context-arabic-64` | 963.562 / 1,056.500 / 1,118.771 | 70.375 / 83.125 / 111.000 | -92.7% [-92.9%, -92.0%] | faster |
| `context-extended-arabic-64` | 1,018.646 / 1,098.187 / 1,171.604 | 79.344 / 91.250 / 127.771 | -92.2% [-92.4%, -91.7%] | faster |
| `context-joiners-127` | 602.438 / 692.562 / 749.230 | 449.948 / 524.062 / 564.834 | -25.1% [-27.7%, -23.2%] | faster |

### CPython 3.8.20

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 6.750 / 7.125 / 7.417 | 0.958 / 1.000 / 1.083 | -86.0% [-86.4%, -85.7%] | faster |
| `username-unicode` | 11.334 / 12.021 / 15.334 | 5.667 / 6.000 / 6.396 | -50.0% [-50.8%, -49.2%] | faster |
| `username-width` | 7.708 / 8.188 / 8.604 | 1.250 / 1.355 / 1.438 | -83.8% [-83.9%, -83.6%] | faster |
| `username-katakana-width` | 5.458 / 5.792 / 6.375 | 4.292 / 4.583 / 4.896 | -21.1% [-21.8%, -20.8%] | faster |
| `username-lowercase` | 5.917 / 6.292 / 6.646 | 3.334 / 3.583 / 3.812 | -43.7% [-44.2%, -43.1%] | faster |
| `username-tolower-alias` | 5.896 / 6.271 / 6.521 | 3.333 / 3.583 / 3.833 | -43.8% [-44.4%, -42.9%] | faster |
| `username-casefold` | 6.625 / 7.021 / 7.417 | 1.895 / 2.021 / 2.125 | -71.1% [-72.0%, -70.9%] | faster |
| `username-preserved` | 5.708 / 6.021 / 6.354 | 1.625 / 1.750 / 1.875 | -71.9% [-72.1%, -71.5%] | faster |
| `username-nfc` | 7.292 / 7.667 / 8.396 | 2.083 / 2.229 / 2.375 | -71.4% [-72.1%, -71.3%] | faster |
| `username-mixed-script` | 10.729 / 11.209 / 13.917 | 6.000 / 6.417 / 7.042 | -44.2% [-44.7%, -43.1%] | faster |
| `password-opaque` | 8.667 / 9.229 / 11.499 | 5.542 / 5.938 / 6.688 | -36.0% [-36.9%, -35.7%] | faster |
| `password-combining-1025` | 2,010.042 / 2,122.541 / 2,259.354 | 292.969 / 328.771 / 361.688 | -85.4% [-85.5%, -85.0%] | faster |
| `nickname-mapped` | 8.292 / 8.729 / 9.646 | 5.334 / 5.708 / 6.646 | -35.6% [-36.1%, -34.9%] | faster |
| `nickname-tolower-alias` | 5.896 / 6.188 / 6.812 | 4.792 / 5.125 / 5.646 | -18.7% [-19.4%, -17.2%] | faster |
| `nickname-casefold` | 6.271 / 6.667 / 7.396 | 3.958 / 4.250 / 4.562 | -37.2% [-37.7%, -36.5%] | faster |
| `nickname-preserved` | 7.979 / 8.500 / 9.438 | 4.958 / 5.312 / 6.354 | -38.3% [-38.6%, -37.4%] | faster |
| `nickname-alias` | 8.250 / 8.749 / 9.750 | 5.354 / 5.708 / 6.646 | -34.9% [-35.8%, -34.3%] | faster |
| `identifier-class` | 2.958 / 3.125 / 3.271 | 0.416 / 0.458 / 0.500 | -86.1% [-87.3%, -85.8%] | faster |
| `freeform-class` | 5.083 / 5.375 / 5.625 | 0.375 / 0.417 / 0.500 | -92.6% [-92.7%, -92.1%] | faster |
| `reject-bidi` | 2.541 / 2.667 / 2.792 | 1.750 / 1.895 / 2.021 | -31.1% [-31.9%, -29.4%] | faster |
| `reject-password-control` | 3.896 / 4.125 / 4.334 | 1.812 / 1.958 / 2.083 | -54.0% [-54.2%, -52.4%] | faster |
| `context-katakana-16` | 109.688 / 115.916 / 152.020 | 15.125 / 16.021 / 22.187 | -86.3% [-86.6%, -85.9%] | faster |
| `context-katakana-64` | 1,695.864 / 1,792.167 / 1,853.271 | 58.104 / 61.062 / 78.646 | -96.6% [-96.7%, -96.5%] | faster |
| `context-katakana-256` | 26,586.584 / 27,095.812 / 29,083.125 | 228.844 / 255.895 / 285.979 | -99.1% [-99.2%, -99.1%] | faster |
| `context-arabic-64` | 436.428 / 479.229 / 512.479 | 30.938 / 32.812 / 47.250 | -92.9% [-93.0%, -92.7%] | faster |
| `context-extended-arabic-64` | 463.937 / 504.417 / 532.542 | 35.416 / 37.833 / 55.188 | -92.4% [-92.5%, -92.3%] | faster |
| `context-joiners-127` | 247.448 / 282.500 / 319.042 | 186.688 / 216.500 / 251.000 | -24.6% [-26.1%, -22.4%] | faster |

### CPython 3.9.25

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 7.333 / 7.729 / 8.104 | 1.083 / 1.167 / 1.230 | -85.1% [-85.3%, -84.9%] | faster |
| `username-unicode` | 12.501 / 13.188 / 16.084 | 6.500 / 6.875 / 7.709 | -47.8% [-49.1%, -47.7%] | faster |
| `username-width` | 8.334 / 8.771 / 9.334 | 1.458 / 1.583 / 1.646 | -82.5% [-82.6%, -82.3%] | faster |
| `username-katakana-width` | 5.938 / 6.354 / 7.521 | 4.958 / 5.229 / 6.146 | -16.5% [-17.5%, -15.8%] | faster |
| `username-lowercase` | 6.354 / 6.688 / 7.104 | 3.875 / 4.083 / 4.417 | -39.2% [-39.9%, -38.3%] | faster |
| `username-tolower-alias` | 6.354 / 6.667 / 7.042 | 3.917 / 4.125 / 4.396 | -38.7% [-39.7%, -37.5%] | faster |
| `username-casefold` | 7.083 / 7.417 / 7.750 | 2.167 / 2.271 / 2.417 | -69.4% [-69.7%, -68.3%] | faster |
| `username-preserved` | 6.146 / 6.479 / 6.958 | 1.812 / 1.938 / 2.062 | -70.4% [-70.9%, -69.7%] | faster |
| `username-nfc` | 7.938 / 8.396 / 9.729 | 2.334 / 2.500 / 2.667 | -70.4% [-70.7%, -70.0%] | faster |
| `username-mixed-script` | 11.896 / 12.459 / 18.125 | 6.917 / 7.313 / 7.938 | -41.7% [-42.0%, -41.6%] | faster |
| `password-opaque` | 9.542 / 10.146 / 12.333 | 6.208 / 6.521 / 7.208 | -35.1% [-35.7%, -34.7%] | faster |
| `password-combining-1025` | 2,182.344 / 2,298.917 / 2,396.771 | 287.438 / 322.604 / 355.750 | -86.8% [-87.0%, -86.7%] | faster |
| `nickname-mapped` | 8.979 / 9.438 / 10.938 | 6.000 / 6.354 / 7.312 | -33.1% [-33.9%, -32.2%] | faster |
| `nickname-tolower-alias` | 6.208 / 6.562 / 7.021 | 5.375 / 5.687 / 6.021 | -13.4% [-14.7%, -13.1%] | faster |
| `nickname-casefold` | 6.709 / 7.062 / 7.396 | 4.396 / 4.646 / 5.062 | -34.1% [-35.2%, -33.0%] | faster |
| `nickname-preserved` | 8.666 / 9.125 / 10.208 | 5.542 / 5.854 / 6.375 | -36.1% [-37.1%, -35.0%] | faster |
| `nickname-alias` | 8.979 / 9.479 / 11.251 | 6.000 / 6.313 / 7.479 | -33.3% [-33.7%, -31.8%] | faster |
| `identifier-class` | 3.167 / 3.333 / 3.438 | 0.458 / 0.500 / 0.542 | -85.5% [-85.8%, -85.3%] | faster |
| `freeform-class` | 5.542 / 5.854 / 6.125 | 0.417 / 0.459 / 0.542 | -92.5% [-92.5%, -91.8%] | faster |
| `reject-bidi` | 2.604 / 2.792 / 3.000 | 1.896 / 2.021 / 2.166 | -27.8% [-28.8%, -25.6%] | faster |
| `reject-password-control` | 4.125 / 4.334 / 4.646 | 2.000 / 2.084 / 2.229 | -52.0% [-53.4%, -51.3%] | faster |
| `context-katakana-16` | 125.906 / 139.313 / 177.395 | 17.833 / 18.688 / 24.854 | -86.0% [-86.2%, -85.7%] | faster |
| `context-katakana-64` | 1,918.229 / 2,013.604 / 2,104.771 | 68.198 / 75.188 / 94.895 | -96.5% [-96.5%, -96.4%] | faster |
| `context-katakana-256` | 30,463.167 / 31,336.396 / 34,323.979 | 267.177 / 298.646 / 367.438 | -99.1% [-99.1%, -99.1%] | faster |
| `context-arabic-64` | 514.500 / 560.042 / 596.792 | 37.521 / 39.459 / 53.438 | -92.7% [-92.9%, -92.7%] | faster |
| `context-extended-arabic-64` | 531.229 / 578.895 / 608.292 | 42.020 / 43.937 / 57.980 | -92.2% [-92.3%, -91.9%] | faster |
| `context-joiners-127` | 282.250 / 323.646 / 363.125 | 216.042 / 243.250 / 276.646 | -23.6% [-24.8%, -22.8%] | faster |

### CPython 3.10.22

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 7.417 / 7.875 / 8.146 | 1.020 / 1.084 / 1.167 | -86.3% [-86.6%, -86.0%] | faster |
| `username-unicode` | 12.541 / 13.250 / 15.584 | 6.312 / 6.708 / 7.062 | -49.8% [-50.0%, -49.2%] | faster |
| `username-width` | 8.459 / 8.979 / 9.834 | 1.375 / 1.520 / 1.625 | -83.6% [-84.0%, -83.2%] | faster |
| `username-katakana-width` | 6.000 / 6.354 / 6.646 | 4.771 / 5.104 / 5.354 | -20.5% [-21.0%, -18.7%] | faster |
| `username-lowercase` | 6.396 / 6.750 / 7.041 | 3.771 / 4.042 / 4.333 | -41.3% [-41.5%, -40.8%] | faster |
| `username-tolower-alias` | 6.521 / 6.812 / 7.271 | 3.750 / 4.021 / 4.292 | -42.0% [-43.0%, -41.4%] | faster |
| `username-casefold` | 7.188 / 7.625 / 7.896 | 2.125 / 2.292 / 2.438 | -70.4% [-70.7%, -69.2%] | faster |
| `username-preserved` | 6.167 / 6.604 / 6.854 | 1.792 / 1.917 / 2.042 | -70.7% [-71.3%, -69.9%] | faster |
| `username-nfc` | 7.958 / 8.417 / 9.334 | 2.354 / 2.542 / 2.688 | -70.4% [-70.8%, -69.8%] | faster |
| `username-mixed-script` | 11.938 / 12.542 / 15.834 | 6.771 / 7.188 / 8.146 | -43.1% [-43.5%, -42.8%] | faster |
| `password-opaque` | 9.729 / 10.126 / 11.709 | 6.000 / 6.417 / 7.458 | -38.3% [-38.9%, -36.8%] | faster |
| `password-combining-1025` | 2,004.761 / 2,089.834 / 2,180.500 | 107.229 / 115.083 / 137.958 | -94.6% [-94.7%, -94.6%] | faster |
| `nickname-mapped` | 9.000 / 9.541 / 10.854 | 5.791 / 6.167 / 6.500 | -35.9% [-36.1%, -34.8%] | faster |
| `nickname-tolower-alias` | 6.271 / 6.625 / 6.896 | 5.250 / 5.521 / 5.833 | -15.8% [-17.8%, -14.9%] | faster |
| `nickname-casefold` | 6.771 / 7.146 / 7.438 | 4.292 / 4.583 / 4.812 | -37.2% [-38.7%, -36.4%] | faster |
| `nickname-preserved` | 8.625 / 9.146 / 10.209 | 5.333 / 5.666 / 6.062 | -38.4% [-39.2%, -37.3%] | faster |
| `nickname-alias` | 9.000 / 9.479 / 10.624 | 5.792 / 6.125 / 6.687 | -35.5% [-35.8%, -35.2%] | faster |
| `identifier-class` | 3.188 / 3.438 / 3.563 | 0.417 / 0.459 / 0.541 | -86.9% [-87.2%, -86.8%] | faster |
| `freeform-class` | 5.646 / 5.958 / 6.229 | 0.417 / 0.459 / 0.500 | -92.6% [-92.9%, -92.6%] | faster |
| `reject-bidi` | 2.688 / 2.875 / 3.062 | 1.916 / 2.083 / 2.167 | -29.2% [-30.5%, -26.8%] | faster |
| `reject-password-control` | 4.208 / 4.438 / 4.687 | 2.000 / 2.146 / 2.291 | -52.5% [-53.0%, -51.8%] | faster |
| `context-katakana-16` | 124.146 / 130.291 / 161.042 | 17.396 / 18.334 / 25.459 | -86.0% [-86.3%, -85.6%] | faster |
| `context-katakana-64` | 1,868.844 / 1,950.125 / 2,023.938 | 67.437 / 73.688 / 97.042 | -96.4% [-96.4%, -96.3%] | faster |
| `context-katakana-256` | 29,487.011 / 30,053.000 / 33,118.458 | 265.198 / 292.271 / 323.729 | -99.1% [-99.1%, -99.1%] | faster |
| `context-arabic-64` | 506.594 / 543.000 / 577.896 | 37.042 / 38.750 / 51.834 | -92.7% [-92.8%, -92.5%] | faster |
| `context-extended-arabic-64` | 523.698 / 559.292 / 608.145 | 41.198 / 42.937 / 58.020 | -92.2% [-92.4%, -92.0%] | faster |
| `context-joiners-127` | 284.531 / 316.312 / 351.292 | 216.969 / 243.812 / 275.979 | -23.6% [-24.5%, -23.2%] | faster |

### CPython 3.11.17

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 5.875 / 6.208 / 6.438 | 1.000 / 1.083 / 1.166 | -83.0% [-83.4%, -82.7%] | faster |
| `username-unicode` | 9.979 / 10.541 / 12.583 | 5.813 / 6.208 / 6.667 | -41.9% [-42.4%, -41.1%] | faster |
| `username-width` | 6.979 / 7.312 / 7.688 | 1.333 / 1.417 / 1.520 | -81.0% [-81.4%, -80.8%] | faster |
| `username-katakana-width` | 4.917 / 5.208 / 5.708 | 4.479 / 4.750 / 5.063 | -8.5% [-9.3%, -7.7%] | faster |
| `username-lowercase` | 5.083 / 5.354 / 5.625 | 3.437 / 3.687 / 3.896 | -32.0% [-32.5%, -31.0%] | faster |
| `username-tolower-alias` | 5.083 / 5.333 / 5.604 | 3.417 / 3.646 / 3.896 | -32.5% [-33.7%, -32.1%] | faster |
| `username-casefold` | 5.667 / 6.021 / 6.292 | 1.895 / 2.021 / 2.125 | -66.9% [-67.0%, -66.3%] | faster |
| `username-preserved` | 4.917 / 5.188 / 5.417 | 1.625 / 1.750 / 1.875 | -66.9% [-67.1%, -66.4%] | faster |
| `username-nfc` | 6.291 / 6.625 / 6.917 | 2.104 / 2.250 / 2.375 | -66.4% [-67.2%, -65.8%] | faster |
| `username-mixed-script` | 9.459 / 10.041 / 12.666 | 6.229 / 6.604 / 6.938 | -34.3% [-35.3%, -33.4%] | faster |
| `password-opaque` | 7.688 / 8.104 / 9.646 | 5.375 / 5.708 / 6.000 | -30.2% [-30.7%, -29.6%] | faster |
| `password-combining-1025` | 1,657.698 / 1,745.146 / 2,175.583 | 104.135 / 112.375 / 138.645 | -93.7% [-93.8%, -93.5%] | faster |
| `nickname-mapped` | 7.000 / 7.354 / 7.812 | 5.083 / 5.396 / 5.708 | -27.2% [-27.4%, -26.4%] | faster |
| `nickname-tolower-alias` | 4.875 / 5.104 / 5.354 | 4.542 / 4.792 / 5.042 | -6.0% [-7.7%, -4.7%] | faster |
| `nickname-casefold` | 5.333 / 5.604 / 5.833 | 3.667 / 3.896 / 4.146 | -31.1% [-32.2%, -30.0%] | faster |
| `nickname-preserved` | 6.771 / 7.167 / 7.667 | 4.750 / 5.042 / 5.333 | -29.5% [-30.6%, -29.1%] | faster |
| `nickname-alias` | 7.000 / 7.458 / 7.812 | 5.083 / 5.396 / 5.812 | -26.9% [-27.6%, -26.5%] | faster |
| `identifier-class` | 2.917 / 3.104 / 3.229 | 0.417 / 0.459 / 0.500 | -85.7% [-85.7%, -85.4%] | faster |
| `freeform-class` | 4.833 / 5.062 / 5.292 | 0.416 / 0.459 / 0.541 | -91.4% [-91.4%, -91.2%] | faster |
| `reject-bidi` | 2.271 / 2.417 / 2.604 | 1.771 / 1.896 / 2.000 | -21.8% [-22.2%, -21.3%] | faster |
| `reject-password-control` | 3.271 / 3.521 / 3.688 | 1.833 / 2.000 / 2.104 | -43.6% [-45.6%, -43.3%] | faster |
| `context-katakana-16` | 121.729 / 127.938 / 160.355 | 16.270 / 17.188 / 22.166 | -86.4% [-86.7%, -86.3%] | faster |
| `context-katakana-64` | 1,850.448 / 1,943.250 / 2,050.584 | 62.312 / 65.146 / 88.355 | -96.6% [-96.7%, -96.6%] | faster |
| `context-katakana-256` | 29,060.156 / 29,657.688 / 31,111.605 | 245.302 / 273.250 / 305.771 | -99.2% [-99.2%, -99.1%] | faster |
| `context-arabic-64` | 436.447 / 475.250 / 507.604 | 32.323 / 33.979 / 45.188 | -92.6% [-92.9%, -92.4%] | faster |
| `context-extended-arabic-64` | 465.031 / 498.250 / 518.000 | 36.188 / 38.084 / 48.625 | -92.2% [-92.4%, -92.0%] | faster |
| `context-joiners-127` | 240.812 / 269.375 / 305.104 | 183.427 / 204.625 / 234.812 | -23.3% [-24.6%, -23.0%] | faster |

### CPython 3.12.15

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 5.459 / 5.771 / 6.104 | 1.042 / 1.125 / 1.230 | -80.8% [-81.2%, -80.5%] | faster |
| `username-unicode` | 9.334 / 9.834 / 12.125 | 5.917 / 6.229 / 6.646 | -36.6% [-38.1%, -36.2%] | faster |
| `username-width` | 6.646 / 7.021 / 7.375 | 1.416 / 1.541 / 1.666 | -78.8% [-79.2%, -78.7%] | faster |
| `username-katakana-width` | 4.813 / 5.084 / 5.542 | 4.729 / 5.000 / 5.313 | -1.8% [-2.2%, -1.3%] | within uncertainty |
| `username-lowercase` | 4.709 / 4.959 / 5.250 | 3.583 / 3.792 / 4.125 | -23.9% [-25.8%, -23.6%] | faster |
| `username-tolower-alias` | 4.688 / 4.958 / 5.209 | 3.562 / 3.792 / 4.146 | -24.3% [-24.8%, -23.2%] | faster |
| `username-casefold` | 5.208 / 5.479 / 5.833 | 2.000 / 2.167 / 2.312 | -61.6% [-61.8%, -61.2%] | faster |
| `username-preserved` | 4.583 / 4.833 / 5.083 | 1.708 / 1.855 / 1.980 | -62.4% [-62.9%, -62.1%] | faster |
| `username-nfc` | 5.875 / 6.167 / 6.417 | 2.271 / 2.417 / 2.563 | -61.5% [-62.0%, -60.9%] | faster |
| `username-mixed-script` | 8.917 / 9.417 / 11.812 | 6.417 / 6.792 / 7.271 | -27.7% [-28.8%, -26.8%] | faster |
| `password-opaque` | 7.167 / 7.542 / 8.459 | 6.042 / 6.375 / 6.833 | -15.5% [-17.0%, -14.9%] | faster |
| `password-combining-1025` | 1,597.417 / 1,689.626 / 1,794.792 | 194.698 / 216.855 / 244.354 | -87.9% [-88.0%, -87.8%] | faster |
| `nickname-mapped` | 6.625 / 6.958 / 7.521 | 5.542 / 5.833 / 6.271 | -16.6% [-17.4%, -15.5%] | faster |
| `nickname-tolower-alias` | 4.521 / 4.792 / 5.063 | 5.000 / 5.250 / 5.500 | +9.7% [+9.1%, +10.7%] | slower |
| `nickname-casefold` | 4.896 / 5.166 / 5.375 | 3.917 / 4.146 / 4.396 | -20.0% [-21.5%, -18.8%] | faster |
| `nickname-preserved` | 6.417 / 6.771 / 7.312 | 5.208 / 5.542 / 5.875 | -18.6% [-18.8%, -17.9%] | faster |
| `nickname-alias` | 6.604 / 7.000 / 7.896 | 5.521 / 5.833 / 6.271 | -16.7% [-18.8%, -15.5%] | faster |
| `identifier-class` | 2.479 / 2.625 / 2.792 | 0.375 / 0.438 / 0.500 | -84.9% [-85.0%, -83.9%] | faster |
| `freeform-class` | 4.250 / 4.500 / 4.771 | 0.375 / 0.417 / 0.500 | -91.2% [-91.4%, -91.2%] | faster |
| `reject-bidi` | 2.333 / 2.479 / 2.667 | 2.000 / 2.146 / 2.271 | -15.0% [-16.8%, -14.3%] | faster |
| `reject-password-control` | 3.167 / 3.354 / 3.604 | 1.875 / 2.042 / 2.167 | -40.5% [-41.2%, -39.7%] | faster |
| `context-katakana-16` | 113.583 / 127.813 / 162.208 | 16.312 / 17.125 / 22.334 | -85.6% [-85.8%, -85.5%] | faster |
| `context-katakana-64` | 1,722.177 / 1,818.687 / 1,947.771 | 61.521 / 66.271 / 85.500 | -96.4% [-96.5%, -96.4%] | faster |
| `context-katakana-256` | 26,988.219 / 27,579.271 / 28,880.562 | 243.875 / 271.938 / 299.062 | -99.1% [-99.1%, -99.1%] | faster |
| `context-arabic-64` | 405.292 / 440.604 / 468.833 | 33.042 / 34.666 / 46.604 | -91.8% [-92.2%, -91.8%] | faster |
| `context-extended-arabic-64` | 430.708 / 485.084 / 543.833 | 37.021 / 39.166 / 53.083 | -91.4% [-91.8%, -91.3%] | faster |
| `context-joiners-127` | 229.448 / 261.438 / 295.229 | 188.938 / 209.770 / 238.896 | -17.7% [-18.5%, -16.7%] | faster |

### CPython 3.13.16

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 5.646 / 5.896 / 6.208 | 0.917 / 1.000 / 1.063 | -84.1% [-84.1%, -83.5%] | faster |
| `username-unicode` | 9.791 / 10.333 / 12.271 | 5.938 / 6.333 / 6.875 | -39.1% [-39.8%, -38.4%] | faster |
| `username-width` | 6.917 / 7.271 / 8.146 | 1.291 / 1.375 / 1.479 | -81.4% [-81.6%, -81.2%] | faster |
| `username-katakana-width` | 4.979 / 5.250 / 5.667 | 4.604 / 4.917 / 5.417 | -6.0% [-8.4%, -5.8%] | faster |
| `username-lowercase` | 4.875 / 5.104 / 5.375 | 3.479 / 3.708 / 3.959 | -28.3% [-29.7%, -26.4%] | faster |
| `username-tolower-alias` | 4.833 / 5.125 / 5.396 | 3.500 / 3.729 / 4.000 | -27.7% [-28.0%, -26.7%] | faster |
| `username-casefold` | 5.334 / 5.667 / 5.917 | 1.875 / 2.021 / 2.167 | -64.7% [-65.0%, -64.0%] | faster |
| `username-preserved` | 4.708 / 4.917 / 5.104 | 1.625 / 1.770 / 1.875 | -65.1% [-65.8%, -64.9%] | faster |
| `username-nfc` | 6.125 / 6.458 / 6.729 | 2.250 / 2.375 / 2.563 | -63.4% [-64.0%, -63.0%] | faster |
| `username-mixed-script` | 9.375 / 9.854 / 11.876 | 6.500 / 6.938 / 8.375 | -29.9% [-31.9%, -29.5%] | faster |
| `password-opaque` | 7.542 / 8.021 / 9.188 | 5.667 / 6.021 / 6.646 | -25.0% [-25.5%, -24.3%] | faster |
| `password-combining-1025` | 1,674.750 / 1,756.458 / 1,838.896 | 192.364 / 217.750 / 240.875 | -88.5% [-88.6%, -88.5%] | faster |
| `nickname-mapped` | 6.958 / 7.375 / 7.958 | 5.188 / 5.521 / 6.146 | -25.4% [-27.1%, -24.4%] | faster |
| `nickname-tolower-alias` | 4.708 / 5.000 / 5.250 | 4.562 / 4.854 / 5.084 | -2.7% [-4.4%, -1.3%] | within uncertainty |
| `nickname-casefold` | 5.146 / 5.375 / 5.854 | 3.500 / 3.708 / 3.875 | -32.4% [-33.1%, -31.4%] | faster |
| `nickname-preserved` | 6.750 / 7.208 / 7.708 | 4.875 / 5.167 / 5.583 | -27.3% [-28.4%, -26.2%] | faster |
| `nickname-alias` | 7.042 / 7.375 / 7.896 | 5.209 / 5.521 / 6.042 | -26.1% [-27.1%, -25.1%] | faster |
| `identifier-class` | 2.625 / 2.792 / 2.938 | 0.417 / 0.459 / 0.541 | -84.1% [-84.1%, -83.9%] | faster |
| `freeform-class` | 4.500 / 4.750 / 4.979 | 0.416 / 0.458 / 0.500 | -90.8% [-91.4%, -90.7%] | faster |
| `reject-bidi` | 2.250 / 2.375 / 2.542 | 1.855 / 2.000 / 2.125 | -16.8% [-20.1%, -15.1%] | faster |
| `reject-password-control` | 3.333 / 3.521 / 3.667 | 1.792 / 1.917 / 2.041 | -46.5% [-46.9%, -45.0%] | faster |
| `context-katakana-16` | 119.625 / 128.125 / 173.604 | 16.396 / 17.333 / 23.937 | -86.1% [-86.3%, -85.9%] | faster |
| `context-katakana-64` | 1,792.333 / 1,874.124 / 2,003.708 | 62.635 / 66.667 / 91.999 | -96.5% [-96.5%, -96.4%] | faster |
| `context-katakana-256` | 28,833.605 / 29,572.770 / 34,383.791 | 248.771 / 295.354 / 358.938 | -99.1% [-99.1%, -99.1%] | faster |
| `context-arabic-64` | 422.875 / 463.854 / 498.375 | 33.188 / 34.896 / 47.291 | -92.1% [-92.2%, -92.0%] | faster |
| `context-extended-arabic-64` | 437.917 / 476.916 / 522.104 | 37.771 / 40.000 / 50.855 | -91.4% [-91.6%, -91.2%] | faster |
| `context-joiners-127` | 243.562 / 272.521 / 308.062 | 191.010 / 213.146 / 250.375 | -21.7% [-23.0%, -20.8%] | faster |

### CPython 3.14.8

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 5.854 / 6.271 / 6.542 | 1.042 / 1.146 / 1.229 | -82.2% [-82.4%, -81.7%] | faster |
| `username-unicode` | 10.104 / 10.667 / 10.875 | 6.292 / 6.688 / 6.875 | -37.7% [-38.7%, -35.9%] | faster |
| `username-width` | 7.229 / 7.521 / 7.854 | 1.458 / 1.584 / 1.667 | -79.7% [-79.9%, -79.5%] | faster |
| `username-katakana-width` | 5.292 / 5.500 / 5.729 | 5.083 / 5.250 / 5.562 | -3.9% [-5.5%, -2.0%] | within uncertainty |
| `username-lowercase` | 5.062 / 5.417 / 5.584 | 3.750 / 3.917 / 4.146 | -26.7% [-28.1%, -24.8%] | faster |
| `username-tolower-alias` | 5.083 / 5.438 / 5.625 | 3.729 / 3.958 / 4.167 | -26.5% [-27.5%, -26.2%] | faster |
| `username-casefold` | 5.584 / 5.896 / 6.167 | 2.125 / 2.292 / 2.417 | -62.0% [-62.6%, -61.6%] | faster |
| `username-preserved` | 4.958 / 5.146 / 5.417 | 1.833 / 2.000 / 2.084 | -62.9% [-63.9%, -62.3%] | faster |
| `username-nfc` | 6.312 / 6.729 / 6.958 | 2.416 / 2.542 / 2.729 | -61.6% [-62.7%, -61.3%] | faster |
| `username-mixed-script` | 9.688 / 10.188 / 10.500 | 6.979 / 7.417 / 7.729 | -27.5% [-29.4%, -26.8%] | faster |
| `password-opaque` | 7.750 / 8.229 / 8.438 | 6.041 / 6.375 / 6.646 | -22.3% [-22.7%, -21.6%] | faster |
| `password-combining-1025` | 1,721.448 / 1,775.458 / 1,818.646 | 193.989 / 203.083 / 228.271 | -88.8% [-88.8%, -88.7%] | faster |
| `nickname-mapped` | 7.146 / 7.604 / 7.979 | 5.583 / 5.792 / 6.188 | -22.1% [-23.9%, -21.1%] | faster |
| `nickname-tolower-alias` | 4.979 / 5.250 / 5.458 | 4.896 / 5.146 / 5.417 | -1.3% [-2.5%, +0.8%] | within uncertainty |
| `nickname-casefold` | 5.354 / 5.583 / 5.854 | 3.792 / 4.042 / 4.250 | -29.6% [-30.1%, -27.0%] | faster |
| `nickname-preserved` | 6.875 / 7.334 / 7.646 | 5.271 / 5.562 / 6.000 | -23.2% [-24.0%, -22.6%] | faster |
| `nickname-alias` | 7.250 / 7.500 / 8.084 | 5.521 / 5.813 / 6.146 | -23.2% [-24.9%, -21.5%] | faster |
| `identifier-class` | 2.625 / 2.771 / 2.917 | 0.458 / 0.500 / 0.583 | -82.7% [-84.1%, -82.4%] | faster |
| `freeform-class` | 4.646 / 4.833 / 5.104 | 0.417 / 0.458 / 0.500 | -91.0% [-91.1%, -90.9%] | faster |
| `reject-bidi` | 2.354 / 2.542 / 2.667 | 2.083 / 2.167 / 2.292 | -12.3% [-14.0%, -10.7%] | faster |
| `reject-password-control` | 3.479 / 3.688 / 3.875 | 1.958 / 2.125 / 2.250 | -43.6% [-44.6%, -42.2%] | faster |
| `context-katakana-16` | 122.584 / 127.020 / 155.041 | 17.230 / 17.959 / 19.791 | -85.9% [-86.3%, -85.7%] | faster |
| `context-katakana-64` | 1,879.500 / 1,946.624 / 2,030.083 | 66.104 / 69.042 / 82.729 | -96.5% [-96.6%, -96.4%] | faster |
| `context-katakana-256` | 29,128.625 / 29,596.688 / 30,205.791 | 262.375 / 277.167 / 296.688 | -99.1% [-99.1%, -99.1%] | faster |
| `context-arabic-64` | 473.291 / 496.875 / 519.500 | 35.500 / 36.979 / 43.646 | -92.5% [-92.6%, -92.3%] | faster |
| `context-extended-arabic-64` | 488.562 / 516.146 / 537.354 | 39.709 / 40.666 / 50.230 | -91.8% [-92.0%, -91.8%] | faster |
| `context-joiners-127` | 259.312 / 278.688 / 302.604 | 199.958 / 211.458 / 236.812 | -23.0% [-23.4%, -21.8%] | faster |

### CPython 3.15.2

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 5.083 / 5.396 / 5.604 | 0.875 / 0.938 / 1.000 | -82.8% [-83.3%, -82.6%] | faster |
| `username-unicode` | 8.729 / 9.146 / 9.375 | 5.271 / 5.604 / 5.792 | -39.6% [-40.0%, -38.2%] | faster |
| `username-width` | 6.229 / 6.625 / 6.917 | 1.250 / 1.333 / 1.438 | -79.9% [-80.1%, -79.8%] | faster |
| `username-katakana-width` | 4.542 / 4.813 / 5.041 | 4.188 / 4.500 / 4.708 | -7.8% [-9.5%, -4.7%] | faster |
| `username-lowercase` | 4.417 / 4.667 / 4.875 | 3.167 / 3.396 / 3.583 | -27.6% [-29.4%, -27.1%] | faster |
| `username-tolower-alias` | 4.396 / 4.667 / 4.938 | 3.188 / 3.396 / 3.625 | -27.5% [-28.4%, -26.5%] | faster |
| `username-casefold` | 4.834 / 5.125 / 5.312 | 1.792 / 1.958 / 2.062 | -62.7% [-63.8%, -62.2%] | faster |
| `username-preserved` | 4.271 / 4.521 / 4.729 | 1.583 / 1.750 / 1.833 | -63.1% [-63.4%, -62.2%] | faster |
| `username-nfc` | 5.458 / 5.812 / 6.000 | 2.062 / 2.229 / 2.375 | -62.2% [-62.9%, -61.2%] | faster |
| `username-mixed-script` | 8.251 / 8.771 / 9.063 | 5.812 / 6.250 / 6.521 | -30.1% [-30.4%, -28.3%] | faster |
| `password-opaque` | 6.479 / 6.875 / 7.104 | 5.312 / 5.708 / 5.875 | -17.4% [-19.2%, -16.5%] | faster |
| `password-combining-1025` | 1,403.917 / 1,458.333 / 1,493.833 | 186.583 / 198.917 / 225.396 | -86.7% [-86.9%, -86.6%] | faster |
| `nickname-mapped` | 6.167 / 6.604 / 6.938 | 4.896 / 5.084 / 5.396 | -21.4% [-22.9%, -19.7%] | faster |
| `nickname-tolower-alias` | 4.292 / 4.604 / 4.812 | 4.250 / 4.458 / 4.708 | -1.5% [-2.4%, -0.0%] | within uncertainty |
| `nickname-casefold` | 4.625 / 4.812 / 5.062 | 3.229 / 3.479 / 3.667 | -29.9% [-30.5%, -29.1%] | faster |
| `nickname-preserved` | 5.958 / 6.375 / 6.625 | 4.542 / 4.792 / 5.125 | -23.3% [-24.8%, -22.8%] | faster |
| `nickname-alias` | 6.125 / 6.479 / 6.792 | 4.834 / 5.104 / 5.396 | -21.4% [-21.9%, -20.5%] | faster |
| `identifier-class` | 2.167 / 2.354 / 2.458 | 0.375 / 0.416 / 0.459 | -82.7% [-83.6%, -82.7%] | faster |
| `freeform-class` | 3.812 / 4.000 / 4.208 | 0.354 / 0.375 / 0.458 | -90.7% [-91.2%, -90.2%] | faster |
| `reject-bidi` | 2.042 / 2.167 / 2.333 | 1.750 / 1.875 / 2.021 | -14.3% [-16.0%, -12.3%] | faster |
| `reject-password-control` | 3.000 / 3.187 / 3.354 | 1.667 / 1.855 / 1.938 | -44.1% [-44.8%, -43.3%] | faster |
| `context-katakana-16` | 106.458 / 110.083 / 132.667 | 13.771 / 14.459 / 15.166 | -86.9% [-87.3%, -86.6%] | faster |
| `context-katakana-64` | 1,592.677 / 1,655.813 / 1,696.854 | 53.166 / 55.938 / 65.688 | -96.7% [-96.7%, -96.6%] | faster |
| `context-katakana-256` | 25,155.656 / 25,533.646 / 25,844.896 | 205.865 / 217.520 / 248.500 | -99.2% [-99.2%, -99.2%] | faster |
| `context-arabic-64` | 330.927 / 345.813 / 372.062 | 25.521 / 26.875 / 30.938 | -92.2% [-92.3%, -91.9%] | faster |
| `context-extended-arabic-64` | 347.656 / 365.271 / 386.041 | 28.521 / 29.646 / 34.979 | -91.8% [-91.9%, -91.6%] | faster |
| `context-joiners-127` | 209.458 / 223.583 / 251.145 | 166.583 / 172.813 / 200.333 | -20.2% [-20.9%, -19.9%] | faster |

### PyPy 3.10.16 (PyPy 7.3.19)

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 1.875 / 2.000 / 2.146 | 0.875 / 1.000 / 5.833 | -53.3% [-54.9%, -50.5%] | faster |
| `username-unicode` | 3.500 / 3.667 / 3.979 | 4.167 / 4.458 / 8.896 | +18.4% [+14.2%, +20.5%] | slower |
| `username-width` | 2.396 / 2.521 / 2.708 | 1.021 / 1.125 / 5.500 | -57.8% [-58.4%, -54.4%] | faster |
| `username-katakana-width` | 1.438 / 1.521 / 2.333 | 3.021 / 3.250 / 8.688 | +111.6% [+104.4%, +126.5%] | slower |
| `username-lowercase` | 2.062 / 2.188 / 2.271 | 2.667 / 2.833 / 3.063 | +30.3% [+26.7%, +35.4%] | slower |
| `username-tolower-alias` | 2.083 / 2.188 / 2.292 | 2.667 / 2.875 / 5.583 | +28.7% [+23.8%, +34.4%] | slower |
| `username-casefold` | 1.833 / 1.958 / 2.083 | 1.542 / 1.771 / 5.833 | -14.1% [-18.0%, -9.3%] | faster |
| `username-preserved` | 1.917 / 2.021 / 2.126 | 1.500 / 1.688 / 5.729 | -21.3% [-22.6%, -16.1%] | faster |
| `username-nfc` | 2.271 / 2.375 / 5.979 | 1.688 / 2.854 / 5.938 | -24.1% [-26.6%, -21.7%] | faster |
| `username-mixed-script` | 3.167 / 3.333 / 3.584 | 4.208 / 4.708 / 12.896 | +32.0% [+29.4%, +37.6%] | slower |
| `password-opaque` | 2.041 / 2.125 / 2.209 | 3.646 / 4.792 / 7.771 | +79.6% [+77.5%, +85.0%] | slower |
| `password-combining-1025` | 527.115 / 573.020 / 616.875 | 450.334 / 487.750 / 555.334 | -14.3% [-15.3%, -13.5%] | faster |
| `nickname-mapped` | 1.750 / 1.833 / 1.938 | 3.458 / 3.583 / 3.791 | +97.7% [+87.4%, +112.5%] | slower |
| `nickname-tolower-alias` | 1.708 / 1.833 / 1.938 | 3.250 / 3.458 / 3.624 | +90.3% [+82.4%, +98.8%] | slower |
| `nickname-casefold` | 1.229 / 1.375 / 2.083 | 2.146 / 2.375 / 4.104 | +78.1% [+65.7%, +85.7%] | slower |
| `nickname-preserved` | 1.583 / 1.687 / 1.771 | 3.021 / 3.167 / 3.479 | +92.1% [+79.0%, +98.8%] | slower |
| `nickname-alias` | 1.730 / 1.834 / 1.938 | 3.479 / 3.646 / 3.833 | +102.3% [+94.3%, +106.2%] | slower |
| `identifier-class` | 0.542 / 0.625 / 0.667 | 0.542 / 0.625 / 1.812 | -3.5% [-7.4%, +8.1%] | within uncertainty |
| `freeform-class` | 0.917 / 1.000 / 1.083 | 0.542 / 0.625 / 1.792 | -41.3% [-43.1%, -38.7%] | faster |
| `reject-bidi` | 3.397 / 3.583 / 4.458 | 1.375 / 2.833 / 6.875 | -37.5% [-64.5%, +10.8%] | within uncertainty |
| `reject-password-control` | 3.250 / 3.417 / 3.874 | 2.729 / 5.062 / 6.333 | +41.6% [-72.1%, +48.7%] | within uncertainty |
| `context-katakana-16` | 32.750 / 37.688 / 43.896 | 4.812 / 13.875 / 15.771 | -85.3% [-86.1%, -84.8%] | faster |
| `context-katakana-64` | 506.552 / 530.167 / 582.396 | 17.188 / 20.875 / 33.000 | -96.6% [-96.8%, -95.6%] | faster |
| `context-katakana-256` | 8,139.448 / 8,400.104 / 8,554.188 | 75.375 / 86.167 / 205.396 | -99.1% [-99.1%, -99.0%] | faster |
| `context-arabic-64` | 80.021 / 86.416 / 98.417 | 6.146 / 12.354 / 14.312 | -92.3% [-93.2%, -91.4%] | faster |
| `context-extended-arabic-64` | 85.959 / 93.000 / 105.812 | 6.083 / 12.312 / 12.979 | -92.9% [-93.5%, -92.0%] | faster |
| `context-joiners-127` | 61.000 / 69.459 / 84.855 | 42.270 / 53.437 / 71.937 | -30.8% [-31.7%, -28.5%] | faster |

### PyPy 3.11.15 (PyPy 7.3.23)

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 1.875 / 1.980 / 2.083 | 0.834 / 0.958 / 5.667 | -55.1% [-56.5%, -50.6%] | faster |
| `username-unicode` | 3.500 / 3.667 / 3.999 | 3.958 / 4.271 / 8.542 | +13.8% [+11.2%, +15.6%] | slower |
| `username-width` | 2.354 / 2.479 / 2.646 | 1.000 / 1.145 / 5.479 | -58.0% [-58.6%, -54.5%] | faster |
| `username-katakana-width` | 1.417 / 1.500 / 2.292 | 2.896 / 3.208 / 8.459 | +105.9% [+101.5%, +110.8%] | slower |
| `username-lowercase` | 2.062 / 2.167 / 2.271 | 2.583 / 2.771 / 3.021 | +25.8% [+22.8%, +30.3%] | slower |
| `username-tolower-alias` | 2.104 / 2.188 / 2.292 | 2.583 / 2.813 / 5.646 | +24.1% [+21.6%, +30.3%] | slower |
| `username-casefold` | 1.812 / 1.958 / 2.062 | 1.520 / 1.770 / 5.896 | -14.8% [-18.1%, -12.1%] | faster |
| `username-preserved` | 1.938 / 2.062 / 2.208 | 1.480 / 1.645 / 5.646 | -22.7% [-25.5%, -16.9%] | faster |
| `username-nfc` | 2.208 / 2.333 / 4.750 | 1.688 / 2.854 / 5.771 | -22.4% [-26.2%, -20.6%] | faster |
| `username-mixed-script` | 3.146 / 3.292 / 3.646 | 4.083 / 4.458 / 11.437 | +30.3% [+27.7%, +33.8%] | slower |
| `password-opaque` | 2.000 / 2.104 / 2.292 | 3.708 / 4.062 / 8.021 | +86.5% [+80.7%, +92.5%] | slower |
| `password-combining-1025` | 525.990 / 562.375 / 616.438 | 469.875 / 501.750 / 566.708 | -10.8% [-11.4%, -9.5%] | faster |
| `nickname-mapped` | 1.750 / 1.875 / 1.979 | 3.500 / 3.646 / 3.812 | +98.8% [+93.0%, +111.1%] | slower |
| `nickname-tolower-alias` | 1.708 / 1.792 / 1.875 | 3.250 / 3.438 / 3.646 | +91.5% [+87.9%, +96.3%] | slower |
| `nickname-casefold` | 1.250 / 1.333 / 2.521 | 2.167 / 2.396 / 3.688 | +76.4% [+71.6%, +81.4%] | slower |
| `nickname-preserved` | 1.583 / 1.688 / 1.771 | 3.062 / 3.250 / 3.438 | +93.5% [+85.8%, +98.6%] | slower |
| `nickname-alias` | 1.730 / 1.833 / 1.938 | 3.479 / 3.625 / 3.854 | +101.2% [+97.6%, +108.7%] | slower |
| `identifier-class` | 0.583 / 0.625 / 0.709 | 0.542 / 0.625 / 1.792 | -7.0% [-10.6%, +4.2%] | within uncertainty |
| `freeform-class` | 1.000 / 1.042 / 1.125 | 0.562 / 0.667 / 1.812 | -41.7% [-45.8%, -40.0%] | faster |
| `reject-bidi` | 3.396 / 3.563 / 3.854 | 1.333 / 2.792 / 6.938 | -21.6% [-62.2%, +56.5%] | within uncertainty |
| `reject-password-control` | 3.188 / 3.417 / 3.708 | 2.708 / 4.979 / 6.500 | +38.0% [-72.5%, +49.0%] | within uncertainty |
| `context-katakana-16` | 32.750 / 37.688 / 46.229 | 4.812 / 13.958 / 14.354 | -85.3% [-85.6%, -84.9%] | faster |
| `context-katakana-64` | 507.875 / 538.562 / 585.146 | 17.188 / 20.958 / 36.062 | -96.6% [-96.7%, -95.4%] | faster |
| `context-katakana-256` | 8,112.052 / 8,379.896 / 8,579.812 | 75.573 / 89.771 / 234.792 | -99.1% [-99.1%, -99.0%] | faster |
| `context-arabic-64` | 84.750 / 92.000 / 104.291 | 6.104 / 14.312 / 16.542 | -92.7% [-93.3%, -92.7%] | faster |
| `context-extended-arabic-64` | 89.980 / 98.604 / 108.812 | 6.104 / 13.354 / 15.062 | -93.2% [-93.7%, -93.1%] | faster |
| `context-joiners-127` | 59.979 / 67.979 / 83.688 | 41.896 / 54.000 / 68.501 | -30.0% [-30.9%, -29.1%] | faster |

### CPython 3.14.8 (GIL disabled)

| Workload | Upstream P50 / P95 / P99 (µs) | Candidate P50 / P95 / P99 (µs) | Paired P50 change [95% interval] | Verdict |
| --- | ---: | ---: | ---: | --- |
| `username-ascii` | 4.396 / 4.583 / 4.917 | 0.834 / 0.916 / 1.000 | -81.0% [-81.5%, -80.8%] | faster |
| `username-unicode` | 7.646 / 8.062 / 10.625 | 4.688 / 4.917 / 5.188 | -38.9% [-39.8%, -37.7%] | faster |
| `username-width` | 5.312 / 5.542 / 6.375 | 1.167 / 1.270 / 1.417 | -77.8% [-78.4%, -77.7%] | faster |
| `username-katakana-width` | 4.062 / 4.271 / 5.292 | 3.834 / 4.000 / 4.250 | -5.6% [-6.7%, -4.6%] | faster |
| `username-lowercase` | 3.854 / 4.062 / 4.375 | 2.792 / 2.917 / 3.042 | -27.7% [-28.8%, -27.2%] | faster |
| `username-tolower-alias` | 3.833 / 4.062 / 4.750 | 2.760 / 2.938 / 3.167 | -27.5% [-29.2%, -27.2%] | faster |
| `username-casefold` | 4.208 / 4.458 / 5.000 | 1.604 / 1.708 / 1.833 | -62.3% [-62.9%, -61.7%] | faster |
| `username-preserved` | 3.687 / 3.875 / 4.375 | 1.375 / 1.479 / 1.583 | -62.1% [-62.9%, -61.9%] | faster |
| `username-nfc` | 4.833 / 5.146 / 6.250 | 1.770 / 1.917 / 2.021 | -63.3% [-63.6%, -62.8%] | faster |
| `username-mixed-script` | 7.333 / 7.729 / 9.000 | 5.042 / 5.312 / 7.771 | -30.7% [-32.7%, -29.3%] | faster |
| `password-opaque` | 5.854 / 6.229 / 8.729 | 4.750 / 5.021 / 7.208 | -17.7% [-19.1%, -16.3%] | faster |
| `password-combining-1025` | 1,260.427 / 1,341.667 / 1,418.208 | 186.313 / 199.792 / 225.272 | -85.2% [-85.3%, -85.1%] | faster |
| `nickname-mapped` | 5.479 / 5.813 / 7.771 | 4.312 / 4.667 / 6.896 | -21.4% [-22.0%, -20.9%] | faster |
| `nickname-tolower-alias` | 3.854 / 4.042 / 4.396 | 3.896 / 4.125 / 4.833 | +1.1% [-1.0%, +2.7%] | within uncertainty |
| `nickname-casefold` | 4.083 / 4.333 / 4.979 | 2.917 / 3.083 / 3.542 | -28.9% [-29.7%, -27.0%] | faster |
| `nickname-preserved` | 5.229 / 5.521 / 7.500 | 4.083 / 4.334 / 6.938 | -22.6% [-22.9%, -21.2%] | faster |
| `nickname-alias` | 5.500 / 5.979 / 8.604 | 4.292 / 4.583 / 6.667 | -21.1% [-22.3%, -20.2%] | faster |
| `identifier-class` | 1.917 / 2.021 / 2.146 | 0.333 / 0.375 / 0.459 | -82.4% [-82.6%, -81.3%] | faster |
| `freeform-class` | 3.333 / 3.542 / 4.125 | 0.333 / 0.375 / 0.458 | -90.0% [-90.3%, -89.9%] | faster |
| `reject-bidi` | 1.792 / 1.917 / 2.042 | 1.625 / 1.709 / 1.855 | -11.4% [-12.8%, -9.3%] | faster |
| `reject-password-control` | 2.646 / 2.833 / 3.833 | 1.521 / 1.625 / 1.770 | -42.5% [-43.0%, -42.0%] | faster |
| `context-katakana-16` | 92.771 / 99.542 / 114.688 | 12.749 / 13.374 / 16.834 | -86.1% [-86.6%, -85.7%] | faster |
| `context-katakana-64` | 1,400.375 / 1,508.958 / 1,559.688 | 48.146 / 50.083 / 58.896 | -96.6% [-96.6%, -96.5%] | faster |
| `context-katakana-256` | 22,485.687 / 22,983.291 / 23,248.291 | 189.250 / 204.292 / 227.292 | -99.2% [-99.2%, -99.1%] | faster |
| `context-arabic-64` | 304.646 / 325.521 / 358.521 | 24.355 / 25.104 / 28.688 | -92.0% [-92.0%, -92.0%] | faster |
| `context-extended-arabic-64` | 323.365 / 349.104 / 381.229 | 26.271 / 27.750 / 30.480 | -91.8% [-91.9%, -91.7%] | faster |
| `context-joiners-127` | 189.980 / 201.771 / 233.333 | 149.208 / 156.229 / 185.750 | -21.2% [-22.2%, -20.1%] | faster |
