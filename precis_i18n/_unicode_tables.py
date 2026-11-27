"""Immutable supplementary data generated from the Unicode Character Database."""

import hashlib
import json
from _thread import allocate_lock
from pkgutil import get_data
from types import MappingProxyType
from typing import Dict, List, Mapping, NamedTuple, Union

from precis_i18n.codepointset import CodepointSet

AVAILABLE = ("17.0.0", "18.0.0")
CURRENT = AVAILABLE[-1]
_LOAD_LOCKS = {version: allocate_lock() for version in AVAILABLE}
_Translation = Mapping[int, Union[int, str]]


class Tables(NamedTuple):
    version: str
    identity: str
    width: _Translation
    lower: _Translation
    fold: _Translation
    spaces: _Translation
    sigma: int
    final_sigma: str
    ranges: Mapping[str, CodepointSet]


_LOADED: Dict[str, Tables] = {}


def _translation(values: Mapping[str, Union[List[int], int]]) -> _Translation:
    table: Dict[int, Union[int, str]] = {}
    for cp, mapping in values.items():
        if isinstance(mapping, list):
            table[int(cp)] = mapping[0] if len(mapping) == 1 else "".join(map(chr, mapping))
        else:
            table[int(cp)] = mapping
    return MappingProxyType(table)


def load(version: str) -> Tables:
    """Load and share only immutable Unicode data, never application input."""
    table = _LOADED.get(version)
    if table is not None:
        return table
    lock = _LOAD_LOCKS.get(version)
    if lock is None:
        raise ValueError("Unsupported versioned Unicode data: {}".format(version))
    # A concurrent miss must share the completed table. Failed loads publish
    # nothing, and later callers can retry. Established lookups take no lock.
    with lock:
        table = _LOADED.get(version)
        if table is None:
            table = _load_tables(version)
            _LOADED[version] = table
        return table


def _load_tables(version: str) -> Tables:
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
            name: CodepointSet._from_sorted_ranges(ranges)
            for name, ranges in document["ranges"].items()
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
        mapping = tables.lower.get(cp, char)
        result.append(chr(mapping) if isinstance(mapping, int) else mapping)
    if pending is not None:
        result[pending] = tables.final_sigma
    return "".join(result)
