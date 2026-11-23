# Paso 4. Requests simultáneos y `threading.Lock`

![Paso 4. Requests simultáneos y `threading.Lock`](diagrams/lock-concurrencia.svg)

Este paso toma unos 25 minutos.

## Antes de empezar

1. Dos personas reservan la última sala libre en el mismo milisegundo. ¿Qué podría salir mal si el servidor revisa "¿está libre?" y después guarda la reserva?
2. En Arquitectura del computador viste que varias instrucciones pueden intercalarse. ¿Qué parte de `reserve` no debería intercalarse con otro hilo?
3. ¿Por qué un error de este tipo casi nunca aparece cuando pruebas a mano?

## Por qué importa

Un servidor web atiende varios requests al mismo tiempo. Cuando dos de ellos leen y escriben el mismo dato, aparece una race condition, ambos ven la sala libre y ambos la reservan. [`threading.Lock`](https://docs.python.org/3/library/threading.html#lock-objects) deja pasar un hilo a la vez por la sección crítica. En los retos de las Unidades 2 y 3 verás el mismo problema con agendas y con intentos de login.

## Lo mínimo que necesitas saber

- **Hilos y memoria compartida.** Varios hilos de un mismo proceso pueden ejecutar el mismo método a la vez y leer o escribir el mismo diccionario en memoria.
- **Candado (`threading.Lock()`).** Crea un candado compartido en `__init__` (`self._lock = threading.Lock()`). Solo un hilo puede sostenerlo al mismo tiempo; los demás esperan su turno.
- **Sección crítica con `with self._lock:`.** Todo el bloque indentado dentro de `with self._lock:` se ejecuta de forma exclusiva y libera el candado automáticamente al salir, incluso si ocurre un error.

## Qué vas a hacer

- **Leer.** Corre `uv run onramp inspect --paso 4` varias veces. Cinco hilos arrancan juntos gracias a `threading.Barrier(5)` e intentan reservar la misma sala.
- **Debuguear.** En [paso04_concurrencia.py](../../paso04_concurrencia.py), marca las líneas que van desde que un hilo revisa la sala hasta que guarda la reserva. El `time.sleep` simula una base de datos lenta y hace visible el problema.
- **Escribir.** Protege esa sección para que solo un hilo a la vez la ejecute.

## Criterios de aceptación

- `CA-4.1` Con 5 hilos sincronizados que reservan `"sala-a"`, se confirma exactamente 1 reserva y queda guardado 1 registro.
- `CA-4.2` Con 5 hilos por sala sobre `"sala-a"` y `"sala-b"`, cada sala queda con exactamente 1 reserva.

## Al terminar

1. Si pones el candado solo alrededor de `append`, sin incluir la revisión de disponibilidad, ¿se arregla el problema? ¿Por qué?
2. Tu API corre en dos servidores detrás de un load balancer (un servidor que reparte los requests entre los dos). ¿Sigue sirviendo `threading.Lock`? ¿Qué pieza tendría que garantizar la exclusión en ese caso?
3. Quitas el `time.sleep` y los tests pasan sin candado. ¿Significa que el código es correcto?
4. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

```bash
uv run onramp inspect --paso 4
uv run onramp check --paso 4
```

Si te trabas, abre la [pista 1](hints/1.md). Cada pista da un poco más que la anterior; la pista 3 trae un esqueleto, nunca la respuesta completa.

## Respuestas de autoevaluación («Al terminar»)

1. No. Dos hilos pueden pasar la revisión antes de que cualquiera llegue al `append`, y los dos guardan su reserva. La revisión y la escritura tienen que estar dentro del mismo candado.
2. No, porque cada servidor tiene su propio candado en memoria. La exclusión la tiene que garantizar algo compartido, por ejemplo la base de datos con una restricción `UNIQUE` o una transacción.
3. No. Las race conditions dependen del momento en que se intercalan los hilos; quitar la espera solo las hace menos probables. El código sigue siendo incorrecto.
4. Respuesta personal. Debe mencionar la sección crítica entre revisar y guardar, y el candado compartido por todos los hilos.
