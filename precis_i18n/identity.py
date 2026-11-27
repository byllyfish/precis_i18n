"""Stable identities for factory-created preparation policies."""

from hashlib import sha256
import json
from typing import NamedTuple, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from precis_i18n.baseclass import BaseClass
    from precis_i18n.profile import Profile


class ProfileIdentity(NamedTuple):
    """Description of the preparation and comparison semantics of a profile."""

    profile: str
    standards: str
    library_version: str
    semantic_revision: str
    unicode_version: str
    property_version: str
    execution_mode: str
    width_mapping: str
    case_mapping: str
    comparison_case_mapping: str
    normalization: str
    data_identity: str
    attestable: bool

    @property
    def fingerprint(self) -> Optional[str]:
        """Return a deterministic fingerprint for an identified data configuration."""
        if not self.attestable:
            return None
        payload = json.dumps(self._asdict(), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        return sha256(payload.encode("ascii")).hexdigest()


def get_profile_identity(profile: Union["BaseClass", "Profile"]) -> ProfileIdentity:
    """Return the captured identity of a profile or class from get_profile()."""
    identity = getattr(profile, "_profile_identity", None)
    if not isinstance(identity, ProfileIdentity):
        raise ValueError("Profile identity is available for factory-created profiles only")
    from precis_i18n.profile import Profile

    data = profile.base.ucd if isinstance(profile, Profile) else profile.ucd
    if data is not getattr(profile, "_profile_identity_data", None) or data.data_identity != identity.data_identity:
        raise ValueError("The profile Unicode data has changed since construction")
    return identity
