from app.domain.settlement import Settlement
from app.domain.transaction import Transaction
from app.services.synthetic_data_generator import SyntheticDataGenerator


def test_generator_produces_at_least_50_transactions() -> None:
    generator = SyntheticDataGenerator(seed=42)

    transactions, settlements = generator.generate()

    assert len(transactions) >= 50
    assert len(settlements) >= 50


def test_generator_is_reproducible() -> None:
    first_generator = SyntheticDataGenerator(seed=42)
    second_generator = SyntheticDataGenerator(seed=42)

    first_transactions, first_settlements = first_generator.generate()
    second_transactions, second_settlements = second_generator.generate()

    assert first_transactions == second_transactions
    assert first_settlements == second_settlements


def test_generated_records_have_valid_domain_types() -> None:
    generator = SyntheticDataGenerator(seed=42)

    transactions, settlements = generator.generate()

    assert all(isinstance(transaction, Transaction) for transaction in transactions)
    assert all(isinstance(settlement, Settlement) for settlement in settlements)


def test_generator_injects_reconciliation_scenarios() -> None:
    generator = SyntheticDataGenerator(seed=42)

    transactions, settlements = generator.generate()

    settlements_by_transaction = {
        transaction.transaction_id: [
            settlement
            for settlement in settlements
            if settlement.transaction_reference == transaction.transaction_id
        ]
        for transaction in transactions
    }

    assert any(
        len(candidate_settlements) == 0
        for candidate_settlements in settlements_by_transaction.values()
    )

    assert any(
        len(candidate_settlements) > 1
        for candidate_settlements in settlements_by_transaction.values()
    )

    assert any(
        candidate_settlements
        and candidate_settlements[0].amount.amount
        < next(
            transaction.amount.amount
            for transaction in transactions
            if transaction.transaction_id == candidate_settlements[0].transaction_reference
        )
        for candidate_settlements in settlements_by_transaction.values()
    )

    assert any(
        candidate_settlements
        and candidate_settlements[0].amount.amount
        >
        next(
            transaction.amount.amount
            for transaction in transactions
            if transaction.transaction_id == candidate_settlements[0].transaction_reference
        )
        for candidate_settlements in settlements_by_transaction.values()
    )


def test_generator_preserves_transaction_settlement_relationships() -> None:
    generator = SyntheticDataGenerator(seed=42)

    transactions, settlements = generator.generate()

    transaction_ids = {transaction.transaction_id for transaction in transactions}

    assert all(
        settlement.transaction_reference in transaction_ids
        for settlement in settlements
    )