"""CLI principal de Backend Onramp: `onramp inspect` y `onramp check`."""

import argparse
import sqlite3
import subprocess
import sys
import warnings

from onramp_judge.helpers import (
    format_http_exchange,
    format_query_plan,
    run_concurrent_bookings,
)


def _inspect_lab01() -> None:
    from fastapi.testclient import TestClient

    import lab01_http_y_servidor as lab01

    print("=== LAB 01: HTTP, Pydantic y estado aislado ===")
    try:
        app_a = lab01.create_app()
        app_b = lab01.create_app()
        client_a = TestClient(app_a)
        client_b = TestClient(app_b)

        res_create = client_a.post("/books", json={"title": "Clean Code", "price": "125.50"})
        print(
            format_http_exchange(
                "POST",
                "/books",
                res_create.status_code,
                res_create.headers.get("content-type"),
                res_create.content,
            )
        )

        res_extra = client_a.post(
            "/books",
            json={"title": "Extra", "price": "50.00", "campo_inventado": True},
        )
        print(
            format_http_exchange(
                "POST",
                "/books (con campo extra)",
                res_extra.status_code,
                res_extra.headers.get("content-type"),
                res_extra.content,
            )
        )

        res_missing = client_a.get("/books/999")
        print(
            format_http_exchange(
                "GET",
                "/books/999",
                res_missing.status_code,
                res_missing.headers.get("content-type"),
                res_missing.content,
            )
        )

        res_delete = client_a.delete("/books/1")
        print(
            format_http_exchange(
                "DELETE",
                "/books/1",
                res_delete.status_code,
                res_delete.headers.get("content-type"),
                res_delete.content,
            )
        )

        res_isolated = client_b.get("/books")
        print(f"  Libros visibles en una segunda instancia (app_b): {res_isolated.text}")
    except Exception as exc:
        print(f"  Error al inspeccionar Lab 01: {type(exc).__name__}: {exc}")
    print()


def _inspect_lab02() -> None:
    import lab02_sql_relacional as lab02

    print("=== LAB 02: SQLite relacional, JOIN, paginación y EXPLAIN QUERY PLAN ===")
    conn = sqlite3.connect(":memory:")
    try:
        lab02.init_db(conn)
        author_id = lab02.add_author(conn, "Miguel Ángel Asturias")
        lab02.add_book(conn, "El Señor Presidente", 1946, author_id)
        lab02.add_book(conn, "Hombres de Maíz", 1949, author_id)

        try:
            lab02.add_book(conn, "Libro huérfano", 2020, 9999)
            print("  Llave foránea: PENDIENTE (SQLite permitió un author_id inexistente)")
        except sqlite3.IntegrityError:
            print("  Llave foránea: OK (SQLite rechazó el author_id inexistente)")

        joined = lab02.list_books_with_authors(conn)
        print(f"  Resultado de INNER JOIN: {joined}")

        page = lab02.list_books_page(conn, limit=1, offset=1)
        print(f"  Resultado de paginación (limit=1, offset=1): {page}")

        plan = lab02.explain_books_by_author(conn, author_id)
        print("  Plan de consulta para WHERE author_id = ?:")
        print(format_query_plan(plan))
    except Exception as exc:
        print(f"  Error al inspeccionar Lab 02: {type(exc).__name__}: {exc}")
    finally:
        conn.close()
    print()


def _inspect_lab03() -> None:
    from fastapi.testclient import TestClient

    import lab03_di_jwt_y_carrera as lab03

    print("=== LAB 03: Depends, JWT en Base64Url y concurrencia con Barrier(5) ===")
    try:
        member_token = lab03.create_access_token("ana", "member")
        librarian_token = lab03.create_access_token("carlos", "librarian")
        print(f"  Token de ejemplo (member): {member_token[:36]}...")
        try:
            decoded = lab03.decode_jwt_payload_unverified(member_token)
            print(f"  Payload decodificado sin clave secreta: {decoded}")
        except Exception as exc:
            print(f"  Decodificación Base64Url pendiente: {type(exc).__name__}: {exc}")

        app = lab03.create_app()
        client = TestClient(app)
        res_no_token = client.post("/admin/rooms", json={"code": "sala-b", "name": "Sala B"})
        res_member = client.post(
            "/admin/rooms",
            json={"code": "sala-b", "name": "Sala B"},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        res_librarian = client.post(
            "/admin/rooms",
            json={"code": "sala-b", "name": "Sala B"},
            headers={"Authorization": f"Bearer {librarian_token}"},
        )
        print(
            f"  POST /admin/rooms -> sin token: {res_no_token.status_code}, "
            f"rol member: {res_member.status_code}, rol librarian: {res_librarian.status_code}"
        )

        service = lab03.RoomReservationService()
        successes, stored = run_concurrent_bookings(service, "sala-a", threads=5)
        status_msg = (
            "OK (Lock protegió la reserva)"
            if successes == 1 and stored == 1
            else "PENDIENTE (condición de carrera: varios hilos reservaron la misma sala)"
        )
        print(
            f"  Concurrencia Barrier(5) sobre 'sala-a': "
            f"{successes} confirmaciones, {stored} registros -> {status_msg}"
        )
    except Exception as exc:
        print(f"  Error al inspeccionar Lab 03: {type(exc).__name__}: {exc}")
    print()


def run_inspect() -> int:
    """Ejecuta la inspección en vivo de los 3 ejercicios sin detenerse por errores."""
    warnings.filterwarnings(
        "ignore",
        message="Using `httpx` with `starlette.testclient` is deprecated",
    )
    _inspect_lab01()
    _inspect_lab02()
    _inspect_lab03()
    return 0


def run_check() -> int:
    """Ejecuta la suite de 12 pruebas deterministas con pytest."""
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--tb=short", "tests/test_onramp.py"],
        check=False,
    )
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada del comando `onramp`."""
    parser = argparse.ArgumentParser(
        prog="onramp",
        description="Inspector y verificador de ejercicios de Backend Onramp.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("inspect", help="Muestra en vivo respuestas HTTP, SQL y concurrencia.")
    subparsers.add_parser("check", help="Corre las 12 pruebas para verificar tus avances.")

    args = parser.parse_args(argv)
    if args.command == "inspect":
        return run_inspect()
    if args.command == "check":
        return run_check()
    return 1


if __name__ == "__main__":
    sys.exit(main())
