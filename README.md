# Biblioteca — Backend Onramp (Solución de referencia)

Este repositorio contiene la solución completa y verificada de [Backend Onramp](https://github.com/ykro/backend-onramp) para el [Curso 1 de Backend con FastAPI](https://github.com/ykro/backend-course). Las 15 pruebas de [tests/test_onramp.py](tests/test_onramp.py) pasan aquí sin Docker ni cuentas externas, tanto en conjunto como por separado con `--paso 1` hasta `--paso 5`.

![Mapa general de Backend Onramp](docs/diagrams/overview.svg)

## Los 5 pasos (independientes)

| Paso | Enfoque | Guía |
| --- | --- | --- |
| Paso 1 | Contratos HTTP/1.1 (`201`, `204`, `404`) y estado aislado por instancia | [steps/01-http-contratos/README.md](steps/01-http-contratos/README.md) |
| Paso 2 | Validación estricta con Pydantic (`extra="forbid"`, `Decimal` y `422`) | [steps/02-validacion-pydantic/README.md](steps/02-validacion-pydantic/README.md) |
| Paso 3 | SQLite relacional (`PRAGMA foreign_keys`, `INNER JOIN`, paginación e índice) | [steps/03-sql-relacional/README.md](steps/03-sql-relacional/README.md) |
| Paso 4 | `Depends`, `dependency_overrides`, JWT en Base64Url y `401` vs `403` | [steps/04-depends-y-jwt/README.md](steps/04-depends-y-jwt/README.md) |
| Paso 5 | Concurrencia y exclusión mutua con `threading.Lock` ante `Barrier(5)` | [steps/05-concurrencia/README.md](steps/05-concurrencia/README.md) |

## Dónde ver la solución de cada paso

Si vienes del [repositorio del problema](https://github.com/ykro/backend-onramp), esta tabla indica qué se trabajó, qué cambio exacto resuelve cada criterio y en qué archivo está la solución.

| Paso | Criterio | Qué se cambió y por qué | Archivo de solución |
| --- | --- | --- | --- |
| Paso 1 | `CA-1.1`, `CA-1.2`, `CA-1.3` | Se añadió `status_code=201` en `POST /books`, `HTTPException(404)` en `GET /books/{book_id}`, `Response(status_code=204)` sin cuerpo en `DELETE /books/{book_id}`, y se movieron `books` y `next_id` dentro de `create_app()` con `nonlocal next_id` para aislar cada instancia. | [paso01_http_contratos.py](paso01_http_contratos.py) |
| Paso 2 | `CA-2.1`, `CA-2.2`, `CA-2.3` | En `BookCreate` se agregó `model_config = ConfigDict(extra="forbid")`, `title` con `Field(min_length=1, max_length=120)` y `price: Decimal = Field(gt=Decimal("0"), decimal_places=2)` para rechazar entradas inválidas con `422` y evitar errores de `float` en dinero. | [paso02_validacion_pydantic.py](paso02_validacion_pydantic.py) |
| Paso 3 | `CA-3.1`, `CA-3.2`, `CA-3.3`, `CA-3.4` | En `init_db` se activó `PRAGMA foreign_keys = ON` y se creó `idx_books_author_id` (cambiando `SCAN books` a `SEARCH books USING INDEX`); se implementó `INNER JOIN` en `list_books_with_authors` y paginación ordenada con filtro `LIKE ?` parametrizado en `list_books_page`. | [paso03_sql_relacional.py](paso03_sql_relacional.py) |
| Paso 4 | `CA-4.1`, `CA-4.2`, `CA-4.3` | En `GET /rooms` se inyectó `repo` con `Depends(get_room_repo)` para habilitar `dependency_overrides`; en `decode_jwt_payload_unverified` se decodificó `parts[1]` en Base64Url con relleno `=`; en `POST /admin/rooms` se cambió el rechazo de rol insuficiente de `401` a `403 Forbidden`. | [paso04_depends_y_jwt.py](paso04_depends_y_jwt.py) |
| Paso 5 | `CA-5.1`, `CA-5.2` | En `RoomReservationService` se agregó `self._lock = threading.Lock()` y se envolvió el cuerpo de `reserve` y `reservation_count` en `with self._lock:`, garantizando que ante 5 hilos simultáneos con `Barrier(5)` solo 1 hilo reserve la sala (`stored == 1`). | [paso05_concurrencia.py](paso05_concurrencia.py) |

## Inicio rápido y verificación

1. Instala las dependencias con `uv sync` (o `UV_CACHE_DIR=/tmp/uv-cache-onramp uv sync` si tu caché global tiene permisos restringidos).
2. Inspecciona todos los pasos o uno específico con `uv run onramp inspect` o `uv run onramp inspect --paso N`.
3. Verifica todas las pruebas o un paso específico con `uv run onramp check` o `uv run onramp check --paso N`.

Consulta el [glosario con documentación oficial](docs/glosario.md) para repasar cualquier concepto. Al igual que en el repositorio inicial, [AGENTS.md](AGENTS.md) mantiene el modo tutor socrático por si usas un asistente de IA para revisar la solución.

## Repositorios relacionados

- Índice general de nivelaciones: [ykro/courses-onramp](https://github.com/ykro/courses-onramp)
- Repositorio inicial con ejercicios: [ykro/backend-onramp](https://github.com/ykro/backend-onramp)
- Curso principal: [ykro/backend-course](https://github.com/ykro/backend-course)
