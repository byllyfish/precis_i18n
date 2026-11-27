"""Immutable supplementary data generated from the Unicode Character Database."""

import hashlib
import json
from functools import lru_cache
from pkgutil import get_data
from types import MappingProxyType
from typing import Iterable, List, Mapping, NamedTuple, Tuple, Union

from precis_i18n.codepointset import CodepointSet

AVAILABLE = ("17.0.0", "18.0.0")
CURRENT = AVAILABLE[-1]


class Tables(NamedTuple):
    version: str
    identity: str
    width: Mapping[int, str]
    lower: Mapping[int, str]
    fold: Mapping[int, str]
    spaces: Mapping[int, str]
    sigma: int
    final_sigma: str
    ranges: Mapping[str, CodepointSet]


def _translation(values: Mapping[str, Union[List[int], int]]) -> Mapping[int, str]:
    return MappingProxyType({
        int(cp): "".join(map(chr, mapping)) if isinstance(mapping, list) else chr(mapping)
        for cp, mapping in values.items()
    })


def _codepoint_set(ranges: Iterable[Tuple[int, int]]) -> CodepointSet:
    return CodepointSet("\n".join(
        "{:04X}..{:04X}".format(first, last) for first, last in ranges
    ))


@lru_cache(maxsize=len(AVAILABLE))
def load(version: str) -> Tables:
    """Load and share only immutable Unicode data, never application input."""
    if version not in AVAILABLE:
        raise ValueError("Unsupported versioned Unicode data: {}".format(version))
    filename = "_unicode_{}.json".format(version.split(".", 1)[0])
    payload = get_data("precis_i18n", filename)
    if payload is None:
        raise RuntimeError("Missing bundled Unicode data")
    document = json.loads(payload)
    if document["version"] != version:
        raise RuntimeError("Wrong bundled Unicode data version")
    sigma, final_sigma = document["context"]["final_sigma"]
    return Tables(
        version, hashlib.sha256(payload).hexdigest(),
        _translation(document["width"]), _translation(document["lower"]),
        _translation(document["fold"]), _translation(document["spaces"]),
        sigma, "".join(map(chr, final_sigma)),
        MappingProxyType({
            name: _codepoint_set(ranges) for name, ranges in document["ranges"].items()
        }),
    )


def versioned_lower(value: str, tables: Tables) -> str:
    """Apply default Unicode lowercase including the locale-neutral final sigma."""
    if chr(tables.sigma) not in value:
        return value.translate(tables.lower)

    result: List[str] = []
    pending = None
    after_cased = False
    cased = tables.ranges["cased"]
    ignored = tables.ranges["case_ignorable"]
    for char in value:
        cp = ord(char)
        if cp not in ignored:
            next_is_cased = cp in cased
            if pending is not None and not next_is_cased:
                result[pending] = tables.final_sigma
            pending = len(result) if cp == tables.sigma and after_cased else None
            after_cased = next_is_cased
        result.append(tables.lower.get(cp, char))
    if pending is not None:
        result[pending] = tables.final_sigma
    return "".join(result)
