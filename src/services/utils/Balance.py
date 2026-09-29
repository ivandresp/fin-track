from utils.func import Decimal, to_decimal
from dataclasses import dataclass

@dataclass
class Balance:
    def __init__(self, total_amount:Decimal, total_paid: Decimal, remaining_amount:Decimal):
        self.total_amount = total_amount
        self.total_paid = total_paid
        self.remaining_amount = remaining_amount

    @staticmethod
    def from_row(row:tuple) -> "Balance":
        return Balance(
            total_amount=to_decimal(row[0]),
            total_paid=to_decimal(row[1]),
            remaining_amount=to_decimal(row[2]),
        )