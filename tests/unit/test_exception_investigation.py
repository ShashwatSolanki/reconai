from app.domain.exception import ExceptionCategory, ExceptionSeverity, FinancialException
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    InvestigationResult,
    RootCauseCategory,
)
from app.domain.money import Money


def build_exception() -> FinancialException:
    return FinancialException(
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


def test_investigation_result_captures_root_cause_and_recommendation() -> None:
    result = InvestigationResult(
        exception_id="exc_0001",
        root_cause=RootCauseCategory.FEE_DEDUCTION,
        explanation="The settlement is lower by 2000 paise, consistent with a fee deduction.",
        evidence=["Transaction amount: 100000 paise", "Settlement amount: 98000 paise"],
        recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
        confidence=0.95,
        requires_human_review=False,
    )

    assert result.exception_id == "exc_0001"
    assert result.root_cause == RootCauseCategory.FEE_DEDUCTION
    assert result.recommendation == InvestigationRecommendation.ACCEPT_SETTLEMENT
    assert result.confidence == 0.95
    assert result.requires_human_review is False


def test_investigation_result_rejects_invalid_confidence() -> None:
    try:
        InvestigationResult(
            exception_id="exc_0001",
            root_cause=RootCauseCategory.UNKNOWN,
            explanation="Unable to determine the cause.",
            evidence=["Insufficient settlement information."],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=1.1,
            requires_human_review=True,
        )
    except ValueError as error:
        assert "confidence" in str(error)
    else:
        raise AssertionError("Expected invalid confidence to raise ValueError.")


def test_investigation_result_requires_explanation() -> None:
    try:
        InvestigationResult(
            exception_id="exc_0001",
            root_cause=RootCauseCategory.UNKNOWN,
            explanation="",
            evidence=["Insufficient settlement information."],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.2,
            requires_human_review=True,
        )
    except ValueError as error:
        assert "explanation" in str(error)
    else:
        raise AssertionError("Expected empty explanation to raise ValueError.")


def test_investigation_result_requires_evidence() -> None:
    try:
        InvestigationResult(
            exception_id="exc_0001",
            root_cause=RootCauseCategory.UNKNOWN,
            explanation="Unable to determine the cause.",
            evidence=[],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.2,
            requires_human_review=True,
        )
    except ValueError as error:
        assert "evidence" in str(error)
    else:
        raise AssertionError("Expected empty evidence to raise ValueError.")


def test_investigation_result_requires_human_review_for_escalation() -> None:
    try:
        InvestigationResult(
            exception_id="exc_0001",
            root_cause=RootCauseCategory.UNKNOWN,
            explanation="Unable to determine the cause.",
            evidence=["Insufficient settlement information."],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.2,
            requires_human_review=False,
        )
    except ValueError as error:
        assert "human review" in str(error)
    else:
        raise AssertionError("Expected escalation to require human review.")