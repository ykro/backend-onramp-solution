"""Versiones con un bug de `calculate_late_fee` que usa el verificador del Paso 5.

El verificador pone cada una en lugar de la función correcta y corre tus tests. Si tus
tests siguen en verde con alguna, no la detectan. No las importes en tus tests; compáralas
con la correcta usando `uv run onramp inspect --paso 5`.
"""

from decimal import Decimal


def version_a(days_late: int, daily_rate: Decimal = Decimal("2.50")) -> Decimal:
    return (Decimal(days_late) * daily_rate).quantize(Decimal("0.01"))


def version_b(days_late: int, daily_rate: Decimal = Decimal("2.50")) -> Decimal:
    if days_late <= 0:
        return Decimal("0.00")
    return (Decimal(days_late - 1) * daily_rate).quantize(Decimal("0.01"))


VERSIONES = {"version_a": version_a, "version_b": version_b}
