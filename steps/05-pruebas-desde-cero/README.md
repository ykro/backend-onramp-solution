# Paso 5. Tests desde cero con `pytest`

![Paso 5. Tests desde cero con `pytest`](diagrams/ciclo-testing.svg)

Este paso toma unos 20 minutos.

## Antes de empezar

1. Si un test pasa siempre, pase lo que pase con el código, ¿qué te dice sobre el código?
2. ¿Qué casos borde se te ocurren para una multa por días de atraso?
3. ¿Qué diferencia hay entre probar a mano en `/docs` y tener un test automático?

## Por qué importa

En el curso escribirás tus propios tests y la nota toma en cuenta si detectan errores reales. Un buen test sigue el patrón Arrange, Act, Assert (preparar datos, ejecutar, comprobar) y cumple dos condiciones, pasa en verde con el código correcto y se pone en rojo cuando aparece un bug. Este paso usa [pytest](https://docs.pytest.org/en/stable/getting-started.html).

## Qué vas a hacer

- **Leer.** Lee [paso05_pruebas.py](../../paso05_pruebas.py). Trae `calculate_late_fee`, la versión correcta, y `calculate_late_fee_buggy`, una versión con un bug. Corre `uv run onramp inspect --paso 5` para comparar las dos con varios valores.
- **Debuguear.** Antes de escribir tests, descubre qué hace mal la versión con un bug. Busca un valor de entrada donde las dos funciones den resultados distintos.
- **Escribir.** Completa los tres tests de [tests/test_paso05_estudiante.py](../../tests/test_paso05_estudiante.py), un caso normal, un caso borde con días en cero o negativos, y un test que falle con la versión con un bug.

## Criterios de aceptación

- `CA-5.1` El archivo tiene al menos 3 funciones `test_*` y todas pasan contra `calculate_late_fee`.
- `CA-5.2` Cuando el verificador reemplaza `calculate_late_fee` por `calculate_late_fee_buggy`, al menos uno de tus tests falla.

## Al terminar

1. Escribe un test que pase con las dos versiones, la correcta y la que tiene el bug. ¿Por qué ese test no protege nada?
2. Si la tarifa diaria cambiara a `Decimal("3.00")`, ¿cuántos de tus tests tendrías que cambiar? ¿Cómo los escribirías para que dependan menos de ese número?
3. ¿Por qué el verificador corre tus tests contra la versión con un bug en lugar de solo revisar que pasen?
4. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

```bash
uv run onramp inspect --paso 5
uv run pytest tests/test_paso05_estudiante.py
uv run onramp check --paso 5
```

Si te trabas, abre la [pista 1](hints/1.md). Cada pista da un poco más que la anterior; la pista 3 trae un esqueleto, nunca la respuesta completa.

## Respuestas de autoevaluación

1. Por ejemplo, comprobar que el resultado es un `Decimal`. Pasa con las dos versiones porque no revisa el valor, así que nunca te avisaría del bug.
2. Si cada test repite `2.50` a mano, todos. Es mejor calcular el esperado a partir de la tarifa que pasas como argumento (`daily_rate`), o pasar la tarifa explícitamente en el test.
3. Porque un test que solo pasa no demuestra nada. Correrlo contra una versión con un bug comprueba que el test sí revisa la regla y se pone en rojo cuando alguien la rompe.
4. Respuesta personal. Debe mencionar Arrange, Act, Assert, el caso borde de días menores o iguales a cero y el valor donde la versión con un bug falla.
