"""Paso 2: Base de datos relacional en SQLite puro, JOIN, paginación e índices."""

import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    """Activa llaves foráneas, crea las tablas authors y books y agrega el índice."""
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_books_author_id
        ON books(author_id)
        """
    )
    conn.commit()


def add_author(conn: sqlite3.Connection, name: str) -> int:
    """Inserta un autor y devuelve su identificador."""
    cursor = conn.execute("INSERT INTO authors (name) VALUES (?)", (name,))
    conn.commit()
    assert cursor.lastrowid is not None
    return int(cursor.lastrowid)


def add_book(conn: sqlite3.Connection, title: str, year: int, author_id: int) -> int:
    """Inserta un libro vinculado a un autor existente y devuelve su identificador."""
    cursor = conn.execute(
        "INSERT INTO books (title, year, author_id) VALUES (?, ?, ?)",
        (title, year, author_id),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return int(cursor.lastrowid)


def list_books_with_authors(conn: sqlite3.Connection) -> list[dict[str, object]]:
    """Devuelve todos los libros junto con el nombre de su autor usando INNER JOIN."""
    rows = conn.execute(
        """
        SELECT b.id, b.title, b.year, a.name AS author_name
        FROM books AS b
        INNER JOIN authors AS a ON a.id = b.author_id
        ORDER BY b.id ASC
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "year": row["year"],
            "author_name": row["author_name"],
        }
        for row in rows
    ]


def list_books_page(
    conn: sqlite3.Connection,
    limit: int,
    offset: int,
    title_filter: str | None = None,
) -> list[dict[str, object]]:
    """Devuelve una página ordenada de libros usando parámetros '?' seguros."""
    if title_filter is not None:
        rows = conn.execute(
            """
            SELECT b.id, b.title, b.year, a.name AS author_name
            FROM books AS b
            INNER JOIN authors AS a ON a.id = b.author_id
            WHERE b.title LIKE ?
            ORDER BY b.title ASC
            LIMIT ? OFFSET ?
            """,
            (f"%{title_filter}%", limit, offset),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT b.id, b.title, b.year, a.name AS author_name
            FROM books AS b
            INNER JOIN authors AS a ON a.id = b.author_id
            ORDER BY b.title ASC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "year": row["year"],
            "author_name": row["author_name"],
        }
        for row in rows
    ]


def explain_books_by_author(conn: sqlite3.Connection, author_id: int) -> list[str]:
    """Devuelve el detalle de EXPLAIN QUERY PLAN al buscar libros por author_id."""
    rows = conn.execute(
        "EXPLAIN QUERY PLAN SELECT id, title FROM books WHERE author_id = ?",
        (author_id,),
    ).fetchall()
    return [str(row["detail"]) for row in rows]
