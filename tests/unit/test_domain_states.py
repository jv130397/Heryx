from rarepedigree.domain import EvidenceState, ObservationStatus


def test_unknown_is_not_a_negative_observation() -> None:
    assert ObservationStatus.UNKNOWN is not ObservationStatus.ABSENT


def test_missingness_reasons_remain_distinct() -> None:
    assert len(EvidenceState) == 6
    assert EvidenceState.NOT_TESTED != EvidenceState.UNKNOWN
    assert EvidenceState.WITHHELD != EvidenceState.NOT_ASKED
