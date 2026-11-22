"""Paso 5: tests desde cero con `pytest`.

`calculate_late_fee` calcula la multa por entregar tarde un libro y es la versión correcta.
No necesitas editar este archivo. El verificador guarda dos versiones con un bug y corre tus
tests contra cada una: tus tests deben pasar con esta función y fallar con las dos versiones.

Escribe tus tests en `tests/test_paso05_estudiante.py`, compara las versiones con
`uv run onramp inspect --paso 5` y verifica con `uv run onramp check --paso 5`.
"""

from decimal import Decimal


def calculate_late_fee(days_late: int, daily_rate: Decimal = Decimal("2.50")) -> Decimal:
    """Devuelve la multa exacta por los días de atraso. Sin atraso, la multa es 0.00."""
    if days_late <= 0:
        return Decimal("0.00")
    return (Decimal(days_late) * daily_rate).quantize(Decimal("0.01"))
