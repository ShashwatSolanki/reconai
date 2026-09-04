import pytest

from app.domain.money import Money


def test_money_stores_amount_in_minor_units() -> None:
    money = Money(123456)

    assert money.amount == 123456
    assert money.currency == "INR"


def test_money_normalizes_currency_to_uppercase() -> None:
    money = Money(1000, "inr")

    assert money.currency == "INR"


def test_money_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        Money(-1)


def test_money_rejects_invalid_currency() -> None:
    with pytest.raises(ValueError, match="3-letter"):
        Money(100, "IN")


def test_money_addition() -> None:
    first = Money(10000)
    second = Money(2500)

    result = first.add(second)

    assert result == Money(12500)


def test_money_subtraction() -> None:
    first = Money(10000)
    second = Money(2500)

    result = first.subtract(second)

    assert result == Money(7500)


def test_money_rejects_negative_result_from_subtraction() -> None:
    first = Money(1000)
    second = Money(1500)

    with pytest.raises(ValueError, match="negative amount"):
        first.subtract(second)


def test_money_rejects_currency_mismatch() -> None:
    inr = Money(1000, "INR")
    usd = Money(1000, "USD")

    with pytest.raises(ValueError, match="Currency mismatch"):
        inr.add(usd)


def test_money_is_immutable() -> None:
    money = Money(1000)

    with pytest.raises(AttributeError):
        money.amount = 2000
