from sqlalchemy.orm import Session

from app.db.models import SettlementModel
from app.domain.settlement import Settlement


class SqlAlchemySettlementRepository:
    """SQLAlchemy-backed repository for settlement records."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, settlement: Settlement) -> None:
        existing = self._session.get(SettlementModel, settlement.settlement_id)

        if existing is not None:
            raise ValueError(f"Settlement already exists: {settlement.settlement_id}")

        self._session.add(SettlementModel.from_domain(settlement))
        self._session.commit()

    def get(self, settlement_id: str) -> Settlement | None:
        model = self._session.get(SettlementModel, settlement_id)

        if model is None:
            return None

        return model.to_domain()

    def get_by_merchant(self, merchant_id: str) -> list[Settlement]:
        models = (
            self._session.query(SettlementModel)
            .filter(SettlementModel.merchant_id == merchant_id)
            .all()
        )

        return [model.to_domain() for model in models]