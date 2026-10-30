"""Explicit missingness and observation states used across the domain."""

from enum import StrEnum


class EvidenceState(StrEnum):
    """Why a value is absent or unavailable.

    These values are intentionally not interchangeable with a negative result.
    """

    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_ASKED = "not_asked"
    NOT_TESTED = "not_tested"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class ObservationStatus(StrEnum):
    """Status of a condition-specific phenotypic observation."""

    PRESENT = "present"
    ABSENT = "absent"
    UNKNOWN = "unknown"

