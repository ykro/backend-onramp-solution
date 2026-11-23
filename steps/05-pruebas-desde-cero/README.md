# Paso 5. Tests desde cero con `pytest`

![Paso 5. Tests desde cero con `pytest`](diagrams/ciclo-testing.svg)

Este paso toma unos 30 minutos.

## Antes de empezar

1. Si un test pasa siempre, pase lo que pase con el código, ¿qué te dice sobre el código?
2. Una biblioteca cobra Q2.50 por cada día de atraso. ¿Qué valores de días probarías para convencerte de que el cálculo está bien? Escribe al menos cuatro antes de seguir.
3. ¿Qué diferencia hay entre probar a mano en `/docs` y tener un test automático?

## Por qué importa

En el curso tus tests tienen que detectar errores reales. Un buen test sigue el patrón Arrange, Act, Assert (preparar datos, ejecutar, comprobar) y cumple dos condiciones, pasa en verde con el código correcto y se pone en rojo cuando aparece un bug. Un solo caso casi nunca basta, porque cada bug se esconde en un lugar distinto. Este paso usa [pytest](https://docs.pytest.org/en/stable/getting-started.html).

## Lo mínimo que necesitas saber

- **Funciones `def test_*`.** `pytest` descubre y ejecuta automáticamente cualquier función cuyo nombre empieza con `test_` dentro de un archivo `test_*.py`.
- **`assert`.** Cada test comprueba el resultado esperado con `assert resultado == esperado`. Si la expresión es falsa, el test falla y muestra ambos valores.
- **`Decimal` exacto.** `calculate_late_fee` devuelve un `Decimal` con dos decimales (por ejemplo `Decimal("0.00")` o `Decimal("10.00")`), así que tus `assert` deben comparar contra `Decimal(...)`.

## Qué vas a hacer

- **Leer.** Lee `calculate_late_fee` en [paso05_pruebas.py](../../paso05_pruebas.py). El verificador guarda dos versiones con un bug, la A y la B. Corre `uv run onramp inspect --paso 5` para ver una tabla con la correcta y las dos versiones lado a lado.
- **Debuguear.** Antes de escribir tests, describe con tus palabras qué hace mal cada versión. Para cada una, anota un valor de días donde da un resultado distinto de la correcta. Compara esa lista con los cuatro valores que escribiste al inicio: ¿alguno de tus valores habría detectado los dos bugs?
- **Escribir.** Completa los tres tests de [tests/test_paso05_estudiante.py](../../tests/test_paso05_estudiante.py): un caso normal, un edge case sin atraso (cero y días negativos, entrega anticipada) y un tercer caso que tú elijas. Juntos tienen que detectar las dos versiones.

## Criterios de aceptación

- `CA-5.1` El archivo tiene al menos 3 funciones `test_*` y todas pasan contra `calculate_late_fee`. Cada test llama a `calculate_late_fee` y comprueba el resultado con un `assert`.
- `CA-5.2` Cuando el verificador pone la versión A en lugar de `calculate_late_fee`, al menos uno de tus tests falla.
- `CA-5.3` Lo mismo con la versión B.

## Al terminar

1. Escribe un test que pase con la correcta y con las dos versiones con un bug. ¿Por qué ese test no protege nada?
2. Si la tarifa diaria cambiara a `Decimal("3.00")`, ¿cuántos de tus tests tendrías que cambiar? ¿Cómo los escribirías para que dependan menos de ese número?
3. Mañana alguien escribe una versión C que cobra el doble a partir del día 10. ¿Tus tests la detectarían? ¿Qué caso agregarías y por qué nunca puedes probar todos los valores?
4. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

```bash
uv run onramp inspect --paso 5
uv run pytest tests/test_paso05_estudiante.py
uv run onramp check --paso 5
```

Si te trabas, abre la [pista 1](hints/1.md). Cada pista da un poco más que la anterior; la pista 3 trae un esqueleto, nunca la respuesta completa.

## Respuestas de autoevaluación («Al terminar»)

1. Por ejemplo, comprobar que el resultado es un `Decimal`, o probar solo con `0` días. Pasa con las tres funciones porque no revisa un valor donde difieren, así que nunca te avisaría de un bug.
2. Si cada test repite `2.50` a mano, todos. Es mejor pasar la tarifa explícitamente en el test (`daily_rate=Decimal("3.00")`) y calcular el esperado a partir de ella.
3. Solo si alguno de tus tests usa 10 días o más. Habría que agregar un caso en ese límite, por ejemplo 9, 10 y 11 días. Los valores posibles son infinitos, así que eliges los que están cerca de cada regla: el cero, los negativos, el primer día y cada cambio de tarifa.
4. Respuesta personal. Debe mencionar Arrange, Act, Assert, por qué el `0` no basta para la versión A y qué caso normal detecta la B.
