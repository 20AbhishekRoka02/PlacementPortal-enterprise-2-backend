from decimal import Decimal, ROUND_HALF_UP

def file_size_in_kbs(size):
    return (
        Decimal(size) / Decimal(1024)
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
