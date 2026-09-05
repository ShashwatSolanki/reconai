from datetime import UTC, datetime

import pytest

from app.domain.money import Money
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.reconai_service import ReconAIService


def make_transaction() -> Transaction:
    return Transaction(
        transaction_id="pay_001",
        merchant_id="merchant_001",
        amount=Money(10000),
        transaction_time=datetime(2026, 9, 1, 10, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_pay_001",
        status=TransactionStatus.SUCCESS,
    )


def make_settlement(amount: int = 9900) -> Settlement:
    return Settlement(
        settlement_id="set_001",
        merchant_id="merchant_001",
        amount=Money(amount),
        settlement_time=datetime(2026, 9, 1, 12, tzinfo=UTC),
        reference_id="ref_set_001",
        transaction_reference="pay_001",
        status=SettlementStatus.SETTLED,
    )


def test_registers_exception_for_mismatch() -> None:
    transaction = make_transaction()
    settlement = make_settlement()

    result = ReconciliationResult(
        transaction_id="pay_001",
        settlement_id="set_001",
        status=ReconciliationStatus.MISMATCH,
        expected_amount=Money(10000),
        actual_amount=Money(9900),
        difference=Money(100),
        reason="Settlement amount differs from transaction amount.",
    )

    service = ReconAIService()

    exception = service.register_exception(
        result=result,
        transaction=transaction,
        settlement=settlement,
    )

    assert exception is not None
    assert exception.transaction_id == "pay_001"
    assert exception.category.value == "amount_mismatch"
    assert exception.exception_id in service.exceptions


def test_does_not_register_matched_transaction() -> None:
    transaction = make_transaction()
    settlement = make_settlement(10000)

    result = ReconciliationResult(
        transaction_id="pay_001",
        settlement_id="set_001",
        status=ReconciliationStatus.MATCHED,
        expected_amount=Money(10000),
        actual_amount=Money(10000),
        difference=Money(0),
        reason="Transaction and settlement matched.",
    )

    service = ReconAIService()

    exception = service.register_exception(
        result=result,
        transaction=transaction,
        settlement=settlement,
    )

    assert exception is None
    assert service.exceptions == {}


def test_investigation_runs_agent_decision_and_audit() -> None:
    transaction = make_transaction()
    settlement = make_settlement(9900)

    result = ReconciliationResult(
        transaction_id="pay_001",
        settlement_id="set_001",
        status=ReconciliationStatus.MISMATCH,
        expected_amount=Money(10000),
        actual_amount=Money(9900),
        difference=Money(100),
        reason="Settlement amount differs from transaction amount.",
    )

    service = ReconAIService()

    exception = service.register_exception(
        result=result,
        transaction=transaction,
        settlement=settlement,
    )

    assert exception is not None

    workflow = service.investigate(exception.exception_id)

    assert workflow["exception"] == exception

    investigation = workflow["investigation"]
    decision = workflow["decision"]
    action = workflow["action"]
    audit_event = workflow["audit_event"]

    assert investigation.root_cause.value == "fee_deduction"
    assert investigation.recommendation.value == "accept_settlement"
    assert investigation.confidence == 0.85

    # 0.85 is below the 0.90 automatic-resolution threshold.
    assert decision.action == "escalate"
    assert decision.requires_human_review is True

    assert action.action == "escalate"
    assert action.executed is False

    assert audit_event.exception_id == exception.exception_id
    assert audit_event.executed is False


def test_missing_exception_cannot_be_investigated() -> None:
    service = ReconAIService()

    with pytest.raises(KeyError):
        service.investigate("does_not_exist")