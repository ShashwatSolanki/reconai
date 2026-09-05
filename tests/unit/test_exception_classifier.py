
import pytest

from app.domain.exception import ExceptionCategory
from app.domain.money import Money
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus
from app.services.exception_classifier import ExceptionClassifier


def make_result(
    status: ReconciliationStatus,
    *,
    actual_amount: Money | None = None,
    difference: Money | None = None,
) -> ReconciliationResult:
    return ReconciliationResult(
        transaction_id="txn_001",
        settlement_id="set_001",
        status=status,
        expected_amount=Money(10000),
        actual_amount=actual_amount,
        difference=difference,
        reason="test result",
    )


@pytest.mark.parametrize(
    ("status", "category"),
    [
        (ReconciliationStatus.PARTIAL_MATCH, ExceptionCategory.PARTIAL_SETTLEMENT),
        (ReconciliationStatus.MISMATCH, ExceptionCategory.AMOUNT_MISMATCH),
        (ReconciliationStatus.MISSING_SETTLEMENT, ExceptionCategory.MISSING_SETTLEMENT),
        (ReconciliationStatus.DUPLICATE, ExceptionCategory.DUPLICATE_SETTLEMENT),
    ],
)
def test_classifies_reconciliation_exception(
    status: ReconciliationStatus,
    category: ExceptionCategory,
) -> None:
    result = make_result(
        status,
        actual_amount=Money(8000),
        difference=Money(2000),
    )

    exception = ExceptionClassifier().classify(result)

    assert exception is not None
    assert exception.transaction_id == "txn_001"
    assert exception.category == category


def test_matched_result_has_no_exception() -> None:
    result = make_result(ReconciliationStatus.MATCHED)

    assert ExceptionClassifier().classify(result) is None