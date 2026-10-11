from dataclasses import dataclass
from models.payment.PaymentMethod import PaymentMethod
from datetime import datetime, date as Date

@dataclass
class Payment:
    debt_id: int
    amount: int
    method: PaymentMethod
    date: Date | None = None
    id: int | None = None
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "debt_id": self.debt_id,
            "amount": self.amount,
            "method": self.method.value,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_row(cls, row) -> "Payment":
        return cls(
            id=row["id"],
            debt_id=row["debt_id"],
            amount=row["amount"],
            method=PaymentMethod(row["method"]),
            date=row["date"],
            created_at=row["created_at"],
        )
