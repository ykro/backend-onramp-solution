"""Paso 2: Validación estricta con Pydantic, `extra="forbid"` y `Decimal`."""

from decimal import Decimal

from fastapi import FastAPI, status
from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    """Datos de entrada para registrar un libro en el catálogo."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=120)
    price: Decimal = Field(gt=Decimal("0"), decimal_places=2)


class BookOut(BaseModel):
    """Representación pública de un libro registrado."""

    id: int
    title: str
    price: Decimal


def create_app() -> FastAPI:
    """Crea una aplicación FastAPI enfocada en validar la entrada con Pydantic."""
    app = FastAPI(title="Biblioteca Onramp - Paso 2")
    books: dict[int, BookOut] = {}
    next_id = 1

    @app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
    def create_book(payload: BookCreate) -> BookOut:
        nonlocal next_id
        book = BookOut(id=next_id, title=payload.title, price=payload.price)
        books[next_id] = book
        next_id += 1
        return book

    return app
