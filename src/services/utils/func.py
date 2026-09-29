from decimal import Decimal, ROUND_HALF_UP

def to_cents(amount: Decimal) -> int:
    return int(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)

def to_decimal(amount:int) -> Decimal:
    return (Decimal(amount) / 100).quantize(Decimal("0.01"))