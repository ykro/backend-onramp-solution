"""Solución de referencia del Paso 5: tres pruebas con Arrange -> Act -> Assert."""

from decimal import Decimal

import paso05_pruebas


def test_normal_late_fee() -> None:
    """Verifica el cálculo normal de multa para cuatro días de atraso."""
    # Arrange
    days_late = 4
    daily_rate = Decimal("2.50")

    # Act
    fee = paso05_pruebas.calculate_late_fee(days_late, daily_rate)

    # Assert
    assert fee == Decimal("10.00")


def test_edge_case_zero_or_negative_days() -> None:
    """Cero días y días negativos no generan multa. La versión A cobra un monto negativo con -3."""
    # Arrange & Act
    fee_zero = paso05_pruebas.calculate_late_fee(0)
    fee_negative = paso05_pruebas.calculate_late_fee(-3)

    # Assert
    assert fee_zero == Decimal("0.00")
    assert fee_negative == Decimal("0.00")


def test_detects_bug_in_late_fee() -> None:
    """El primer día de atraso ya cobra. La versión B devuelve 0.00 aquí."""
    # Arrange
    days_late = 1

    # Act
    fee = paso05_pruebas.calculate_late_fee(days_late)

    # Assert
    assert fee == Decimal("2.50")
