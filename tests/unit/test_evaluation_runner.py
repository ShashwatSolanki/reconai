from app.services.evaluation_runner import EvaluationRunner


def test_evaluation_runner_executes_complete_pipeline() -> None:
    runner = EvaluationRunner(
        seed=42,
        record_count=100,
    )

    result = runner.run()

    assert result.total_transactions == 100
    assert result.total_settlements == 100
    assert len(result.ground_truth) == 100
    assert len(result.reconciliation_results) == 100

    assert result.metrics.total_transactions == 100
    assert result.metrics.status_accuracy == 1.0
    assert result.metrics.exception_precision == 1.0
    assert result.metrics.exception_recall == 1.0


def test_evaluation_runner_is_reproducible() -> None:
    first = EvaluationRunner(seed=42, record_count=100).run()
    second = EvaluationRunner(seed=42, record_count=100).run()

    assert first.metrics == second.metrics
    assert first.ground_truth == second.ground_truth
    assert first.reconciliation_results == second.reconciliation_results
