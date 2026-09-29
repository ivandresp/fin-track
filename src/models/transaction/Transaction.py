from dataclasses import dataclass
from datetime import datetime, date as Date
from models.transaction.TransactionType import TransactionType

@dataclass
class Transaction:
    id: int | None
    type: TransactionType
    amount: int
    description: str
    date: Date
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def from_row(row: tuple) -> "Transaction":
        return Transaction(
            id=row[0],
            type=TransactionType(row[1]),
            amount=row[2],
            description=row[3],
            date=Date.fromisoformat(row[4]),
            created_at=datetime.fromisoformat(row[5]),
        )