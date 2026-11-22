# Paso 3. Dependencias con `Depends` y autorización con JWT

![Paso 3. Dependencias con `Depends` y autorización con JWT](diagrams/depends-y-jwt.svg)

Este paso toma unos 40 minutos.

## Antes de empezar

1. Si una ruta lee una variable global, ¿cómo harías para que un test use datos distintos sin cambiar el código de la ruta?
2. Un JWT se ve como texto aleatorio. ¿Crees que alguien que lo intercepta puede leer lo que trae adentro?
3. Un usuario manda un token válido pero no tiene permiso para crear salas. ¿Debería recibir el mismo error que alguien que no mandó token?

## Por qué importa

[`Depends`](https://fastapi.tiangolo.com/tutorial/dependencies/) es la forma en que FastAPI le entrega a cada ruta lo que necesita (un repositorio, el usuario actual), y [`dependency_overrides`](https://fastapi.tiangolo.com/advanced/testing-dependencies/) permite reemplazarlo en los tests. Un [JWT](https://jwt.io/introduction) es un token firmado con tres partes separadas por punto, y la parte del medio solo está codificada, no cifrada. En la Unidad 3 del curso construirás el login completo sobre estas dos ideas.

## Lo mínimo que necesitas saber

Este paso junta dos ideas que no dependen una de la otra. Puedes resolver primero una y después la otra.

- **Inyección de dependencias.** En lugar de que la ruta busque por su cuenta el repositorio de salas, lo declara como parámetro y FastAPI se lo entrega. Es como recibir un objeto en el constructor en Java en lugar de crearlo adentro. La ventaja es que en un test puedes entregarle otro repositorio.
- **Codificar no es cifrar.** Base64 convierte bytes en letras y números para que viajen como texto. Cualquiera lo revierte sin clave. Cifrar sí necesita una clave.
- **Las tres partes de un JWT.** `encabezado.contenido.firma`. Las dos primeras son JSON en Base64Url. La firma la calcula el servidor con su secreto y sirve para detectar si alguien cambió el contenido.
- **`401` y `403`.** `401` significa "no sé quién eres" (falta el token o es inválido). `403` significa "sé quién eres, pero no tienes permiso".

## Qué vas a hacer

- **Leer.** Corre `uv run onramp inspect --paso 3`. Copia completo el token que imprime y pégalo en [jwt.io](https://jwt.io) para ver su contenido. Luego lee `get_room_repo` y las dos rutas de [paso03_depends_y_jwt.py](../../paso03_depends_y_jwt.py).
- **Debuguear.** En `inspect`, un usuario con rol `member` recibe `401` al crear una sala. Decide qué código corresponde según [401](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401) y [403](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403).
- **Escribir.** Resuelve los tres `TODO`, la dependencia en `GET /rooms`, la lectura del bloque central del token y el código para el rol sin permiso.

## Criterios de aceptación

- `CA-3.1` Sobrescribir `app.dependency_overrides[get_room_repo]` hace que `GET /rooms` devuelva las salas del repositorio inyectado.
- `CA-3.2` `decode_jwt_payload_unverified(token)` devuelve el diccionario con `sub` y `role` sin usar `JWT_SECRET`.
- `CA-3.3` `POST /admin/rooms` responde `401` sin token o con firma inválida, `403` con rol `member` y `201` con rol `librarian`.

## Al terminar

1. Si cualquiera puede leer el contenido de un JWT, ¿qué impide que alguien cambie `"role": "member"` por `"librarian"` y lo reenvíe?
2. ¿Qué dato nunca deberías guardar dentro de un JWT y por qué?
3. En un test reemplazas el repositorio con `dependency_overrides`. ¿Qué tendrías que hacer al terminar el test para no afectar a los siguientes?
4. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

```bash
uv run onramp inspect --paso 3
uv run onramp check --paso 3
```

Si te trabas, abre la [pista 1](hints/1.md). Cada pista da un poco más que la anterior; la pista 3 trae un esqueleto, nunca la respuesta completa.

## Respuestas de autoevaluación

1. La firma. El servidor recalcula la firma con su secreto; si alguien cambia el contenido, la firma ya no coincide y `jwt.decode` lanza un error que termina en `401`.
2. Contraseñas, números de tarjeta o cualquier secreto, porque el contenido viaja solo codificado en Base64Url y cualquiera que tenga el token puede leerlo.
3. Limpiar el reemplazo con `app.dependency_overrides.clear()` (o crear una app nueva por test), para que el siguiente test vuelva a usar la dependencia real.
4. Respuesta personal. Debe mencionar la inyección con `Depends`, que el bloque central del JWT se lee sin secreto y la diferencia entre `401` y `403`.
