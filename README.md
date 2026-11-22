# Biblioteca — Backend On-Ramp (solución de referencia)

Este repositorio contiene la solución verificada de [Backend On-Ramp](https://github.com/ykro/backend-onramp), la nivelación previa al [Curso 1 de Backend con FastAPI](https://github.com/ykro/backend-course). Las 21 pruebas de [tests/test_onramp.py](tests/test_onramp.py) pasan aquí, juntas o por paso con `--paso 0` hasta `--paso 5`. Cada guía en `steps/` termina con las respuestas de autoevaluación.

![Mapa de Backend On-Ramp](docs/diagrams/overview.svg)

## Dónde ver la solución de cada paso

| Paso | Criterios | Qué se cambió y por qué | Archivo |
| --- | --- | --- | --- |
| Paso 0 | `CA-0.1` a `CA-0.3` | Se agregaron `GET /saludo/{nombre}` y `GET /libros`. La parte de la ruta entre llaves llega como parámetro de la función y FastAPI convierte el `return` en JSON con `200`. | [paso00_hola.py](paso00_hola.py) |
| Paso 1 | `CA-1.1` a `CA-1.5` | `201` y `204` van en el decorador porque son el resultado normal de crear y borrar; el `404` sale de `HTTPException` porque es un error. El catálogo vive dentro de `create_app()` para que cada app (y cada test) empiece vacía. `extra="forbid"`, `Field` y `Decimal` hacen que Pydantic rechace con `422` los datos inválidos antes de llegar a la función. | [paso01_http_y_pydantic.py](paso01_http_y_pydantic.py) |
| Paso 2 | `CA-2.1` a `CA-2.4` | `PRAGMA foreign_keys = ON` enciende la verificación que SQLite trae apagada. El `INNER JOIN` trae el nombre del autor en una sola consulta. La paginación pasa `limit`, `offset` y el filtro como parámetros `?`, así el texto del usuario nunca se interpreta como SQL. El índice cambia `SCAN` por `SEARCH`. | [paso02_sql_relacional.py](paso02_sql_relacional.py) |
| Paso 3 | `CA-3.1` a `CA-3.3` | `GET /rooms` recibe el repositorio con `Depends`, así los tests lo reemplazan con `dependency_overrides`. El bloque central del JWT se lee con Base64Url agregando el relleno `=`, porque solo está codificado. Un rol sin permiso recibe `403`, ya que la identidad sí se verificó. | [paso03_depends_y_jwt.py](paso03_depends_y_jwt.py) |
| Paso 4 | `CA-4.1`, `CA-4.2` | Un `threading.Lock` compartido envuelve la revisión y la escritura de `reserve`, que forman la sección crítica; si solo envolviera la escritura, dos hilos podrían pasar la revisión a la vez. | [paso04_concurrencia.py](paso04_concurrencia.py) |
| Paso 5 | `CA-5.1` a `CA-5.3` | Tres tests con Arrange, Act, Assert. El caso borde usa `0` y `-3`; solo el negativo detecta la versión A, que cobra montos negativos. El primer día de atraso detecta la versión B, que cobra un día menos y devuelve `0.00`. | [tests/test_paso05_estudiante.py](tests/test_paso05_estudiante.py) |

## Los 6 pasos

| Paso | Tiempo | Qué practicas | Archivo | Guía |
| --- | --- | --- | --- | --- |
| Paso 0 | 35 min | Instalar `uv`, levantar tu primer servidor y hablarle con el navegador, `/docs` y `curl` | [paso00_hola.py](paso00_hola.py) | [steps/00-entorno-y-primer-servidor](steps/00-entorno-y-primer-servidor/README.md) |
| Paso 1 | 40 min | Códigos HTTP (`201`, `204`, `404`, `422`), estado aislado y validación con Pydantic y `Decimal` | [paso01_http_y_pydantic.py](paso01_http_y_pydantic.py) | [steps/01-http-y-pydantic](steps/01-http-y-pydantic/README.md) |
| Paso 2 | 50 min | Tu primera base de datos, tablas, llaves foráneas, `JOIN`, paginación con parámetros e índices en SQLite | [paso02_sql_relacional.py](paso02_sql_relacional.py) | [steps/02-sql-relacional](steps/02-sql-relacional/README.md) |
| Paso 3 | 40 min | `Depends` y `dependency_overrides`, qué trae un JWT y la diferencia entre `401` y `403` | [paso03_depends_y_jwt.py](paso03_depends_y_jwt.py) | [steps/03-depends-y-jwt](steps/03-depends-y-jwt/README.md) |
| Paso 4 | 25 min | Requests simultáneos, race conditions y `threading.Lock` | [paso04_concurrencia.py](paso04_concurrencia.py) | [steps/04-concurrencia](steps/04-concurrencia/README.md) |
| Paso 5 | 30 min | Tests desde cero con `pytest` que se ponen en rojo ante dos versiones con un bug | [tests/test_paso05_estudiante.py](tests/test_paso05_estudiante.py) | [steps/05-pruebas-desde-cero](steps/05-pruebas-desde-cero/README.md) |

## Verificación

1. `uv sync` (o `UV_CACHE_DIR=/tmp/uv-cache-onramp uv sync` si la caché global tiene permisos restringidos).
2. `uv run onramp inspect` o `uv run onramp inspect --paso N` para ver cada paso en vivo.
3. `uv run onramp check` o `uv run onramp check --paso N` para correr las pruebas.

## Repositorios relacionados

- Índice de on-ramps: [ykro/courses-onramp](https://github.com/ykro/courses-onramp)
- Repositorio con los ejercicios: [ykro/backend-onramp](https://github.com/ykro/backend-onramp)
- Curso principal: [ykro/backend-course](https://github.com/ykro/backend-course)
