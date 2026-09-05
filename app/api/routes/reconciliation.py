from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.repositories.settlement import SqlAlchemySettlementRepository
from app.db.repositories.transaction import SqlAlchemyTransactionRepository
from app.domain.money import Money
from app.domain.reconciliation import ReconciliationResult
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.batch_reconciliation import BatchReconciliationService
from app.services.container import reconai_service
from app.services.persisted_reconciliation import PersistedReconciliationService
from app.services.reconciliation_engine import ReconciliationEngine

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])


class MoneyRequest(BaseModel):
    amount: int = Field(ge=0)
    currency: str = "INR"


class TransactionRequest(BaseModel):
    transaction_id: str
    merchant_id: str
    amount: MoneyRequest
    transaction_time: datetime
    payment_method: PaymentMethod
    reference_id: str
    status: TransactionStatus

    @field_validator("transaction_id", "merchant_id", "reference_id")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value cannot be empty.")
        return value

    @field_validator("transaction_time")
    @classmethod
    def validate_timezone_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("transaction_time must include timezone information.")
        return value


class SettlementRequest(BaseModel):
    settlement_id: str
    merchant_id: str
    amount: MoneyRequest
    settlement_time: datetime
    reference_id: str
    transaction_reference: str
    status: SettlementStatus

    @field_validator(
        "settlement_id",
        "merchant_id",
        "reference_id",
        "transaction_reference",
    )
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value cannot be empty.")
        return value

    @field_validator("settlement_time")
    @classmethod
    def validate_timezone_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("settlement_time must include timezone information.")
        return value

class ReconciliationRequest(BaseModel):
    transactions: list[TransactionRequest]
    settlements: list[SettlementRequest]


class MoneyResponse(BaseModel):
    amount: int
    currency: str


class ReconciliationResultResponse(BaseModel):
    transaction_id: str
    settlement_id: str | None
    status: str
    expected_amount: MoneyResponse
    actual_amount: MoneyResponse | None
    difference: MoneyResponse | None
    reason: str


class ReconciliationSummaryResponse(BaseModel):
    total_transactions: int
    matched: int
    partial_matches: int
    mismatches: int
    missing_settlements: int
    duplicates: int


class ReconciliationResponse(BaseModel):
    results: list[ReconciliationResultResponse]
    summary: ReconciliationSummaryResponse


def _to_transaction(request: TransactionRequest) -> Transaction:
    return Transaction(
        transaction_id=request.transaction_id,
        merchant_id=request.merchant_id,
        amount=Money(request.amount.amount, request.amount.currency),
        transaction_time=request.transaction_time,
        payment_method=request.payment_method,
        reference_id=request.reference_id,
        status=request.status,
    )


def _to_settlement(request: SettlementRequest) -> Settlement:
    return Settlement(
        settlement_id=request.settlement_id,
        merchant_id=request.merchant_id,
        amount=Money(request.amount.amount, request.amount.currency),
        settlement_time=request.settlement_time,
        reference_id=request.reference_id,
        transaction_reference=request.transaction_reference,
        status=request.status,
    )


def _to_money_response(money: Money) -> MoneyResponse:
    return MoneyResponse(amount=money.amount, currency=money.currency)


def _to_result_response(result: ReconciliationResult) -> ReconciliationResultResponse:
    return ReconciliationResultResponse(
        transaction_id=result.transaction_id,
        settlement_id=result.settlement_id,
        status=result.status.value,
        expected_amount=_to_money_response(result.expected_amount),
        actual_amount=(
            _to_money_response(result.actual_amount)
            if result.actual_amount is not None
            else None
        ),
        difference=(
            _to_money_response(result.difference)
            if result.difference is not None
            else None
        ),
        reason=result.reason,
    )


@router.post("", response_model=ReconciliationResponse)
def reconcile(request: ReconciliationRequest) -> ReconciliationResponse:
    transactions = [_to_transaction(item) for item in request.transactions]
    settlements = [_to_settlement(item) for item in request.settlements]

    service = BatchReconciliationService(engine=ReconciliationEngine())
    results = service.reconcile(
        transactions=transactions,
        settlements=settlements,
    )
    summary = service.summarize(results)
    settlement_by_id = {
        settlement.settlement_id: settlement
        for settlement in settlements
    }

    transaction_by_id = {
        transaction.transaction_id: transaction
        for transaction in transactions
    }

    for result in results:
        transaction = transaction_by_id[result.transaction_id]

        settlement = (
            settlement_by_id[result.settlement_id]
            if result.settlement_id is not None
            else None
        )

        reconai_service.register_exception(
            result=result,
            transaction=transaction,
            settlement=settlement,
        )
    return ReconciliationResponse(
        results=[_to_result_response(result) for result in results],
        summary=ReconciliationSummaryResponse(
            total_transactions=summary.total_transactions,
            matched=summary.matched,
            partial_matches=summary.partial_matches,
            mismatches=summary.mismatches,
            missing_settlements=summary.missing_settlements,
            duplicates=summary.duplicates,
        ),
    )


@router.post("/merchants/{merchant_id}", response_model=ReconciliationResponse)
def reconcile_persisted_merchant(
    merchant_id: str,
    db: Session = Depends(get_db),  # noqa: B008
) -> ReconciliationResponse:
    transaction_repository = SqlAlchemyTransactionRepository(db)
    settlement_repository = SqlAlchemySettlementRepository(db)

    service = PersistedReconciliationService(
        transaction_repository=transaction_repository,
        settlement_repository=settlement_repository,
        reconciliation_service=BatchReconciliationService(
            engine=ReconciliationEngine()
        ),
    )

    results = service.reconcile_merchant(merchant_id)
    summary = service.summarize(results)

    return ReconciliationResponse(
        results=[_to_result_response(result) for result in results],
        summary=ReconciliationSummaryResponse(
            total_transactions=summary.total_transactions,
            matched=summary.matched,
            partial_matches=summary.partial_matches,
            mismatches=summary.mismatches,
            missing_settlements=summary.missing_settlements,
            duplicates=summary.duplicates,
        ),
    )