# Backend On-Ramp — Solución de referencia

Este repositorio contiene la solución completa y comentada del [Backend On-Ramp](https://github.com/ykro/backend-onramp) para el [Curso 1 de Backend con FastAPI](https://github.com/ykro/backend-course). Todas las 12 pruebas de [tests/test_onramp.py](./tests/test_onramp.py) pasan aquí sin dependencias externas ni Docker.

**Repositorios relacionados**

- Índice general de nivelaciones: [ykro/courses-onramp](https://github.com/ykro/courses-onramp)
- Repositorio inicial con ejercicios: [ykro/backend-onramp](https://github.com/ykro/backend-onramp)
- Curso principal: [ykro/backend-course](https://github.com/ykro/backend-course)

## Instalación y verificación

En la raíz del repositorio corre:

```bash
uv sync
uv run onramp inspect
uv run onramp check
```

Si `uv` reporta un problema de permisos con la caché global, usa `UV_CACHE_DIR=/tmp/uv-cache-onramp uv sync`.

---

## Qué se cambió en cada laboratorio y por qué pasa cada prueba

### Lab 1: HTTP, validación estricta y estado aislado

Archivo resuelto: [lab01_http_y_servidor.py](./lab01_http_y_servidor.py)

1. **Validación estricta en `BookCreate` (TODO 1)**
   - **Qué estaba roto en el inicial:** `BookCreate` aceptaba cualquier campo extra sin rechazarlo, permitía títulos vacíos y usaba `price: float` sin límite inferior ni control de decimales.
   - **Cambio exacto:** Se agregó `model_config = ConfigDict(extra="forbid")`, se restringió `title` con `Field(min_length=1, max_length=120)` y se cambió `price` a `Decimal = Field(gt=Decimal("0"), decimal_places=2)`.
   - **Por qué pasan las pruebas:** En `test_lab01_validation_422_extra_forbid_and_404_not_found`, enviar un campo extra (`"descuento": 10`) o un precio negativo (`"-5.00"`) hace que FastAPI y Pydantic rechacen la petición con `422 Unprocessable Entity`. En `test_lab01_create_and_get_book_status_and_decimal`, el precio conserva su valor exacto en base 10 (`Decimal("125.50")`).

2. **Código `201 Created` en `POST /books` (TODO 2)**
   - **Qué estaba roto en el inicial:** `@app.post("/books", response_model=BookOut)` devolvía `200 OK` por defecto y convertía `payload.price` desde `float`.
   - **Cambio exacto:** Se añadió `status_code=status.HTTP_201_CREATED` al decorador de `create_book` y se pasó `payload.price` directo como `Decimal` a `BookOut`.
   - **Por qué pasan las pruebas:** `test_lab01_create_and_get_book_status_and_decimal`, `test_lab01_delete_returns_204_without_body` y `test_lab01_isolated_state_between_apps` reciben `201` al crear un libro.

3. **Códigos `404 Not Found` y `204 No Content` en `GET /books/{book_id}` y `DELETE /books/{book_id}` (TODO 3a y 3b)**
   - **Qué estaba roto en el inicial:** `get_book` devolvía `{"detail": "Libro no encontrado"}` con código `200`, y `delete_book` respondía `{"deleted": book_id}` con código `200`.
   - **Cambio exacto:** En `get_book` se lanzó `HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")` cuando el libro no existe. En `delete_book` se colocó `status_code=status.HTTP_204_NO_CONTENT` y se retornó `Response(status_code=status.HTTP_204_NO_CONTENT)`.
   - **Por qué pasan las pruebas:** En `test_lab01_validation_422_extra_forbid_and_404_not_found`, `GET /books/999` devuelve `404`. En `test_lab01_delete_returns_204_without_body`, el primer `DELETE` devuelve `204` con cuerpo vacío (`b""`) y el segundo `DELETE` sobre el mismo identificador devuelve `404`.

4. **Estado aislado dentro de `create_app()` (TODO 4)**
   - **Qué estaba roto en el inicial:** `_SHARED_BOOKS` y `_NEXT_ID` vivían como variables globales de módulo, por lo que dos instancias creadas con `create_app()` compartían los mismos libros.
   - **Cambio exacto:** Se eliminaron `_SHARED_BOOKS` y `_NEXT_ID` del módulo y se crearon `books: dict[int, BookOut] = {}` y `next_id = 1` dentro de `create_app()`, actualizando `next_id` con `nonlocal next_id` dentro de `create_book`.
   - **Por qué pasa la prueba:** En `test_lab01_isolated_state_between_apps`, crear un libro en `client_a` deja vacío el catálogo de `client_b` (`[]`).

---

### Lab 2: SQLite relacional, JOIN, paginación e índices

Archivo resuelto: [lab02_sql_relacional.py](./lab02_sql_relacional.py)

1. **Integridad referencial en `init_db` (TODO 1)**
   - **Qué estaba roto en el inicial:** `init_db` creaba las tablas `authors` y `books` sin activar `PRAGMA foreign_keys = ON`, así que SQLite aceptaba libros con un `author_id` inexistente.
   - **Cambio exacto:** Se agregó `conn.execute("PRAGMA foreign_keys = ON")` al inicio de `init_db`.
   - **Por qué pasa la prueba:** En `test_lab02_foreign_key_enforcement`, llamar a `add_book(conn, "Libro sin autor válido", 2025, 9999)` lanza `sqlite3.IntegrityError`.

2. **Consulta con `INNER JOIN` en `list_books_with_authors` (TODO 2)**
   - **Qué estaba roto en el inicial:** `list_books_with_authors` devolvía una lista vacía `[]`.
   - **Cambio exacto:** Se ejecutó `SELECT b.id, b.title, b.year, a.name AS author_name FROM books AS b INNER JOIN authors AS a ON a.id = b.author_id ORDER BY b.id ASC` y se transformó cada fila en un diccionario con las llaves `id`, `title`, `year` y `author_name`.
   - **Por qué pasa la prueba:** En `test_lab02_insert_and_inner_join`, el resultado contiene el libro unido con el nombre de su autor (`"Miguel Ángel Asturias"`).

3. **Paginación y filtro seguro con parámetros `?` en `list_books_page` (TODO 3)**
   - **Qué estaba roto en el inicial:** `list_books_page` devolvía una lista vacía `[]`.
   - **Cambio exacto:** Se implementó la consulta con `INNER JOIN authors`, `ORDER BY b.title ASC LIMIT ? OFFSET ?` y, cuando `title_filter is not None`, se añadió `WHERE b.title LIKE ?` pasando `(f"%{title_filter}%", limit, offset)` como tupla de parámetros.
   - **Por qué pasa la prueba:** En `test_lab02_pagination_with_order_limit_offset_and_params`, `limit=2, offset=1` devuelve exactamente la segunda página ordenada alfabéticamente y la cadena `"'; DROP TABLE books; --"` se evalúa como texto literal sin borrar ni alterar la tabla `books`.

4. **Índice en `books(author_id)` dentro de `init_db` (TODO 4)**
   - **Qué estaba roto en el inicial:** Sin índice sobre `author_id`, `explain_books_by_author` reportaba `SCAN books`, lo que obliga a leer la tabla completa.
   - **Cambio exacto:** Se agregó `CREATE INDEX IF NOT EXISTS idx_books_author_id ON books(author_id)` en `init_db`.
   - **Por qué pasa la prueba:** En `test_lab02_index_changes_query_plan_from_scan_to_search`, `EXPLAIN QUERY PLAN` devuelve `SEARCH books USING INDEX idx_books_author_id` y ya no contiene `SCAN books`.

---

### Lab 3: Inyección de dependencias, JWT y condición de carrera

Archivo resuelto: [lab03_di_jwt_y_carrera.py](./lab03_di_jwt_y_carrera.py)

1. **Inyección de dependencias en `GET /rooms` (TODO 1)**
   - **Qué estaba roto en el inicial:** `list_rooms()` leía directo `_default_repo.list_rooms()`, ignorando cualquier reemplazo registrado en `app.dependency_overrides`.
   - **Cambio exacto:** Se cambió la firma a `list_rooms(repo: Annotated[RoomRepository, Depends(get_room_repo)])` y se devolvió `repo.list_rooms()`.
   - **Por qué pasa la prueba:** En `test_lab03_dependency_overrides_isolates_tests`, al sobrescribir `app.dependency_overrides[lab03.get_room_repo]`, `GET /rooms` responde con la sala del repositorio aislado (`"sala-test"`).

2. **Decodificación Base64Url del JWT en `decode_jwt_payload_unverified` (TODO 2)**
   - **Qué estaba roto en el inicial:** `decode_jwt_payload_unverified` lanzaba `NotImplementedError`.
   - **Cambio exacto:** Se dividió el token con `token.split(".")`, se validó que tenga 3 segmentos, se completó el relleno `=` del bloque central (`"=" * (-len(payload_segment) % 4)`), se decodificó con `base64.urlsafe_b64decode(...)` y se convirtió a diccionario con `json.loads(...)`.
   - **Por qué pasa la prueba:** En `test_lab03_decode_jwt_payload_without_secret`, la función lee `"sub": "maria"` y `"role": "member"` sin necesitar `JWT_SECRET`, demostrando que un JWT firmado protege la integridad pero no oculta el contenido.

3. **Separación de `401` y `403` en `POST /admin/rooms` (TODO 3)**
   - **Qué estaba roto en el inicial:** Cuando un usuario con token válido tenía rol `"member"` en lugar de `"librarian"`, `create_room` respondía `401 Unauthorized`.
   - **Cambio exacto:** En la verificación `if claims.get("role") != "librarian":`, se cambió `status.HTTP_401_UNAUTHORIZED` por `status.HTTP_403_FORBIDDEN`.
   - **Por qué pasa la prueba:** En `test_lab03_auth_separates_401_and_403`, omitir el encabezado o enviar una firma inválida devuelve `401`, un token válido con rol `"member"` devuelve `403` y un token válido con rol `"librarian"` crea la sala con `201`.

4. **Exclusión mutua con `threading.Lock` en `RoomReservationService` (TODO 4)**
   - **Qué estaba roto en el inicial:** `reserve` revisaba si la sala estaba libre, dormía `delay_seconds` y luego insertaba la reserva sin bloqueo. Cuando 5 hilos entraban a la vez, todos veían la sala libre y los 5 registraban su reserva.
   - **Cambio exacto:** Se creó `self._lock = threading.Lock()` en `__init__` y se protegió todo el bloque de `reserve` y `reservation_count` con `with self._lock:`.
   - **Por qué pasa la prueba:** En `test_lab03_concurrent_booking_protected_with_lock`, solo el primer hilo que adquiere el candado gana la sala (`successes == 1`) y los otros 4 reciben `False` (`stored == 1`).

## Uso de IA

Al igual que en el repositorio inicial, [AGENTS.md](./AGENTS.md) mantiene el modo tutor socrático por si usas un asistente de IA para repasar cualquier cambio de esta solución.
