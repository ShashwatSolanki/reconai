from sqlalchemy.orm import Session

from app.db.models import TransactionModel
from app.domain.transaction import Transaction


class SqlAlchemyTransactionRepository:
    """SQLAlchemy-backed repository for payment transactions."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, transaction: Transaction) -> None:
        existing = self._session.get(TransactionModel, transaction.transaction_id)

        if existing is not None:
            raise ValueError(f"Transaction already exists: {transaction.transaction_id}")

        self._session.add(TransactionModel.from_domain(transaction))
        self._session.commit()

    def get(self, transaction_id: str) -> Transaction | None:
        model = self._session.get(TransactionModel, transaction_id)

        if model is None:
            return None

        return model.to_domain()

    def get_by_merchant(self, merchant_id: str) -> list[Transaction]:
        models = (
            self._session.query(TransactionModel)
            .filter(TransactionModel.merchant_id == merchant_id)
            .all()
        )

        return [model.to_domain() for model in models]