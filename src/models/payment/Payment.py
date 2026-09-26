from dataclasses import dataclass
from PaymentMethod import PaymentMethod
from datetime import datetime, date as Date

@dataclass
class Payment:
    id: int | None
    debt_id: int
    amount: int
    method: PaymentMethod
    date: Date
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "debt_id": self.debt_id,
            "amount": self.amount,
            "method": self.method.value,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def from_row(row: tuple) -> "Payment":
        return Payment(
            id=row[0],
            debt_id=row[1],
            amount=row[2],
            method=PaymentMethod(row[3]),
            date=Date.fromisoformat(row[4]),
            created_at=datetime.fromisoformat(row[5]),
        )