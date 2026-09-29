from repositories.payment.PaymentRepository import PaymentRepository
from models.payment.Payment import Payment, PaymentMethod

PAYMENT_METHODS = ("EFECTIVO", "TRANSFERENCIA", "TARJETA")

class PaymentService:
    def __init__(self, repo:PaymentRepository):
        self.repo = repo

    def find(self, payment_id:int) -> Payment:
        return Payment.from_row(self.repo.get(payment_id))

    def find_all(self):
        return [Payment.from_row(p) for p in self.repo.get_all()]

    def find_by_method(self, method:str):
        if method not in PAYMENT_METHODS:
            raise ValueError("Metodo de pago invalido.")

        return [Payment.from_row(p) for p in self.repo.get_all_by_method(PaymentMethod(method))]

    def find_by_debt(self, debt_id:int):
        return [Payment.from_row(p) for p in self.repo.get_by_debt(debt_id)]