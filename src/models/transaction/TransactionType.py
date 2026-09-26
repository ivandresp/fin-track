from enum import Enum

class TransactionType(str, Enum):
    GASTO = "GASTO"
    INGRESO = "INGRESO"
    DEUDA = "DEUDA"