"""Paso 5 (~10 min): Pruebas automatizadas desde cero con `pytest`.

Este módulo expone dos versiones del cálculo de multa por entrega tardía de un libro:
- `calculate_late_fee`: implementación sana que cobra 0.00 si `days_late <= 0`.
- `calculate_late_fee_buggy`: implementación con bug plantado (resta un día y permite negativos).

No necesitas editar este archivo: escribe tus 3 pruebas en `tests/test_paso05_estudiante.py`
y verifícalas con `uv run onramp check --paso 5`.
"""

from decimal import Decimal


def calculate_late_fee(days_late: int, daily_rate: Decimal = Decimal("2.50")) -> Decimal:
    """Calcula la multa exacta en base 10 por días de atraso de un préstamo."""
    if days_late <= 0:
        return Decimal("0.00")
    return (Decimal(days_late) * daily_rate).quantize(Decimal("0.01"))


def calculate_late_fee_buggy(days_late: int, daily_rate: Decimal = Decimal("2.50")) -> Decimal:
    """Versión con bug plantado: resta un día de atraso y no protege `days_late <= 0`."""
    return (Decimal(days_late - 1) * daily_rate).quantize(Decimal("0.01"))
