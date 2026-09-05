from __future__ import annotations

from app.domain.evaluation import GroundTruth, GroundTruthStatus
from app.domain.settlement import Settlement
from app.domain.transaction import Transaction


class EvaluationGroundTruthGenerator:
    """Generate known reconciliation outcomes for evaluation datasets."""

    def generate(
        self,
        transactions: list[Transaction],
        settlements: list[Settlement],
    ) -> list[GroundTruth]:
        """Generate independent ground truth from transaction/settlement records."""

        ground_truth: list[GroundTruth] = []

        for transaction in transactions:
            matching_settlements = [
                settlement
                for settlement in settlements
                if settlement.transaction_reference == transaction.transaction_id
            ]

            if not matching_settlements:
                status = GroundTruthStatus.MISSING_SETTLEMENT
            elif len(matching_settlements) > 1:
                status = GroundTruthStatus.DUPLICATE
            elif matching_settlements[0].amount.amount == transaction.amount.amount:
                status = GroundTruthStatus.MATCHED
            elif matching_settlements[0].amount.amount < transaction.amount.amount:
                status = GroundTruthStatus.PARTIAL_MATCH
            else:
                status = GroundTruthStatus.MISMATCH

            ground_truth.append(
                GroundTruth(
                    transaction_id=transaction.transaction_id,
                    expected_status=status,
                    has_exception=status != GroundTruthStatus.MATCHED,
                )
            )

        return ground_truth