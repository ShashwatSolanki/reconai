from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary value represented in the smallest currency unit."""

    amount: int
    currency: str = "INR"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative.")

        if len(self.currency) != 3 or not self.currency.isalpha():
            raise ValueError("Currency must be a 3-letter alphabetic code.")

        object.__setattr__(self, "currency", self.currency.upper())

    def add(self, other: Money) -> Money:
        self._validate_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: Money) -> Money:
        self._validate_currency(other)

        if other.amount > self.amount:
            raise ValueError("Money subtraction cannot result in a negative amount.")

        return Money(self.amount - other.amount, self.currency)

    def _validate_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: {self.currency} != {other.currency}"
            )
