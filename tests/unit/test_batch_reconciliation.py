from app.domain.reconciliation import ReconciliationStatus
from app.services.batch_reconciliation import BatchReconciliationService
from app.services.reconciliation_engine import ReconciliationEngine
from app.services.synthetic_data_generator import SyntheticDataGenerator


def test_batch_reconciliation_processes_all_transactions() -> None:
    transactions, settlements = SyntheticDataGenerator(seed=42).generate()

    service = BatchReconciliationService(ReconciliationEngine())

    results = service.reconcile(transactions, settlements)

    assert len(results) == len(transactions)


def test_batch_reconciliation_produces_expected_scenarios() -> None:
    transactions, settlements = SyntheticDataGenerator(seed=42).generate()

    service = BatchReconciliationService(ReconciliationEngine())

    results = service.reconcile(transactions, settlements)

    statuses = [result.status for result in results]

    assert ReconciliationStatus.MATCHED in statuses
    assert ReconciliationStatus.PARTIAL_MATCH in statuses
    assert ReconciliationStatus.MISMATCH in statuses
    assert ReconciliationStatus.MISSING_SETTLEMENT in statuses
    assert ReconciliationStatus.DUPLICATE in statuses


def test_batch_reconciliation_preserves_transaction_order() -> None:
    transactions, settlements = SyntheticDataGenerator(seed=42).generate()

    service = BatchReconciliationService(ReconciliationEngine())

    results = service.reconcile(transactions, settlements)

    assert [result.transaction_id for result in results] == [
        transaction.transaction_id for transaction in transactions
    ]


def test_batch_reconciliation_summary_counts_statuses() -> None:
    transactions, settlements = SyntheticDataGenerator(seed=42).generate()

    service = BatchReconciliationService(ReconciliationEngine())

    results = service.reconcile(transactions, settlements)
    summary = service.summarize(results)

    assert summary.total_transactions == 100
    assert summary.matched == 96
    assert summary.partial_matches == 1
    assert summary.mismatches == 1
    assert summary.missing_settlements == 1
    assert summary.duplicates == 1


def test_batch_reconciliation_summary_handles_empty_results() -> None:
    service = BatchReconciliationService(ReconciliationEngine())

    summary = service.summarize([])

    assert summary.total_transactions == 0
    assert summary.matched == 0
    assert summary.partial_matches == 0
    assert summary.mismatches == 0
    assert summary.missing_settlements == 0
    assert summary.duplicates == 0