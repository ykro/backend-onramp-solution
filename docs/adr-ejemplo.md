# Cómo leer un ADR (`ARCHITECTURE_DECISIONS.md`)

En el curso principal encontrarás un archivo `ARCHITECTURE_DECISIONS.md` compuesto por registros cortos llamados **ADR** (*Architecture Decision Records*), según la convención de [adr.github.io](https://adr.github.io/). Un ADR explica por qué el equipo eligió una opción técnica y qué descartó en ese momento.

## Ejemplo: ADR-001 — Usar `Decimal` para precios y multas

- **Contexto:** La API de biblioteca calcula precios de libros y multas por atraso. Con `float` binario aparecen errores de redondeo como `0.1 + 0.2 != 0.3`.
- **Decisión:** Representar todo monto monetario con `decimal.Decimal` en modelos Pydantic y funciones de dominio, limitando la entrada a dos decimales.
- **Alternativas descartadas:** Usar `float` con `round()` en cada vista (fácil de olvidar y propenso a diferencias entre capas) o guardar texto sin validar (pierde controles aritméticos).
- **Consecuencias:** Evita errores de centavos en reportes y pruebas. A cambio, los clientes deben enviar montos como cadenas decimales exactas (por ejemplo `"125.50"`) y el equipo debe evitar mezclar `float` con `Decimal`.
