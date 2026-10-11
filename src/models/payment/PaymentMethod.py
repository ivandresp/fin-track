from enum import Enum

class PaymentMethod(str, Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    TARJETA = "TARJETA"