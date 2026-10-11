from dataclasses import dataclass
from datetime import date as Date, datetime
from models.debt.DebtDirection import DebtDirection

@dataclass
class Debt:
    transaction_id: int
    involved_person_id: int
    direction: DebtDirection
    max_repayment_date: Date | None
    id: int | None = None
    settled: bool = False
    settled_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "involved_person_id": self.involved_person_id,
            "direction": self.direction.value,
            "max_repayment_date": self.max_repayment_date.isoformat() if self.max_repayment_date else None,
            "settled": self.settled,
            "settled_at": self.settled_at.isoformat() if self.settled_at else None,
        }

    @classmethod
    def from_row(cls, row) -> "Debt":
        return cls(
            id=row["id"],
            transaction_id=row["transaction_id"],
            involved_person_id=row["involved_person_id"],
            direction=DebtDirection(row["direction"]),
            max_repayment_date=row["max_repayment_date"],
            settled=bool(row["settled"]),
            settled_at=row["settled_at"],
        )
