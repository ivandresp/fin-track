from dataclasses import dataclass
from datetime import date as Date, datetime
from models.debt.DebtDirection import DebtDirection

@dataclass
class Debt:
    id: int | None
    transaction_id: int
    involved_person_id: int
    direction: DebtDirection
    max_repayment_date: Date | None
    settled: bool
    settled_at: datetime | None

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

    @staticmethod
    def from_row(row: tuple) -> "Debt":
        return Debt(
            id=row[0],
            transaction_id=row[1],
            involved_person_id=row[2],
            direction=DebtDirection(row[3]),
            max_repayment_date=Date.fromisoformat(row[4]) if row[4] else None,
            settled=row[5],
            settled_at=datetime.fromisoformat(row[6]) if row[6] else None,
        )