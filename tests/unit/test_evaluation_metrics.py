from app.domain.evaluation import GroundTruth, GroundTruthStatus
from app.domain.money import Money
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus
from app.services.evaluation_metrics import EvaluationMetrics


def build_ground_truth(
    transaction_id: str,
    status: GroundTruthStatus,
) -> GroundTruth:
    return GroundTruth(
        transaction_id=transaction_id,
        expected_status=status,
        has_exception=status != GroundTruthStatus.MATCHED,
    )


def build_result(
    transaction_id: str,
    status: ReconciliationStatus,
) -> ReconciliationResult:
    return ReconciliationResult(
        transaction_id=transaction_id,
        settlement_id=None,
        status=status,
        expected_amount=Money(10000),
        actual_amount=None,
        difference=None,
        reason="Evaluation test result.",
    )


def test_metrics_calculate_status_accuracy() -> None:
    ground_truth = [
        build_ground_truth("pay_0001", GroundTruthStatus.MATCHED),
        build_ground_truth("pay_0002", GroundTruthStatus.PARTIAL_MATCH),
        build_ground_truth("pay_0003", GroundTruthStatus.MISMATCH),
        build_ground_truth("pay_0004", GroundTruthStatus.MISSING_SETTLEMENT),
    ]

    results = [
        build_result("pay_0001", ReconciliationStatus.MATCHED),
        build_result("pay_0002", ReconciliationStatus.PARTIAL_MATCH),
        build_result("pay_0003", ReconciliationStatus.MISMATCH),
        build_result("pay_0004", ReconciliationStatus.MATCHED),
    ]

    metrics = EvaluationMetrics().calculate(ground_truth, results)

    assert metrics.total_transactions == 4
    assert metrics.correct_status_predictions == 3
    assert metrics.status_accuracy == 0.75


def test_metrics_calculate_exception_precision_and_recall() -> None:
    ground_truth = [
        build_ground_truth("pay_0001", GroundTruthStatus.MATCHED),
        build_ground_truth("pay_0002", GroundTruthStatus.PARTIAL_MATCH),
        build_ground_truth("pay_0003", GroundTruthStatus.MISMATCH),
        build_ground_truth("pay_0004", GroundTruthStatus.MISSING_SETTLEMENT),
    ]

    results = [
        build_result("pay_0001", ReconciliationStatus.MATCHED),
        build_result("pay_0002", ReconciliationStatus.PARTIAL_MATCH),
        build_result("pay_0003", ReconciliationStatus.MATCHED),
        build_result("pay_0004", ReconciliationStatus.MISMATCH),
    ]

    metrics = EvaluationMetrics().calculate(ground_truth, results)

    assert metrics.actual_exceptions == 3
    assert metrics.predicted_exceptions == 2
    assert metrics.true_positive_exceptions == 2
    assert metrics.exception_precision == 1.0
    assert metrics.exception_recall == 2 / 3


def test_metrics_return_zero_when_no_exceptions_exist() -> None:
    ground_truth = [
        build_ground_truth("pay_0001", GroundTruthStatus.MATCHED),
        build_ground_truth("pay_0002", GroundTruthStatus.MATCHED),
    ]

    results = [
        build_result("pay_0001", ReconciliationStatus.MATCHED),
        build_result("pay_0002", ReconciliationStatus.MATCHED),
    ]

    metrics = EvaluationMetrics().calculate(ground_truth, results)

    assert metrics.actual_exceptions == 0
    assert metrics.predicted_exceptions == 0
    assert metrics.true_positive_exceptions == 0
    assert metrics.exception_precision == 0.0
    assert metrics.exception_recall == 0.0


def test_metrics_return_zero_for_empty_dataset() -> None:
    metrics = EvaluationMetrics().calculate([], [])

    assert metrics.total_transactions == 0
    assert metrics.correct_status_predictions == 0
    assert metrics.status_accuracy == 0.0
    assert metrics.actual_exceptions == 0
    assert metrics.predicted_exceptions == 0
    assert metrics.true_positive_exceptions == 0
    assert metrics.exception_precision == 0.0
    assert metrics.exception_recall == 0.0


def test_metrics_reject_mismatched_dataset_lengths() -> None:
    ground_truth = [
        build_ground_truth("pay_0001", GroundTruthStatus.MATCHED),
    ]

    results = [
        build_result("pay_0001", ReconciliationStatus.MATCHED),
        build_result("pay_0002", ReconciliationStatus.MATCHED),
    ]

    try:
        EvaluationMetrics().calculate(ground_truth, results)
        raise AssertionError("Expected ValueError for mismatched dataset lengths.")
    except ValueError as error:
        assert str(error) == (
            "Ground truth and reconciliation results must have the same length."
        )
