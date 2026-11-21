# Paso 5. Pruebas automatizadas desde cero con `pytest`

![Ciclo de pruebas automatizadas Arrange, Act, Assert](diagrams/ciclo-testing.svg)

## Por qué importa

Durante el curso principal escribirás tus propias pruebas para verificar cada regla de negocio y cada ruta HTTP, siguiendo las guías oficiales de [pytest](https://docs.pytest.org/en/stable/) y [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/). Una prueba útil sigue el patrón **Arrange -> Act -> Assert**: prepara los datos de entrada, ejecuta la función bajo prueba y comprueba el resultado esperado. Además, una prueba solo te protege si pasa en verde ante código sano y falla en rojo cuando aparece un bug.

## Qué se construye

El módulo [paso05_pruebas.py](../../paso05_pruebas.py) ya está completo y expone dos funciones: `calculate_late_fee` (versión sana) y `calculate_late_fee_buggy` (versión con bug plantado que resta un día y permite multas negativas). Tu trabajo consiste en completar 3 pruebas en [tests/test_paso05_estudiante.py](../../tests/test_paso05_estudiante.py) (~10 minutos):

- **Caso normal (`test_normal_late_fee`):** verifica que para varios días de atraso (por ejemplo, 4 días a tarifa `Decimal("2.50")`), `paso05_pruebas.calculate_late_fee` devuelva `Decimal("10.00")`.
- **Caso borde con `days_late <= 0` (`test_edge_case_zero_or_negative_days`):** verifica que `0` días y días negativos (por ejemplo, `-3`) devuelvan `Decimal("0.00")`.
- **Detección del bug (`test_detects_bug_in_late_fee`):** verifica una regla exacta sobre `paso05_pruebas.calculate_late_fee` que la versión `calculate_late_fee_buggy` incumple.

## Criterios de aceptación

- `CA-5.1` `tests/test_paso05_estudiante.py` define al menos 3 funciones `test_*` y todas pasan en verde (código de salida `0`) contra `paso05_pruebas.calculate_late_fee`.
- `CA-5.2` Cuando el verificador reemplaza `paso05_pruebas.calculate_late_fee` por `paso05_pruebas.calculate_late_fee_buggy`, al menos una de tus pruebas falla en rojo (código de salida `1`).

## Cómo verificar

Compara la salida de ambas funciones en consola, corre tus pruebas directo con `pytest` y luego ejecuta el verificador del Paso 5:

```bash
uv run onramp inspect --paso 5
uv run pytest tests/test_paso05_estudiante.py
uv run onramp check --paso 5
```
