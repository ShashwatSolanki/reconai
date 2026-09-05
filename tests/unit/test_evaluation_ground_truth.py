from app.domain.evaluation import GroundTruth, GroundTruthStatus


def test_ground_truth_stores_expected_reconciliation_status() -> None:
    ground_truth = GroundTruth(
        transaction_id="pay_0001",
        expected_status=GroundTruthStatus.MATCHED,
        has_exception=False,
    )

    assert ground_truth.transaction_id == "pay_0001"
    assert ground_truth.expected_status == GroundTruthStatus.MATCHED
    assert ground_truth.has_exception is False


def test_ground_truth_requires_exception_for_non_matched_status() -> None:
    ground_truth = GroundTruth(
        transaction_id="pay_0002",
        expected_status=GroundTruthStatus.PARTIAL_MATCH,
        has_exception=True,
    )

    assert ground_truth.expected_status == GroundTruthStatus.PARTIAL_MATCH
    assert ground_truth.has_exception is True


def test_ground_truth_rejects_empty_transaction_id() -> None:
    import pytest

    with pytest.raises(ValueError, match="transaction_id cannot be empty"):
        GroundTruth(
            transaction_id="",
            expected_status=GroundTruthStatus.MATCHED,
            has_exception=False,
        )


def test_ground_truth_rejects_inconsistent_exception_flag() -> None:
    import pytest

    with pytest.raises(ValueError, match="matched transaction cannot have an exception"):
        GroundTruth(
            transaction_id="pay_0003",
            expected_status=GroundTruthStatus.MATCHED,
            has_exception=True,
        )