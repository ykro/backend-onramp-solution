"""Paso 0 (~35 min): tu primer servidor web con FastAPI.

Levanta el servidor con `uv run uvicorn paso00_hola:app --reload`, ábrelo en el navegador
(`http://127.0.0.1:8000/` y `http://127.0.0.1:8000/docs`) y resuelve los TODO hasta que pase
`uv run onramp check --paso 0`.
"""

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
