"""Implements the PRECIS profile classes."""

import re
from functools import partial

from precis_i18n.baseclass import FreeFormClass, IdentifierClass, raise_error
from precis_i18n.bidi import bidi_rule, has_rtl
from precis_i18n.unicode import UnicodeData

# pylint: disable=no-self-use

_USERNAME_RULE_OVERRIDES = frozenset((
    "width_mapping_rule", "additional_mapping_rule", "case_mapping_rule",
    "normalization_rule", "directionality_rule",
))
_USERNAME_DATABASE_OVERRIDES = frozenset((
    "width_map", "lower", "casefold", "normalize", "bidirectional",
    "category", "control", "default_ignorable", "has_compat", "noncharacter", "old_hangul_jamo",
))


class Profile:
    """Base class for a PRECIS profile.

    Subclasses should override the `*_rule` methods.

    Args:
        base (BaseClass): Base string class.
        name (str): Name of profile.
        casemap (Optional[str]): Case mapping function: 'fold' or 'lower'.
    """

    _admit_before_mapping = False

    def __init__(self, base, name, casemap=None):
        self._base = base
        self._name = name
        if casemap not in (None, "fold", "lower"):
            raise ValueError("Unknown casemap value: %s" % casemap)
        self._casemap = casemap

    @property
    def base(self):
        """Base string class."""
        return self._base

    @property
    def name(self):
        """Profile name."""
        return self._name

    def enforce(self, value):
        """Ensure that all characters in `value` are allowed by the profile.

        If `value` is bytes, it's first decoded as UTF-8 to a string.

        Args:
            value (Union[str, bytes]): String value to enforce.

        Returns:
            str: Enforced value.

        Raises:
            UnicodeEncodeError: Value is disallowed by the profile.
            ValueError: `value` not a string or bytes.
        """
        value = _decode(value)
        if self._uses_stock_rules(value):
            return self._enforce_stock(value, self.case_mapping_rule)
        output = self.idempotence_check(self.apply_five_rules(value))
        return self._enforced_output(value, output)

    def comparison_key(self, value):
        """Return the exact UTF-8 bytes used to compare an enforced value."""
        return self.enforce(value).encode("utf-8")

    def _enforced_output(self, source, output):
        if not output:
            raise_error(self.name, source, -1, "empty")
        return self.base.enforce(output, self.name)

    def _uses_stock_rules(self, value):
        if type(self) not in _STOCK_PROFILES or type(value) is not str:
            return False
        ucd = self.base.ucd
        return type(ucd) is UnicodeData and ucd.identity_attestable

    def _enforce_stock(self, source, case_mapping):
        name = self.name
        enforce = self.base.enforce
        width_map = self.width_mapping_rule
        admitted = enforce(width_map(source), name)
        ucd = self.base.ucd
        if (type(self) is Username and admitted and admitted.isascii() and ucd.mode == "native"
                and _USERNAME_RULE_OVERRIDES.isdisjoint(vars(self))
                and _USERNAME_DATABASE_OVERRIDES.isdisjoint(vars(ucd))
                and "enforce" not in vars(self.base)):
            # Admission already excluded spaces and controls. ASCII case
            # mapping preserves that class, NFC, the absence of RTL and the
            # absence of width mappings. Its result is already stable.
            return admitted if self._casemap is None else admitted.lower()
        output = self._apply_mappings(admitted, case_mapping)
        if output == source:
            # An unchanged result from deterministic rules is stable. The
            # class check already covers it when preparation saw that string.
            if output and output == admitted:
                return output
            return self._enforced_output(source, output)

        reuse = (ucd.mode == "native" and "normalize" not in vars(ucd)
                 and "bidirectional" not in vars(ucd)
                 and "normalization_rule" not in vars(self)
                 and "directionality_rule" not in vars(self))
        # Recheck preparation before considering the previous output stable.
        for _ in range(3):
            prepared = width_map(output)
            if prepared != admitted:
                admitted = enforce(prepared, name)
            updated = self._apply_mappings(admitted, case_mapping, output if reuse else None)
            if updated == output:
                if output and output == admitted:
                    return output
                return self._enforced_output(source, output)
            output = updated
        raise_error(name, output, -1, "not_idempotent")

    def apply_five_rules(self, value):
        """Apply the five rules and any profile-specific preparation in order.

        Args:
            value (str): Value to enforce.

        Returns:
            str: Enforced value.
        """
        return self._apply_rules(value, self.case_mapping_rule)

    def _apply_rules(self, value, case_mapping):
        value = self.width_mapping_rule(value)
        # For Username this is the width-mapped IdentifierClass check.
        # OpaqueString and Nickname use identity width mapping, so they
        # check FreeformClass before any mapping or normalization.
        if self._admit_before_mapping:
            value = self.base.enforce(value, self.name)
        return self._apply_mappings(value, case_mapping)

    def _apply_mappings(self, value, case_mapping, checked_output=None):
        value = self.additional_mapping_rule(value)
        value = case_mapping(value)
        # The previous pass normalized this exact string and checked its
        # directionality. NFC and NFKC are idempotent for the native database.
        if checked_output is not None and value == checked_output:
            return value
        value = self.normalization_rule(value)
        return self.directionality_rule(value)

    def width_mapping_rule(self, value):
        """Apply width mapping rule.

        Args:
            value (str): Value to enforce.

        Returns:
            str: Enforced value.
        """
        return value

    def additional_mapping_rule(self, value):
        """Apply additional mapping rule.

        Args:
            value (str): Value to enforce.

        Returns:
            str: Enforced value.
        """
        return value

    def case_mapping_rule(self, value):
        """Apply case mapping rule.

        Args:
            value (str): Value to enforce.

        Returns:
            str: Enforced value.
        """
        if self._casemap == "lower":
            return self.base.ucd.lower(value)
        if self._casemap == "fold":
            return self.base.ucd.casefold(value)
        return value

    def normalization_rule(self, value):
        """Apply normalization rule.

        Args:
            value (str): Value to enforce.

        Returns:
            str: Enforced value.
        """
        return self.base.ucd.normalize("NFC", value)

    def directionality_rule(self, value):
        """Apply directionality rule.

        Args:
            value (str): Value to enforce.

        Returns:
            str: Enforced value.
        """
        return value

    def idempotence_check(self, value):
        """Check that profile result is idempotent.

        Profiles that are not idempotent should override this method.

        Args:
            value (str): Value to enforce.

        Returns:
            str: Enforced value.
        """
        return _stabilize(value, self.apply_five_rules, self.name)


class Username(Profile):
    """Concrete class for Username profile.

    Reference:
        Name:  UsernameCasePreserved | UsernameCaseMapped

        Base Class:  IdentifierClass.

        Applicability:  Usernames in security and application protocols.

        Replaces:  The SASLprep profile of stringprep.

        Width-Mapping Rule:  Map fullwidth and halfwidth characters to their
           decomposition mappings.

        Additional Mapping Rule:  None.

        Case-Mapping Rule:  None | Map uppercase and titlecase characters to
           lowercase.

        Normalization Rule:  NFC.

        Directionality Rule:  The "Bidi Rule" defined in RFC 5893 applies.

        Enforcement:  To be defined by security or application protocols that
           use this profile.

        Specification:  RFC 8265, Section 3.3.

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): Name of profile.
        casemap (Optional[str]): Case mapping function: 'fold' or 'lower'.
    """

    _admit_before_mapping = True

    def __init__(self, ucd, name, casemap=None):
        super().__init__(IdentifierClass(ucd), name, casemap)

    def width_mapping_rule(self, value):
        # Override
        return self.base.ucd.width_map(value)

    def directionality_rule(self, value):
        # Override
        # Only apply the "bidi rule" if the string contains RTL characters.
        if has_rtl(value, self.base.ucd):
            if not bidi_rule(value, self.base.ucd):
                raise_error(self.name, value, -1, "bidi_rule")
        return value


class OpaqueString(Profile):
    """Concrete class for OpaqueString profile.

    Reference:
        Name:  OpaqueString.

        Base Class:  FreeformClass.

        Applicability:  Passwords and other opaque strings in security and
           application protocols.

        Replaces:  The SASLprep profile of stringprep.

        Width-Mapping Rule:  None.

        Additional Mapping Rule:  Map non-ASCII space characters to ASCII
           space.

        Case-Mapping Rule:  None.

        Normalization Rule:  NFC.

        Directionality Rule:  None.

        Enforcement:  To be defined by security or application protocols that
           use this profile.

        Specification:  RFC 8265, Section 4.2.

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): Name of profile.
    """

    _admit_before_mapping = True

    def __init__(self, ucd, name):
        super().__init__(FreeFormClass(ucd), name, casemap=None)

    def additional_mapping_rule(self, value):
        # Override
        return self.base.ucd.map_nonascii_space_to_ascii(value)


class Nickname(Profile):
    """Concrete class for Nickname profile.

    Reference:
        Name:  Nickname.

        Base Class:  FreeformClass.

        Applicability:  Nicknames in messaging and text conferencing
           technologies; petnames for devices, accounts, and people; and
           other uses of nicknames or petnames.

        Replaces:  None.

        Width Mapping Rule:  None (handled via NFKC).

        Additional Mapping Rule:  Map non-ASCII space characters to ASCII
           space, strip leading and trailing space characters, map interior
           sequences of multiple space characters to a single ASCII space.

        Case Mapping Rule:  Unicode lowercase during RFC 8266 comparison.
           The case-mapped compatibility profiles apply their selected case
           rule during enforcement.

        Normalization Rule:  NFKC.

        Directionality Rule:  None.

        Enforcement:  To be specified by applications.

        Specification:  RFC 8266

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): Name of profile.
        casemap (Optional[str]): Case mapping function: 'fold' or 'lower'.
    """

    _admit_before_mapping = True

    def __init__(self, ucd, name, casemap=None):
        super().__init__(FreeFormClass(ucd), name, casemap)

    def additional_mapping_rule(self, value):
        # Override
        temp = self.base.ucd.map_nonascii_space_to_ascii(value)
        return re.sub(r"  +", " ", temp.strip(" "))

    def normalization_rule(self, value):
        # Override
        return self.base.ucd.normalize("NFKC", value)

    def comparison_key(self, value):
        """Return exact UTF-8 bytes after applying the nickname comparison rules."""
        if self._casemap is not None:
            return super().comparison_key(value)
        source = _decode(value)
        case_mapping = self.base.ucd.lower
        if self._uses_stock_rules(source):
            return self._enforce_stock(source, case_mapping).encode("utf-8")
        compare = partial(self._apply_rules, case_mapping=case_mapping)
        output = _stabilize(compare(source), compare, self.name)
        return self._enforced_output(source, output).encode("utf-8")


_STOCK_PROFILES = (Username, OpaqueString, Nickname)


def _decode(value):
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if not isinstance(value, str):
        raise ValueError("not a string")
    return value


def _stabilize(value, operation, name):
    # RFC 8264 section 7 recommends up to three passes after the first.
    for _ in range(3):
        updated = operation(value)
        if updated == value:
            return value
        value = updated
    raise_error(name, value, -1, "not_idempotent")
