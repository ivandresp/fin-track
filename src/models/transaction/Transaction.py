from dataclasses import dataclass
from datetime import datetime, date as Date
from models.transaction.TransactionType import TransactionType

@dataclass
class Transaction:
    type: TransactionType
    amount: int
    description: str
    id: int | None = None
    date: Date | None = None
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Transaction":
        return cls(
            id=row["id"],
            type=TransactionType(row["type"]),
            amount=row["amount"],
            description=row["description"],
            date=Date.fromisoformat(row["date"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )