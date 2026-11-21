# Glosario de Backend Onramp

Este glosario reúne los conceptos clave que aparecen en los 5 pasos de Backend Onramp. Cada entrada explica qué resuelve el concepto y enlaza a su documentación oficial.

## HTTP status codes

Códigos numéricos de tres dígitos que el servidor devuelve en cada respuesta para indicar qué pasó con la petición, según [MDN HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status). En este repositorio usas `201 Created` al crear un libro o una sala, `204 No Content` al borrar sin cuerpo, `404 Not Found` cuando el recurso no existe y `422 Unprocessable Entity` cuando el JSON no cumple la validación.

## Pydantic (`BaseModel`, `Field` y `ConfigDict`)

Biblioteca de validación de datos que FastAPI usa para revisar cada petición antes de ejecutar tu función. Con [`ConfigDict(extra="forbid")`](https://docs.pydantic.dev/latest/api/config/) rechazas campos que el cliente no debería enviar, y con [`Field`](https://docs.pydantic.dev/latest/concepts/fields/) fijas límites como longitud mínima (`min_length`) o precios mayores que cero (`gt`).

## `Decimal`

Tipo numérico de la biblioteca estándar de Python para operar en base 10 con exactitud, documentado en [Python `decimal`](https://docs.python.org/3/library/decimal.html). En precios y montos de dinero reemplaza a `float` porque los números en punto flotante binario acumulan errores de redondeo como `0.1 + 0.2 != 0.3`.

## `PRAGMA foreign_keys`

Instrucción de SQLite que activa la verificación de llaves foráneas en la conexión actual, según [SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html). SQLite desactiva esta verificación por defecto al abrir cada conexión; al ejecutar `PRAGMA foreign_keys = ON`, la base de datos lanza `sqlite3.IntegrityError` si intentas guardar un libro con un `author_id` que no existe.

## `INNER JOIN`

Cláusula SQL que combina filas de dos tablas cuando coinciden en una columna relacionada, documentada en [SQLite `SELECT` y `JOIN`](https://www.sqlite.org/lang_select.html#fromclause). En el Paso 3 une `books` con `authors` usando `ON a.id = b.author_id` para devolver cada libro junto con el nombre de su autor en una sola consulta.

## `EXPLAIN QUERY PLAN`

Comando de SQLite que muestra cómo ejecutará una consulta sin devolver sus filas, documentado en [SQLite `EXPLAIN QUERY PLAN`](https://www.sqlite.org/eqp.html). Permite comprobar si la base de datos recorre toda la tabla (`SCAN books`) o salta directo a las filas que coinciden mediante un índice (`SEARCH books USING INDEX`).

## `Depends` y `dependency_overrides`

Mecanismo de inyección de dependencias de FastAPI documentado en [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) y [Testing Dependencies](https://fastapi.tiangolo.com/advanced/testing-dependencies/). Al declarar `repo: Annotated[RoomRepository, Depends(get_room_repo)]`, una ruta recibe su repositorio desde afuera en lugar de leer una variable global, lo que permite reemplazarlo por un repositorio aislado en pruebas con `app.dependency_overrides`.

## JWT y `Base64Url`

JSON Web Token ([RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)) es un formato compacto con tres segmentos separados por punto: `encabezado.contenido.firma`. El bloque central no está cifrado, sino codificado en Base64Url ([Python `urlsafe_b64decode`](https://docs.python.org/3/library/base64.html#base64.urlsafe_b64decode)), por lo que cualquiera puede leerlo; la seguridad viene de verificar su firma criptográfica en el servidor con [PyJWT](https://pyjwt.readthedocs.io/en/stable/).

## `401 Unauthorized` frente a `403 Forbidden`

Dos códigos HTTP distintos para control de acceso. El servidor devuelve [`401 Unauthorized`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401) cuando falta el token o su firma no es válida (no sabe quién eres). Devuelve [`403 Forbidden`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403) cuando el token es válido, pero tu rol no tiene permiso para ejecutar esa acción.

## Race condition (condición de carrera)

Defecto de concurrencia donde el resultado cambia según el orden en que se intercalan varios hilos que leen y escriben el mismo dato al mismo tiempo. En el Paso 5 aparece cuando cinco hilos consultan si `"sala-a"` está libre antes de que alguno termine de escribir su reserva, logrando reservar la misma sala varias veces.

## `threading.Lock`

Candado de exclusión mutua de la biblioteca estándar de Python, documentado en [Python `threading.Lock`](https://docs.python.org/3/library/threading.html#lock-objects). Al envolver la sección crítica dentro de `with self._lock:`, garantizas que solo un hilo a la vez verifique la disponibilidad y guarde la reserva.
