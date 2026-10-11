from repositories.transaction.TransactionRepository import TransactionRepository
from models.transaction.Transaction import Transaction, TransactionType
from services.utils.func import Decimal, to_cents

TYPES = ("GASTO", "INGRESO", "DEUDA")

class TransactionService:
    def __init__(self, repo: TransactionRepository):
        self.repo = repo

    def save(self, type: str, amount: Decimal, description: str) -> int:
        if type not in TYPES:
            raise ValueError("Tipo no permitido.")

        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0.")

        if not description or not description.strip():
            raise ValueError("Descripcion Obligatoria.")

        trans = Transaction(
            type=TransactionType(type), amount=to_cents(amount), description=description
        )
        return self.repo.save(trans)

    def find(self, transaction_id: int) -> Transaction:
        return Transaction.from_row(self.repo.get(transaction_id))

    def find_all(self) -> list[Transaction]:
        return [Transaction.from_row(t) for t in self.repo.get_all()]

    def find_by_type(self, type: str):
        if type not in TYPES:
            raise ValueError("Tipo no permitido.")

        return [Transaction.from_row(t) for t in self.repo.get_by_type(type)]
