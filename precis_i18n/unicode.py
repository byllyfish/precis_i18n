"""Implements the UnicodeData class."""

import json
import re
import sys
import unicodedata
from types import ModuleType

from precis_i18n._unicode_tables import AVAILABLE, CURRENT, load, versioned_lower

# pylint: disable=no-self-use


def _version_to_float(version):
    m = re.match(r"^([0-9]+\.[0-9]+)\.[0-9]+$", version)
    if not m:
        raise ValueError("Unexpected unicode version format: %s" % version)
    return float(m.group(1))


class UnicodeData:
    """Adapter for Python's built-in unicodedata module and compatible providers.

    The default and legacy alternate providers retain interpreter case mapping
    and use the current supplementary property tables. An explicitly selected
    version uses matching provider data and version-pinned supplementary data
    and case mappings. A custom versioned provider must supply a stable
    ``precis_data_identity`` identifying its data and operations. The declaration
    is trusted, and the provider must keep its semantics fixed.

    Args:
        ucd (Union[module,object]): Implements the unicodedata interface.
        unicode_version (Optional[str]): Select a matching versioned configuration.
    """

    def __init__(self, ucd=None, *, unicode_version=None):
        self._ucd = unicodedata if ucd is None else ucd
        version = getattr(self._ucd, "unidata_version", None)
        if not isinstance(version, str) or not all(
            callable(getattr(self._ucd, method, None))
            for method in ("category", "combining", "bidirectional", "normalize")
        ):
            raise ValueError("Expected a Unicode data provider")
        self._version = _version_to_float(version)
        self._data_version = version

        if unicode_version is not None:
            if unicode_version not in AVAILABLE:
                raise ValueError("Unsupported versioned Unicode data: {}".format(unicode_version))
            if unicode_version != version:
                raise ValueError("Versioned configuration requires Unicode data {}".format(unicode_version))
        self._tables = load(CURRENT if unicode_version is None else unicode_version)
        self._mode = "native" if self._ucd is unicodedata else "legacy"
        if unicode_version is not None:
            self._mode = "versioned"
        self._data_identity, self._identity_attestable = self._describe_data()
        if self.mode == "versioned" and not self.identity_attestable:
            raise ValueError("Versioned Unicode provider requires a stable data identity")

    @property
    def version(self):
        return self._version

    @property
    def data_version(self):
        """Return the exact Unicode data version used by the backend provider."""
        return self._data_version

    @property
    def property_version(self):
        """Return the Unicode generation of the supplementary property tables."""
        return self._tables.version

    @property
    def mode(self):
        """Return the native, legacy alternate, or explicitly versioned mode."""
        return self._mode

    @property
    def data_identity(self):
        """Identify the selected provider, tables, and runtime casing where applicable."""
        return self._data_identity

    @property
    def identity_attestable(self):
        """Report whether the backend has an identifiable implementation or data contract."""
        return self._identity_attestable

    def _describe_data(self):
        provider_type = type(self._ucd)
        provider = getattr(self._ucd, "__name__", provider_type.__qualname__)
        origin = getattr(self._ucd, "__module__", provider_type.__module__)
        custom_id = getattr(self._ucd, "precis_data_identity", None)
        if not isinstance(custom_id, str) or not custom_id.strip():
            custom_id = None
        registered = (
            _unicodedata2_revision()
            if isinstance(self._ucd, ModuleType) and self._ucd is sys.modules.get("unicodedata2")
            else None
        )
        revision = registered or getattr(self._ucd, "__version__", None)
        fields = [
            self.mode, str(origin), str(provider), str(revision), custom_id,
            self.data_version, self._tables.identity,
        ]
        if self.mode != "versioned":
            fields.extend((sys.implementation.name, sys.version, unicodedata.unidata_version))
        attestable = self._ucd is unicodedata or registered is not None or custom_id is not None
        return json.dumps(fields, ensure_ascii=True, separators=(",", ":")), attestable

    # These methods call through to the underlying unicodedata object.

    def category(self, char):
        return self._ucd.category(char)

    def combining(self, char):
        return self._ucd.combining(char)

    def bidirectional(self, char):
        return self._ucd.bidirectional(char)

    def normalize(self, form, value):
        return self._ucd.normalize(form, value)

    def width_map(self, value):
        """Map only the UCD's literal wide and narrow decompositions."""
        if value.isascii():
            return value
        return value.translate(self._tables.width)

    def lower(self, value):
        """Apply default lowercase under the selected casing configuration."""
        if self.mode == "versioned":
            return versioned_lower(value, self._tables)
        return value.lower()

    def casefold(self, value):
        """Apply full, non-Turkic case folding under the selected configuration."""
        if self.mode == "versioned":
            return value.translate(self._tables.fold)
        return value.casefold()

    def map_nonascii_space_to_ascii(self, value):
        """Convert non-ASCII space separators (Zs) to ASCII space."""
        if value.isascii():
            return value
        return value.translate(self._tables.spaces)

    def default_ignorable(self, cp):
        return cp in self._tables.ranges["default_ignorable"]

    def has_compat(self, cp):
        char = chr(cp)
        norm = self.normalize("NFKC", char)
        assert norm
        return norm != char

    def control(self, cp):
        return (0x00 <= cp <= 0x1F) or (0x7F <= cp <= 0x9F)

    def noncharacter(self, cp):
        last = cp & 0x0000FFFF
        return (0xFFFE <= last <= 0xFFFF) or (0xFDD0 <= cp <= 0xFDEF)

    def old_hangul_jamo(self, cp):
        return cp in self._tables.ranges["jamo"]

    def greek_script(self, cp):
        return cp in self._tables.ranges["greek"]

    def hebrew_script(self, cp):
        return cp in self._tables.ranges["hebrew"]

    def hiragana_katakana_han_script(self, cp):
        return cp in self._tables.ranges["hiragana_katakana_han"]

    def combining_virama(self, cp):
        return self.combining(chr(cp)) == 9

    def arabic_indic(self, cp):
        return 0x0660 <= cp <= 0x0669

    def extended_arabic_indic(self, cp):
        return 0x06F0 <= cp <= 0x06F9

    def valid_jointype(self, value, offset):
        """Check the parsed join-control position without copying input slices."""
        assert 0x200C <= ord(value[offset]) <= 0x200D
        if offset < 0:
            offset += len(value)
        # Transparent runs end at nontransparent characters, including
        # join controls. Across all join controls each run is scanned at most twice.
        return self._scan_join(value, range(offset - 1, -1, -1), "L") and self._scan_join(
            value, range(offset + 1, len(value)), "R"
        )

    def _scan_join(self, value, offsets, term):
        for index in offsets:
            join_type = self._join_type(ord(value[index]))
            if join_type in (term, "D"):
                return True
            if join_type != "T":
                return False
        return False

    def _join_type(self, cp):
        ranges = self._tables.ranges
        if cp in ranges["dual_joining"]:
            return "D"
        if cp in ranges["right_joining"]:
            return "R"
        if cp in ranges["left_joining"]:
            return "L"
        if cp in ranges["transparent_joining"]:
            return "T"
        return None


def _unicodedata2_revision():
    try:
        from importlib.metadata import PackageNotFoundError, version
    except ImportError:
        return None  # Python 3.7 lacks importlib.metadata.
    try:
        return version("unicodedata2")
    except PackageNotFoundError:
        return None
