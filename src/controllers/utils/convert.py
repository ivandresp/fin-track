from decimal import Decimal

def decimal_from_str(amount:str) -> Decimal:
    return Decimal(amount.strip().replace(",", ""))