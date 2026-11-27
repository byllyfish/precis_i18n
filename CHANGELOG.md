# Changelog

## Unreleased

- Bind native username operations once per preparation and validate stock
  inputs against the same admitted Unicode data before mapping and bidi.
- Share exclusion masks with qualified explicit Unicode providers and avoid
  width translation on text without a mapped character.
- Avoid regular-expression dispatch when a nickname has no repeated spaces.
- Combine exceptional native admission properties in sparse bitmaps and use
  the active Unicode backend to classify ordinary characters. Preserve
  diagnostics and positional checks for exceptional characters.
- Detect native username bidi requirements in one scan and reject a label
  with RTL characters when its first character cannot start an RTL label.
- Share one initialized immutable table per Unicode generation, with direct
  range loading and compact one-code-point mappings.
- Pack common native classifications and use bulk admission for long strings
  composed entirely of those admitted characters.
- Apply the established ASCII invariants after username admission, including
  when width mapping yields ASCII. Custom rules keep their existing behavior.
- Apply profile-specific base-class admission before later mapping and
  normalization. Username profiles first apply literal Unicode width
  decompositions. U+212A and an uppercase middle-dot context now fail
  before lowercase can make them admissible.
- Prepare strings before enforcing later profile rules and check
  stability using bounded repetition. Password and nickname preparation
  preserve their own class and normalization rules. A preceding invalid
  character can now be reported before a later bidi failure.
- Add explicitly versioned Unicode 17 and 18 configurations, exact comparison
  keys, and immutable semantic identities. Keep native and legacy provider
  calls available. Revalidate existing keys and collisions before switching.
- Reuse string-wide contextual verdicts within one pass and remove joining-type
  string slices. Keep context rules and error offsets.
- Reduce native admission work for printable ASCII and common Unicode
  characters. Reuse normalization and directionality checks during
  stabilization when the mapped value matches the previous checked output.

### Performance

[Full benchmark results and methodology](docs/performance.md).

Upstream commit `865faed` and this implementation were measured in six
balanced fresh-process pairs per interpreter using its native Unicode
configuration. Short workloads used 10,000 timed samples per process.
Each comparison uses inputs with equivalent preparation or rejection
outcomes. The counts use the paired P50 verdicts. Negative percentages
indicate lower latency, and the last column takes the median of the
paired P50 changes across comparable workloads.

| Runtime | Architecture | Faster | Within uncertainty | Slower | Median P50 change |
| --- | --- | ---: | ---: | ---: | ---: |
| CPython 3.7.17 | x86_64 | 27 | 0 | 0 | -52.7% |
| CPython 3.8.20 | arm64 | 27 | 0 | 0 | -54.0% |
| CPython 3.9.25 | arm64 | 27 | 0 | 0 | -52.0% |
| CPython 3.10.22 | arm64 | 27 | 0 | 0 | -52.5% |
| CPython 3.11.17 | arm64 | 27 | 0 | 0 | -43.6% |
| CPython 3.12.15 | arm64 | 25 | 1 | 1 | -40.5% |
| CPython 3.13.16 | arm64 | 26 | 1 | 0 | -46.5% |
| CPython 3.14.8 | arm64 | 25 | 2 | 0 | -43.6% |
| CPython 3.15.2 | arm64 | 26 | 1 | 0 | -44.1% |
| PyPy 3.10.16 (7.3.19) | arm64 | 13 | 3 | 11 | -14.1% |
| PyPy 3.11.15 (7.3.23) | arm64 | 13 | 3 | 11 | -10.8% |
| CPython 3.14.8 (GIL disabled) | arm64 | 26 | 1 | 0 | -42.5% |

Selected preparation and rejection P50s in microseconds, shown as upstream → candidate.

| Runtime | ASCII mapped | Unicode mapped | Halfwidth Katakana | Lowercase | Bidi rejection |
| --- | ---: | ---: | ---: | ---: | ---: |
| CPython 3.7.17 | 15.521 → 2.375 | 26.666 → 14.521 | 12.396 → 10.667 | 13.479 → 8.666 | 5.896 → 4.729 |
| CPython 3.8.20 | 6.750 → 0.958 | 11.334 → 5.667 | 5.458 → 4.292 | 5.917 → 3.334 | 2.541 → 1.750 |
| CPython 3.9.25 | 7.333 → 1.083 | 12.501 → 6.500 | 5.938 → 4.958 | 6.354 → 3.875 | 2.604 → 1.896 |
| CPython 3.10.22 | 7.417 → 1.020 | 12.541 → 6.312 | 6.000 → 4.771 | 6.396 → 3.771 | 2.688 → 1.916 |
| CPython 3.11.17 | 5.875 → 1.000 | 9.979 → 5.813 | 4.917 → 4.479 | 5.083 → 3.437 | 2.271 → 1.771 |
| CPython 3.12.15 | 5.459 → 1.042 | 9.334 → 5.917 | 4.813 → 4.729 | 4.709 → 3.583 | 2.333 → 2.000 |
| CPython 3.13.16 | 5.646 → 0.917 | 9.791 → 5.938 | 4.979 → 4.604 | 4.875 → 3.479 | 2.250 → 1.855 |
| CPython 3.14.8 | 5.854 → 1.042 | 10.104 → 6.292 | 5.292 → 5.083 | 5.062 → 3.750 | 2.354 → 2.083 |
| CPython 3.15.2 | 5.083 → 0.875 | 8.729 → 5.271 | 4.542 → 4.188 | 4.417 → 3.167 | 2.042 → 1.750 |
| PyPy 3.10.16 (7.3.19) | 1.875 → 0.875 | 3.500 → 4.167 | 1.438 → 3.021 | 2.062 → 2.667 | 3.397 → 1.375 |
| PyPy 3.11.15 (7.3.23) | 1.875 → 0.834 | 3.500 → 3.958 | 1.417 → 2.896 | 2.062 → 2.583 | 3.396 → 1.333 |
| CPython 3.14.8 (GIL disabled) | 4.396 → 0.834 | 7.646 → 4.688 | 4.062 → 3.834 | 3.854 → 2.792 | 1.792 → 1.625 |

Additional representative measurements on CPython 3.10 in microseconds.

| Workload | Upstream → candidate P50 (µs) | Paired P50 change |
| --- | ---: | ---: |
| Fullwidth username | 8.459 → 1.375 | -83.6% |
| Mixed-script username | 11.938 → 6.771 | -43.1% |
| Mapped nickname | 9.000 → 5.791 | -35.9% |
| OpaqueString | 9.729 → 6.000 | -38.3% |
| 1,025-code-point combining sequence | 2004.761 → 107.229 | -94.6% |
| 256-code-point Katakana context | 29487.011 → 265.198 | -99.1% |

## 1.1.2

-   Update internal tables for Unicode 17.0.
-   Drop support for Python 3.5 and 3.6.
-   Update copyright year (2025).

## 1.1.1

-   Update internal tables for Unicode 16.0.
-   Remove `test_suite` from setup.py file. Contributed by `adrien-n` (PR #38).
-   Add Python 3.14-dev to CI build environment.
-   Update copyright year (2024).

## 1.1.0

-   Fixed an issue in the Nickname profile implementation that trimmed
    extra leading/trailing white space beyond the `Zs`
    category prescribed in RFC 8266. Python treats certain
    Unicode control characters such as `'\n'` and `'\t'` as white space. If
    these appeared as leading/trailing spaces in a Nickname string, they
    were stripped. With this release, the Nickname profile will raise a
    UnicodeEncodeError `DISALLOWED/controls` if any control
    characters are encountered. (Issue #29)
-   Update internal tables for Unicode 15.1.
-   Add Python 3.13-dev to CI build environment.
-   Change format of README and CHANGELOG files to Markdown.
-   Drop support for Python 3.3 and 3.4.

## 1.0.5

-   Update internal tables for Unicode 15.0.
-   Small type hint fix to one `.pyi` file.
-   Add Python 3.11 and 3.12 to CI build environment.
-   Update copyright year (2023).

## 1.0.4

-   Update internal tables for Unicode 14.0. These updates also affect
    context rules for Unicode 11.0 through 13.0. In limited cases under
    previous versions of precis_i18n, valid strings under Unicode
    11.0-13.0 were erroneously DISALLOWED due to context reasons
    hebrew_punctuation, katakana_middle_dot, and zero_width_nonjoiner.
    (Issue #19)
-   Add type hints for package. Contributed by `lovetox` (Issue #14).
-   Update copyright year (2022).

## 1.0.3

-   MANIFEST.in excludes `test_derived_props_files.py`; test
    data files are not packaged.
-   CI script now builds source package and runs tests from it.
-   Use Github Actions for continuous integration.
-   Update copyright year (2021).

## 1.0.2

-   `get_profile` now supports alternative unicodedata2 module (Issue
    #8).
-   `get_profile` maps \':\' to \'\_\' before look up (Issue #10).
-   Test Unicode 12.1 for Python 3.8.
-   Test Unicode 12.0 (Using optional unicodedata2 module)
-   Test Unicode 13.0 for Python 3.9 (Issue #9).
-   Update copyright year (2020).

## 1.0.1

-   Fixed a dict/set syntax typo that has no runtime effect (6ae6876).
-   Test forward compatibility of derived props test files as Unicode
    version increases.
-   Test Unicode 11.0 (Python 3.7).
-   Update copyright year (2019).

## 1.0.0

-   Release 1.0 version.
-   Add test that all codepoints are idempotent.
-   Update copyright year (2018).

## 0.7.0

-   (IMPORTANT) This version changes the results of the CaseMapped
    profiles due to publication of new RFC\'s.
-   The CaseMapped profiles now default to using ToLower instead of
    CaseFold.
-   Added profile variants for CaseFold, just for completeness.
-   Update references to RFC numbers in documentation and comments.

## 0.6.0

-   (IMPORTANT) This version changes the results of the Nickname
    profile.
-   Add support for proposed changes to RFC 7564 that will make the
    Nickname profile idempotent (Issue #3).
-   Add the \"DISALLOWED/not_idempotent\" error message.
-   Sign pypi package with gpg.

## 0.5.0

-   (API CHANGE) Profile\'s `enforce` method now returns a Unicode
    string instead of UTF-8 bytes. This API change affects code that
    uses get_profile() to obtain a profile. The codec still returns
    UTF-8 bytes. (Issue 2)
-   The codec search function now returns None when it doesn\'t find a
    matching codec.

## 0.4.1

-   Add LICENSE.txt and CHANGELOG.md to source tarball. (Issue 1)
-   Update travis and pypi metadata for Python 3.6.

## 0.4.0

-   Improve error messages when a string is disallowed.
-   Clean up test examples. Add a few more test cases.

## 0.3.0

-   Added the `get_profile` function to access profiles, when not using
    the codec.
-   Removed the global variables previously used to access profiles.
-   Added codecs for different case mappings of username and nickname.
-   Added codecs for base string classes: identifierclass and
    freeformclass.

## 0.2.2

-   Initial release to PyPI.
