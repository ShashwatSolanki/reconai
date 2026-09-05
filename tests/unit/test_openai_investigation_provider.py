from datetime import UTC, datetime

from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    RootCauseCategory,
)
from app.domain.investigation_context import InvestigationContext
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.openai_investigation_provider import OpenAIInvestigationProvider


def build_context() -> InvestigationContext:
    transaction = Transaction(
        transaction_id="pay_0001",
        merchant_id="merchant_001",
        amount=Money(100000),
        transaction_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_0001",
        status=TransactionStatus.SUCCESS,
    )

    settlement = Settlement(
        settlement_id="set_0001",
        merchant_id="merchant_001",
        amount=Money(98000),
        settlement_time=datetime(2026, 9, 2, 10, 0, tzinfo=UTC),
        reference_id="settle_ref_0001",
        transaction_reference="pay_0001",
        status=SettlementStatus.SETTLED,
    )

    exception = FinancialException(
        exception_id="exc_0001",
        transaction_id="pay_0001",
        settlement_id="set_0001",
        category=ExceptionCategory.AMOUNT_MISMATCH,
        severity=ExceptionSeverity.MEDIUM,
        expected_amount=Money(100000),
        actual_amount=Money(98000),
        difference=Money(2000),
        description="Settlement amount differs from transaction amount.",
    )

    return InvestigationContext(
        exception=exception,
        transaction=transaction,
        settlement=settlement,
    )


class FakeResponses:
    def __init__(self) -> None:
        self.last_input: str | None = None

    def create(self, *, model: str, input: str) -> object:
        self.last_input = input

        return type(
            "FakeResponse",
            (),
            {
                "output_text": (
                    '{"root_cause":"fee_deduction",'
                    '"explanation":"Settlement is lower by 2000 paise, '
                    'consistent with a fee deduction.",'
                    '"evidence":["Transaction amount: 100000 paise",'
                    '"Settlement amount: 98000 paise",'
                    '"Difference: 2000 paise"],'
                    '"recommendation":"accept_settlement",'
                    '"confidence":0.91,'
                    '"requires_human_review":false}'
                )
            },
        )()


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_openai_provider_implements_investigation_contract() -> None:
    provider = OpenAIInvestigationProvider(
        client=FakeOpenAIClient(),
        model="test-model",
    )

    assert hasattr(provider, "investigate")


def test_openai_provider_returns_structured_investigation_result() -> None:
    context = build_context()
    provider = OpenAIInvestigationProvider(
        client=FakeOpenAIClient(),
        model="test-model",
    )

    result = provider.investigate(context)

    assert result.exception_id == "exc_0001"
    assert result.root_cause == RootCauseCategory.FEE_DEDUCTION
    assert result.recommendation == InvestigationRecommendation.ACCEPT_SETTLEMENT
    assert result.confidence == 0.91
    assert result.requires_human_review is False
    assert result.evidence == [
        "Transaction amount: 100000 paise",
        "Settlement amount: 98000 paise",
        "Difference: 2000 paise",
    ]


def test_openai_provider_prompt_contains_verified_financial_evidence() -> None:
    client = FakeOpenAIClient()
    provider = OpenAIInvestigationProvider(
        client=client,
        model="test-model",
    )

    provider.investigate(build_context())

    assert client.responses.last_input is not None
    assert "pay_0001" in client.responses.last_input
    assert "100000 paise" in client.responses.last_input
    assert "98000 paise" in client.responses.last_input
    assert "2000 paise" in client.responses.last_input
    assert "AMOUNT_MISMATCH" in client.responses.last_input