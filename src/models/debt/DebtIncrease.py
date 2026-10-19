from dataclasses import dataclass
from datetime import datetime


@dataclass
class DebtIncrease:
    debt_id: int
    amount: int
    description: str | None = None
    id: int | None = None
    increased_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "debt_id": self.debt_id,
            "amount": self.amount,
            "description": self.description,
            "increased_at": self.increased_at.isoformat() if self.increased_at else None,
        }

    @classmethod
    def from_row(cls, row) -> "DebtIncrease":
        increased_at = row["increased_at"]
        return cls(
            id=row["id"],
            debt_id=row["debt_id"],
            amount=row["amount"],
            description=row["description"],
            increased_at=datetime.fromisoformat(increased_at) if increased_at else None,
        )
