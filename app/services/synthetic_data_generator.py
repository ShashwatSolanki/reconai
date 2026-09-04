from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus


class SyntheticDataGenerator:
    """Generate deterministic synthetic transactions and settlements."""

    def __init__(self, seed: int = 42, record_count: int = 100) -> None:
        if record_count < 50:
            raise ValueError("record_count must be at least 50.")

        self._random = random.Random(seed)
        self._record_count = record_count

    def generate(self) -> tuple[list[Transaction], list[Settlement]]:
        """Generate transactions and settlements with controlled discrepancies."""

        transactions: list[Transaction] = []
        settlements: list[Settlement] = []

        base_time = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)

        for index in range(self._record_count):
            transaction_id = f"pay_{index + 1:04d}"
            amount = self._random.choice(
                [5000, 10000, 25000, 50000, 75000, 100000, 250000, 500000]
            )

            transaction = Transaction(
                transaction_id=transaction_id,
                merchant_id=f"merchant_{(index % 5) + 1:03d}",
                amount=Money(amount),
                transaction_time=base_time + timedelta(minutes=index),
                payment_method=self._random.choice(list(PaymentMethod)),
                reference_id=f"ref_{index + 1:04d}",
                status=TransactionStatus.SUCCESS,
            )

            transactions.append(transaction)

            # Keep the first five records deterministic examples of
            # different reconciliation scenarios.
            if index == 0:
                # Exact match.
                settlements.append(
                    self._build_settlement(transaction, transaction.amount)
                )

            elif index == 1:
                # Partial settlement: settlement is lower than transaction.
                settlements.append(
                    self._build_settlement(
                        transaction,
                        Money(transaction.amount.amount - 2000),
                    )
                )

            elif index == 2:
                # Amount mismatch: settlement is higher than transaction.
                settlements.append(
                    self._build_settlement(
                        transaction,
                        Money(transaction.amount.amount + 2000),
                    )
                )

            elif index == 3:
                # Missing settlement: deliberately create no settlement.
                continue

            elif index == 4:
                # Duplicate settlement: create two records for one transaction.
                settlements.append(
                    self._build_settlement(
                        transaction,
                        transaction.amount,
                        settlement_suffix="a",
                    )
                )
                settlements.append(
                    self._build_settlement(
                        transaction,
                        transaction.amount,
                        settlement_suffix="b",
                    )
                )

            else:
                # Remaining records are exact matches.
                settlements.append(
                    self._build_settlement(transaction, transaction.amount)
                )

        return transactions, settlements

    def _build_settlement(
        self,
        transaction: Transaction,
        amount: Money,
        settlement_suffix: str = "",
    ) -> Settlement:
        """Build a settlement record for a transaction."""

        settlement_id = f"set_{transaction.transaction_id.removeprefix('pay_')}"
        if settlement_suffix:
            settlement_id = f"{settlement_id}_{settlement_suffix}"

        index = int(transaction.transaction_id.removeprefix("pay_"))

        return Settlement(
            settlement_id=settlement_id,
            merchant_id=transaction.merchant_id,
            amount=amount,
            settlement_time=transaction.transaction_time + timedelta(days=1),
            reference_id=f"settle_ref_{index:04d}{settlement_suffix}",
            transaction_reference=transaction.transaction_id,
            status=SettlementStatus.SETTLED,
        )