"""Paso 0: Primer servidor web con FastAPI, parámetros de ruta y respuestas JSON."""

from fastapi import FastAPI

app = FastAPI(title="Biblioteca Onramp - Paso 0")

LIBROS: list[dict[str, object]] = [
    {"id": 1, "titulo": "El Señor Presidente", "anio": 1946},
    {"id": 2, "titulo": "Hombres de Maíz", "anio": 1949},
]


@app.get("/")
def raiz() -> dict[str, str]:
    """Responde un JSON fijo para comprobar que el servidor está vivo."""
    return {"mensaje": "Hola desde la biblioteca"}


@app.get("/saludo/{nombre}")
def saludar(nombre: str) -> dict[str, str]:
    """Arma un saludo con el nombre que viene en la ruta."""
    return {"saludo": f"Hola, {nombre}"}


@app.get("/libros")
def listar_libros() -> list[dict[str, object]]:
    """Devuelve el catálogo fijo en JSON."""
    return LIBROS
