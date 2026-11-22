# Paso 0. Entorno y tu primer servidor web

Este paso toma unos 25 minutos.

## Antes de empezar

1. Cuando escribes una URL en el navegador y presionas Enter, ¿qué le envía el navegador al servidor y qué recibe de vuelta?
2. ¿Qué diferencia hay entre abrir `http://127.0.0.1:8000/` en el navegador y ejecutar una función de Python directamente?
3. Si el servidor responde `404`, ¿el problema está en el navegador o en el servidor?

## Por qué importa

Todo el curso gira alrededor de una idea, un cliente (el navegador, `curl`, una app móvil) manda un request HTTP y un servidor devuelve una respuesta con un código de estado y un cuerpo, casi siempre en JSON. Antes de hablar de validación, bases de datos o tokens, conviene ver esa conversación con tus propios ojos, con un servidor real corriendo en tu computadora. [FastAPI](https://fastapi.tiangolo.com/tutorial/first-steps/) además genera una página `/docs` donde puedes probar cada endpoint sin escribir un cliente.

## Lo mínimo que necesitas saber

- **Cliente y servidor.** El servidor es un programa que se queda escuchando en un puerto (aquí el `8000`). El cliente le manda requests y espera respuestas.
- **Request.** Lleva un método (`GET` para leer, `POST` para crear, `DELETE` para borrar) y una ruta (`/libros`, `/saludo/Ana`).
- **Respuesta.** Lleva un código de estado (`200` todo bien, `404` no existe esa ruta o recurso, `422` datos inválidos) y un cuerpo.
- **JSON.** Es texto con la forma de un diccionario o una lista de Python, por ejemplo `{"saludo": "Hola, Ana"}`. FastAPI convierte lo que devuelves en JSON.
- **Decorador.** `@app.get("/ruta")` encima de una función le dice a FastAPI "cuando llegue un `GET` a esta ruta, ejecuta esta función". Es la parte de Python que más sorprende si vienes de Java.

## Qué vas a hacer

- **Preparar.** Instala [uv](https://docs.astral.sh/uv/getting-started/installation/) (en macOS y Linux `curl -LsSf https://astral.sh/uv/install.sh | sh`; en Windows `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`), cierra y abre la terminal, y corre `uv sync` en la raíz del repo. `uv` descarga Python 3.13 y las dependencias del proyecto sin tocar el Python de tu sistema.
- **Leer.** Abre [paso00_hola.py](../../paso00_hola.py). Levanta el servidor con `uv run uvicorn paso00_hola:app --reload`, abre `http://127.0.0.1:8000/` y luego `http://127.0.0.1:8000/docs`. En otra terminal prueba `curl -i http://127.0.0.1:8000/` y fíjate en la primera línea de la respuesta.
- **Debuguear.** Pide `http://127.0.0.1:8000/saludo/Ana` y `http://127.0.0.1:8000/libros`. Las dos responden `404`. Lee el `TODO` del archivo para saber qué debería pasar.
- **Escribir.** Agrega los dos endpoints que faltan. Gracias a `--reload`, el servidor se reinicia solo cada vez que guardas el archivo; recarga `/docs` y prueba cada uno con el botón **Try it out**.

## Criterios de aceptación

- `CA-0.1` `GET /` responde `200` con `{"mensaje": "Hola desde la biblioteca"}` (ya viene hecho; si falla, el problema está en tu entorno).
- `CA-0.2` `GET /saludo/{nombre}` responde `200` con `{"saludo": "Hola, <nombre>"}` para cualquier nombre, incluso con tildes y espacios.
- `CA-0.3` `GET /libros` responde `200` con la lista `LIBROS` en JSON y las dos rutas aparecen en `/openapi.json`.

## Al terminar

1. Con el servidor apagado, ¿qué te responde `curl http://127.0.0.1:8000/`? ¿Por qué es distinto de un `404`?
2. Pide `http://127.0.0.1:8000/saludo/` (sin nombre). ¿Qué código devuelve FastAPI y por qué no llega a ejecutar tu función?
3. ¿Qué cambiaría si `GET /libros` devolviera un `set` de Python en lugar de una lista? Pruébalo y revisa la respuesta.
4. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

```bash
uv run onramp inspect --paso 0
uv run onramp check --paso 0
```

Si te trabas, abre la [pista 1](hints/1.md). Cada pista da un poco más que la anterior; la pista 3 trae un esqueleto, nunca la respuesta completa.

## Respuestas de autoevaluación

1. `curl` responde que no pudo conectarse (`Connection refused`). Nadie está escuchando en ese puerto, así que no hay servidor que conteste. Un `404` sí es una respuesta, el servidor existe y te dice que esa ruta no.
2. Devuelve `404`, porque la ruta `/saludo/` no coincide con `/saludo/{nombre}`. FastAPI compara la ruta antes de llamar a tu función y, si no encuentra coincidencia, responde sin ejecutar tu código.
3. JSON no tiene sets. FastAPI convierte el `set` en una lista, pero sin orden garantizado; por eso conviene devolver listas cuando el orden importa.
4. Respuesta personal. Debe mencionar el decorador con la ruta, el parámetro tomado de la URL y que FastAPI convierte el `return` en JSON.
