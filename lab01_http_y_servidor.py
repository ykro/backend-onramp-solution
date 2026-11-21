"""Lab 01: Peticiones HTTP reales, validación con Pydantic y estado aislado."""

from decimal import Decimal

from fastapi import FastAPI, HTTPException, Response, status
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
    """Crea una aplicación FastAPI con su propio catálogo en memoria."""
    app = FastAPI(title="Biblioteca Onramp - Lab 01")
    books: dict[int, BookOut] = {}
    next_id = 1

    @app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
    def create_book(payload: BookCreate) -> BookOut:
        nonlocal next_id
        book = BookOut(id=next_id, title=payload.title, price=payload.price)
        books[next_id] = book
        next_id += 1
        return book

    @app.get("/books", response_model=list[BookOut])
    def list_books() -> list[BookOut]:
        return list(books.values())

    @app.get("/books/{book_id}", response_model=BookOut)
    def get_book(book_id: int) -> BookOut:
        book = books.get(book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado",
            )
        return book

    @app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_book(book_id: int) -> Response:
        if book_id not in books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado",
            )
        del books[book_id]
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app
