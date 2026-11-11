from decimal import Decimal, ROUND_HALF_UP


TASA_SERVICIO = Decimal("0.10")
TASA_IVA = Decimal("0.19")


def calcular_desglose(subtotal):
    subtotal_neto = (subtotal / (Decimal("1") + TASA_IVA)).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )
    iva = subtotal - subtotal_neto
    recargo_servicio = (subtotal * TASA_SERVICIO).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )
    return {
        "subtotal": subtotal,
        "subtotal_neto": subtotal_neto,
        "recargo_servicio": recargo_servicio,
        "iva": iva,
        "total": subtotal + recargo_servicio,
    }
