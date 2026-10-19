from repositories.debt.DebtRepository import DebtRepository
from repositories.debt.DebtIncreaseRepository import DebtIncreaseRepository
from models.debt.Debt import Debt, DebtDirection, Date
from models.debt.DebtIncrease import DebtIncrease
from models.payment.Payment import Payment, PaymentMethod
from services.utils.Balance import Balance, Decimal
from services.utils.func import to_cents

DIRECTIONS = ("PROPIA", "AJENA")
PAYMENT_METHODS = ("EFECTIVO", "TRANSFERENCIA", "TARJETA")

class DebtService:
    def __init__(
        self,
        repo: DebtRepository,
        increase_repo: DebtIncreaseRepository | None = None,
    ):
        self.repo = repo
        self.increase_repo = increase_repo or repo.debt_increase_repository

    def save(
        self,
        transaction_id: int,
        involved_person_id: int,
        direction: str,
        max_repayment_date: str | None = None,
    ) -> int:
        if direction not in DIRECTIONS:
            raise ValueError("Direccion invalida. Solo propia o ajena.")

        debt = Debt(
            transaction_id=transaction_id,
            involved_person_id=involved_person_id,
            direction=DebtDirection(direction),
            max_repayment_date=Date.fromisoformat(max_repayment_date) if max_repayment_date is not None else None,
        )

        return self.repo.save(debt)

    def increase_amount(
        self, debt_id: int, amount: Decimal, description: str | None = None
    ) -> Balance:
        """Aumenta el capital de una deuda pendiente y guarda el historial."""
        amount_cents = to_cents(amount)
        if amount_cents <= 0:
            raise ValueError("El monto del aumento debe ser mayor a cero.")

        debt = self.repo.get(debt_id)
        if debt is None:
            raise ValueError(f"No existe la deuda {debt_id}.")

        if bool(debt["settled"]):
            raise ValueError("No se puede aumentar una deuda que ya está saldada.")

        increase = DebtIncrease(
            debt_id=debt_id,
            amount=amount_cents,
            description=(description or "").strip() or None,
        )
        row = self.repo.increase_amount(increase)
        return Balance.from_row(row)

    def find_increases(self, debt_id: int) -> list[DebtIncrease]:
        if self.repo.get(debt_id) is None:
            raise ValueError(f"No existe la deuda {debt_id}.")

        return [
            DebtIncrease.from_row(row)
            for row in self.increase_repo.get_by_debt(debt_id)
        ]

    def find(self, debt_id:int) -> Debt:
        return Debt.from_row(self.repo.get(debt_id))

    def find_all(self):
        return [Debt.from_row(d) for d in self.repo.get_all()]

    def find_by_person(self, person_id:int):
        return [Debt.from_row(d) for d in self.repo.get_by_person(person_id)]

    def find_by_settled(self, is_settled:bool):
        return [Debt.from_row(d) for d in self.repo.get_by_settlement_status(is_settled)]

    def find_debt_balance(self, debt_id:int) -> Balance:
        return Balance.from_row(self.repo.get_debt_total(debt_id=debt_id, conn=None))

    # Retorna el id del pago y si la deuda fue saldada
    def add_payment_to_debt(self, debt_id:int, amount:Decimal, method:str, date:str | None) -> tuple[int, bool]:

        if amount <= 0:
            raise ValueError("El monto debe ser mayor a cero.")

        if method not in PAYMENT_METHODS:
            raise ValueError("Metodo de pago invalido")

        payment = Payment(debt_id=debt_id, amount=to_cents(amount), method=PaymentMethod(method), 
                    date=date or Date.today().isoformat())
        
        return self.repo.register_payment_and_validate(payment)

    def find_by_direction(self, direction:str):
        if direction not in DIRECTIONS:
            raise ValueError("Solo se pueden ver deudas propias o ajenas.")

        return [Debt.from_row(d) for d in self.repo.get_by_direction(DebtDirection(direction))]
