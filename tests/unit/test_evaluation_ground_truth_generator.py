from app.domain.evaluation import GroundTruthStatus
from app.services.evaluation_ground_truth_generator import (
    EvaluationGroundTruthGenerator,
)
from app.services.synthetic_data_generator import SyntheticDataGenerator


def test_generator_produces_ground_truth_for_each_transaction() -> None:
    synthetic_generator = SyntheticDataGenerator(seed=42, record_count=100)
    transactions, settlements = synthetic_generator.generate()

    generator = EvaluationGroundTruthGenerator()

    ground_truth = generator.generate(transactions, settlements)

    assert len(ground_truth) == 100


def test_ground_truth_contains_expected_injected_scenarios() -> None:
    synthetic_generator = SyntheticDataGenerator(seed=42, record_count=100)
    transactions, settlements = synthetic_generator.generate()

    generator = EvaluationGroundTruthGenerator()

    ground_truth = generator.generate(transactions, settlements)

    statuses = {
        item.transaction_id: item.expected_status
        for item in ground_truth
    }

    assert statuses["pay_0001"] == GroundTruthStatus.MATCHED
    assert statuses["pay_0002"] == GroundTruthStatus.PARTIAL_MATCH
    assert statuses["pay_0003"] == GroundTruthStatus.MISMATCH
    assert statuses["pay_0004"] == GroundTruthStatus.MISSING_SETTLEMENT
    assert statuses["pay_0005"] == GroundTruthStatus.DUPLICATE