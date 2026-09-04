from datetime import UTC, datetime

from app.domain.money import Money
from app.domain.reconciliation import ReconciliationStatus
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.reconciliation_engine import ReconciliationEngine


def make_transaction(
    transaction_id: str = "pay_001",
    amount: int = 100000,
    reference_id: str = "ref_001",
) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        merchant_id="merchant_001",
        amount=Money(amount),
        transaction_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id=reference_id,
        status=TransactionStatus.SUCCESS,
    )


def make_settlement(
    settlement_id: str = "set_001",
    amount: int = 100000,
    transaction_reference: str = "pay_001",
) -> Settlement:
    return Settlement(
        settlement_id=settlement_id,
        merchant_id="merchant_001",
        amount=Money(amount),
        settlement_time=datetime(2026, 9, 2, 10, 0, tzinfo=UTC),
        reference_id="settle_ref_001",
        transaction_reference=transaction_reference,
        status=SettlementStatus.SETTLED,
    )


def test_exact_match() -> None:
    engine = ReconciliationEngine()

    result = engine.reconcile(
        transaction=make_transaction(),
        settlements=[make_settlement()],
    )

    assert result.status == ReconciliationStatus.MATCHED
    assert result.settlement_id == "set_001"
    assert result.expected_amount == Money(100000)
    assert result.actual_amount == Money(100000)
    assert result.difference == Money(0)


def test_amount_mismatch() -> None:
    engine = ReconciliationEngine()

    result = engine.reconcile(
        transaction=make_transaction(amount=100000),
        settlements=[make_settlement(amount=110000)],
    )

    assert result.status == ReconciliationStatus.MISMATCH
    assert result.difference == Money(10000)


def test_partial_settlement() -> None:
    engine = ReconciliationEngine()

    result = engine.reconcile(
        transaction=make_transaction(amount=100000),
        settlements=[make_settlement(amount=70000)],
    )

    assert result.status == ReconciliationStatus.PARTIAL_MATCH
    assert result.difference == Money(30000)


def test_missing_settlement() -> None:
    engine = ReconciliationEngine()

    result = engine.reconcile(
        transaction=make_transaction(),
        settlements=[],
    )

    assert result.status == ReconciliationStatus.MISSING_SETTLEMENT
    assert result.settlement_id is None
    assert result.actual_amount is None
    assert result.difference is None


def test_duplicate_settlement() -> None:
    engine = ReconciliationEngine()

    result = engine.reconcile(
        transaction=make_transaction(),
        settlements=[
            make_settlement(settlement_id="set_001"),
            make_settlement(settlement_id="set_002"),
        ],
    )

    assert result.status == ReconciliationStatus.DUPLICATE
    assert result.settlement_id is None


def test_reference_mismatch_is_not_matched() -> None:
    engine = ReconciliationEngine()

    result = engine.reconcile(
        transaction=make_transaction(transaction_id="pay_001"),
        settlements=[
            make_settlement(
                settlement_id="set_001",
                transaction_reference="pay_999",
            )
        ],
    )

    assert result.status == ReconciliationStatus.MISSING_SETTLEMENT
    assert result.settlement_id is None