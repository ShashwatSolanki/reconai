from __future__ import annotations

from app.domain.settlement import Settlement


class SettlementRepository:
    """In-memory repository for settlement records."""

    def __init__(self) -> None:
        self._settlements: dict[str, Settlement] = {}

    def save(self, settlement: Settlement) -> None:
        """Store a settlement by its unique settlement ID."""
        if settlement.settlement_id in self._settlements:
            raise ValueError(
                f"Settlement already exists: {settlement.settlement_id}"
            )

        self._settlements[settlement.settlement_id] = settlement

    def get(self, settlement_id: str) -> Settlement | None:
        """Return a settlement by ID, or None when it does not exist."""
        return self._settlements.get(settlement_id)

    def get_by_merchant(self, merchant_id: str) -> list[Settlement]:
        """Return all settlements associated with a merchant."""
        return [
            settlement
            for settlement in self._settlements.values()
            if settlement.merchant_id == merchant_id
        ]
