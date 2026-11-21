# Paso 1. Contratos HTTP/1.1, estado aislado y validación con Pydantic

![Contratos HTTP/1.1, validación Pydantic y estado aislado](diagrams/flujo-http-pydantic.svg)

## Por qué importa

Un servidor backend real nunca responde `200 OK` a todas las operaciones ni confía en el JSON que envía el cliente. Cuando devuelves códigos HTTP precisos según [MDN HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status), [FastAPI Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/) y [FastAPI Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/), cualquier cliente distingue si creó un recurso (`201`), si borró sin cuerpo (`204`), si pidió un identificador inexistente (`404`) o si envió datos inválidos (`422`). Al mismo tiempo, definir `BookCreate` con [Pydantic `ConfigDict`](https://docs.pydantic.dev/latest/api/config/), [Pydantic `Field`](https://docs.pydantic.dev/latest/concepts/fields/) y [`Decimal`](https://docs.python.org/3/library/decimal.html) evita campos desconocidos y errores de redondeo en dinero, mientras aislar el catálogo dentro de `create_app()` impide que dos instancias mezclen sus datos.

## Qué se construye

Trabajas sobre [paso01_http_y_pydantic.py](../../paso01_http_y_pydantic.py) (~14 minutos):

- **Creación con `201 Created` (TODO 1):** agrega `status_code=status.HTTP_201_CREATED` al decorador `@app.post("/books", ...)`.
- **Error `404 Not Found` en `GET /books/{book_id}` (TODO 2):** cuando el libro no existe, lanza `HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")` en vez de devolver un diccionario con código `200`.
- **Borrado con `204 No Content` en `DELETE /books/{book_id}` (TODO 3):** agrega `status_code=status.HTTP_204_NO_CONTENT` y devuelve `Response(status_code=status.HTTP_204_NO_CONTENT)` sin cuerpo.
- **Estado aislado dentro de `create_app()` (TODO 4):** elimina `_SHARED_BOOKS` y `_NEXT_ID` del nivel de módulo y decláralos como variables locales (`books` y `next_id`) dentro de `create_app()`, usando `nonlocal next_id` en `create_book`.
- **Rechazar campos extra en `BookCreate` (TODO 5):** agrega `model_config = ConfigDict(extra="forbid")`.
- **Restringir `title` y usar `Decimal` en `price` (TODO 6):** define `title: str = Field(min_length=1, max_length=120)` y `price: Decimal = Field(gt=Decimal("0"), decimal_places=2)`, guardando `payload.price` directo en `BookOut`.

## Criterios de aceptación

- `CA-1.1` `POST /books` responde `201 Created`, `GET /books/1` responde `200 OK` y `GET /books/999` responde `404 Not Found`.
- `CA-1.2` `DELETE /books/{book_id}` responde `204 No Content` con cuerpo vacío (`b""`), y un segundo borrado del mismo identificador responde `404 Not Found`.
- `CA-1.3` Dos instancias creadas con `create_app()` mantienen catálogos separados: crear un libro en una instancia deja vacía la lista `GET /books` de la otra.
- `CA-1.4` `POST /books` responde `422 Unprocessable Entity` cuando el JSON trae un campo extra, título vacío, precio negativo, precio cero o más de dos decimales.
- `CA-1.5` `BookCreate.price` usa `Decimal` y conserva el monto exacto en base 10.

## Cómo verificar

Observa primero las respuestas actuales del servidor y luego corre las pruebas del Paso 1:

```bash
uv run onramp inspect --paso 1
uv run onramp check --paso 1
```
