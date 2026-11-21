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


def _inspect_paso01() -> None:
    from fastapi.testclient import TestClient

    import paso01_http_y_pydantic as paso01

    print("=== PASO 1: Contratos HTTP/1.1 (201, 204, 404), estado aislado y Pydantic ===")
    try:
        app_a = paso01.create_app()
        app_b = paso01.create_app()
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

        res_negative = client_a.post("/books", json={"title": "", "price": "-5.00"})
        print(
            format_http_exchange(
                "POST",
                "/books (título vacío y precio negativo)",
                res_negative.status_code,
                res_negative.headers.get("content-type"),
                res_negative.content,
            )
        )

        price_type = paso01.BookCreate.model_fields["price"].annotation
        print(f"  Tipo actual de BookCreate.price: {price_type}")
    except Exception as exc:
        print(f"  Error al inspeccionar Paso 1: {type(exc).__name__}: {exc}")
    print()


def _inspect_paso02() -> None:
    import paso02_sql_relacional as paso02

    print("=== PASO 2: SQLite relacional, JOIN, paginación y EXPLAIN QUERY PLAN ===")
    conn = sqlite3.connect(":memory:")
    try:
        paso02.init_db(conn)
        author_id = paso02.add_author(conn, "Miguel Ángel Asturias")
        paso02.add_book(conn, "El Señor Presidente", 1946, author_id)
        paso02.add_book(conn, "Hombres de Maíz", 1949, author_id)

        try:
            paso02.add_book(conn, "Libro huérfano", 2020, 9999)
            print("  Llave foránea: PENDIENTE (SQLite permitió un author_id inexistente)")
        except sqlite3.IntegrityError:
            print("  Llave foránea: OK (SQLite rechazó el author_id inexistente)")

        joined = paso02.list_books_with_authors(conn)
        print(f"  Resultado de INNER JOIN: {joined}")

        page = paso02.list_books_page(conn, limit=1, offset=1)
        print(f"  Resultado de paginación (limit=1, offset=1): {page}")

        plan = paso02.explain_books_by_author(conn, author_id)
        print("  Plan de consulta para WHERE author_id = ?:")
        print(format_query_plan(plan))
    except Exception as exc:
        print(f"  Error al inspeccionar Paso 2: {type(exc).__name__}: {exc}")
    finally:
        conn.close()
    print()


def _inspect_paso03() -> None:
    from fastapi.testclient import TestClient

    import paso03_depends_y_jwt as paso03

    print("=== PASO 3: Depends, dependency_overrides, JWT en Base64Url y 401 vs 403 ===")
    try:
        member_token = paso03.create_access_token("ana", "member")
        librarian_token = paso03.create_access_token("carlos", "librarian")
        print(f"  Token de ejemplo (member): {member_token[:36]}...")
        try:
            decoded = paso03.decode_jwt_payload_unverified(member_token)
            print(f"  Payload decodificado sin clave secreta: {decoded}")
        except Exception as exc:
            print(f"  Decodificación Base64Url pendiente: {type(exc).__name__}: {exc}")

        app = paso03.create_app()
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
    except Exception as exc:
        print(f"  Error al inspeccionar Paso 3: {type(exc).__name__}: {exc}")
    print()


def _inspect_paso04() -> None:
    import paso04_concurrencia as paso04

    print("=== PASO 4: Concurrencia con Barrier(5) y exclusión mutua con Lock ===")
    try:
        service = paso04.RoomReservationService()
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
        print(f"  Error al inspeccionar Paso 4: {type(exc).__name__}: {exc}")
    print()


def _inspect_paso05() -> None:
    import paso05_pruebas as paso05

    print("=== PASO 5: Pruebas automatizadas desde cero con pytest ===")
    try:
        for days in (4, 1, 0, -2):
            healthy = paso05.calculate_late_fee(days)
            buggy = paso05.calculate_late_fee_buggy(days)
            print(f"  days_late={days:>2} -> sana: {healthy:>6} | con bug: {buggy:>6}")
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests/test_paso05_estudiante.py"],
            check=False,
            capture_output=True,
            text=True,
        )
        summary = completed.stdout.strip().splitlines()
        last_line = summary[-1] if summary else "(sin salida)"
        print(f"  Estado de tests/test_paso05_estudiante.py: {last_line}")
    except Exception as exc:
        print(f"  Error al inspeccionar Paso 5: {type(exc).__name__}: {exc}")
    print()


_INSPECTORS = {
    1: _inspect_paso01,
    2: _inspect_paso02,
    3: _inspect_paso03,
    4: _inspect_paso04,
    5: _inspect_paso05,
}


def run_inspect(paso: int | None = None) -> int:
    """Ejecuta la inspección en vivo de todos los pasos o de uno específico."""
    warnings.filterwarnings(
        "ignore",
        message="Using `httpx` with `starlette.testclient` is deprecated",
    )
    if paso is not None:
        _INSPECTORS[paso]()
        return 0
    for step_number in sorted(_INSPECTORS):
        _INSPECTORS[step_number]()
    return 0


def run_check(paso: int | None = None) -> int:
    """Ejecuta las pruebas deterministas o las pruebas de un paso específico."""
    cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short", "tests/test_onramp.py"]
    if paso is not None:
        cmd.extend(["-k", f"paso0{paso}"])
    completed = subprocess.run(cmd, check=False)
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada del comando `onramp`."""
    parser = argparse.ArgumentParser(
        prog="onramp",
        description="Inspector y verificador de ejercicios de Backend Onramp.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Muestra en vivo respuestas HTTP, Pydantic, SQL, JWT, concurrencia y pruebas.",
    )
    inspect_parser.add_argument(
        "--paso",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Inspecciona únicamente un paso (1 a 5).",
    )

    check_parser = subparsers.add_parser(
        "check",
        help="Corre las pruebas deterministas para verificar tus avances.",
    )
    check_parser.add_argument(
        "--paso",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Verifica únicamente un paso (1 a 5).",
    )

    args = parser.parse_args(argv)
    if args.command == "inspect":
        return run_inspect(paso=args.paso)
    if args.command == "check":
        return run_check(paso=args.paso)
    return 1


if __name__ == "__main__":
    sys.exit(main())
