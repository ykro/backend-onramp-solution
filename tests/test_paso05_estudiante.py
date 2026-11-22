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
    """Verifica que cero días o días negativos nunca generen multa ni montos negativos."""
    # Arrange & Act
    fee_zero = paso05_pruebas.calculate_late_fee(0)
    fee_negative = paso05_pruebas.calculate_late_fee(-3)

    # Assert
    assert fee_zero == Decimal("0.00")
    assert fee_negative == Decimal("0.00")


def test_detects_bug_in_late_fee() -> None:
    """Verifica el cobro del primer día de atraso, donde la versión con un bug devuelve 0.00."""
    # Arrange
    days_late = 1

    # Act
    fee = paso05_pruebas.calculate_late_fee(days_late)

    # Assert
    assert fee == Decimal("2.50")
