"""Suite determinista de 17 pruebas para los 5 pasos independientes de Backend Onramp."""

import ast
import sqlite3
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import paso01_http_y_pydantic as paso01
import paso02_sql_relacional as paso02
import paso03_depends_y_jwt as paso03
import paso04_concurrencia as paso04
from onramp_judge.helpers import run_concurrent_bookings

STUDENT_TEST_FILE = Path(__file__).parent / "test_paso05_estudiante.py"

# --- PASO 1: Contratos HTTP/1.1, estado aislado y validación Pydantic (6 pruebas) ---


def test_paso01_create_get_and_not_found_status_codes() -> None:
    client = TestClient(paso01.create_app())

    create_res = client.post("/books", json={"title": "Clean Architecture", "price": "125.50"})
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] == 1
    assert created["title"] == "Clean Architecture"

    get_res = client.get("/books/1")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Clean Architecture"

    missing_res = client.get("/books/999")
    assert missing_res.status_code == 404


def test_paso01_delete_returns_204_without_body() -> None:
    client = TestClient(paso01.create_app())

    create_res = client.post("/books", json={"title": "Refactoring", "price": "99.90"})
    assert create_res.status_code == 201
    book_id = create_res.json()["id"]

    delete_res = client.delete(f"/books/{book_id}")
    assert delete_res.status_code == 204
    assert delete_res.content == b""

    second_delete = client.delete(f"/books/{book_id}")
    assert second_delete.status_code == 404


def test_paso01_isolated_state_between_apps() -> None:
    client_a = TestClient(paso01.create_app())
    client_b = TestClient(paso01.create_app())

    create_res = client_a.post("/books", json={"title": "Solo en A", "price": "30.00"})
    assert create_res.status_code == 201

    list_b = client_b.get("/books")
    assert list_b.status_code == 200
    assert list_b.json() == []


def test_paso01_rejects_extra_fields_with_422() -> None:
    client = TestClient(paso01.create_app())

    extra_res = client.post(
        "/books",
        json={"title": "Libro con campo extra", "price": "45.00", "descuento": 10},
    )
    assert extra_res.status_code == 422


def test_paso01_rejects_empty_title_and_invalid_price_with_422() -> None:
    client = TestClient(paso01.create_app())

    empty_title = client.post("/books", json={"title": "", "price": "25.00"})
    assert empty_title.status_code == 422

    negative_price = client.post("/books", json={"title": "Precio inválido", "price": "-5.00"})
    assert negative_price.status_code == 422

    zero_price = client.post("/books", json={"title": "Precio cero", "price": "0.00"})
    assert zero_price.status_code == 422

    too_many_decimals = client.post("/books", json={"title": "Tres decimales", "price": "12.345"})
    assert too_many_decimals.status_code == 422


def test_paso01_preserves_exact_decimal_price() -> None:
    assert paso01.BookCreate.model_fields["price"].annotation is Decimal

    client = TestClient(paso01.create_app())
    create_res = client.post("/books", json={"title": "Clean Code", "price": "125.50"})
    assert create_res.status_code == 201
    assert Decimal(str(create_res.json()["price"])) == Decimal("125.50")


# --- PASO 2: SQL relacional en SQLite puro (4 pruebas) ---


def test_paso02_foreign_key_enforcement() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        paso02.init_db(conn)
        with pytest.raises(sqlite3.IntegrityError):
            paso02.add_book(conn, "Libro sin autor válido", 2025, 9999)
    finally:
        conn.close()


def test_paso02_insert_and_inner_join() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        paso02.init_db(conn)
        author_id = paso02.add_author(conn, "Miguel Ángel Asturias")
        book_id = paso02.add_book(conn, "El Señor Presidente", 1946, author_id)

        rows = paso02.list_books_with_authors(conn)
        assert len(rows) == 1
        assert rows[0] == {
            "id": book_id,
            "title": "El Señor Presidente",
            "year": 1946,
            "author_name": "Miguel Ángel Asturias",
        }
    finally:
        conn.close()


def test_paso02_pagination_with_order_limit_offset_and_params() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        paso02.init_db(conn)
        author_id = paso02.add_author(conn, "Augusto Monterroso")
        paso02.add_book(conn, "Obras completas", 1959, author_id)
        paso02.add_book(conn, "La oveja negra", 1969, author_id)
        paso02.add_book(conn, "Lo demás es silencio", 1978, author_id)

        page = paso02.list_books_page(conn, limit=2, offset=1)
        assert [row["title"] for row in page] == ["Lo demás es silencio", "Obras completas"]

        # Un texto malicioso debe tratarse como valor, nunca como instrucción SQL.
        injected = paso02.list_books_page(
            conn,
            limit=5,
            offset=0,
            title_filter="'; DROP TABLE books; --",
        )
        assert injected == []
        assert len(paso02.list_books_with_authors(conn)) == 3
    finally:
        conn.close()


def test_paso02_index_changes_query_plan_from_scan_to_search() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        paso02.init_db(conn)
        author_id = paso02.add_author(conn, "Humberto Ak'abal")
        paso02.add_book(conn, "El animalero", 1990, author_id)

        plan_lines = paso02.explain_books_by_author(conn, author_id)
        plan_text = " ".join(plan_lines)
        assert "SEARCH" in plan_text
        assert "USING INDEX" in plan_text
        assert "SCAN books" not in plan_text
    finally:
        conn.close()


# --- PASO 3: Depends, JWT en Base64Url y 401 vs 403 (3 pruebas) ---


def test_paso03_dependency_overrides_isolates_tests() -> None:
    app = paso03.create_app()
    fake_repo = paso03.RoomRepository(initial_rooms=[{"code": "sala-test", "name": "Sala Test"}])
    app.dependency_overrides[paso03.get_room_repo] = lambda: fake_repo

    client = TestClient(app)
    response = client.get("/rooms")
    assert response.status_code == 200
    assert response.json() == [{"code": "sala-test", "name": "Sala Test"}]


def test_paso03_decode_jwt_payload_without_secret() -> None:
    token = paso03.create_access_token(subject="maria", role="member")
    payload = paso03.decode_jwt_payload_unverified(token)
    assert payload["sub"] == "maria"
    assert payload["role"] == "member"


def test_paso03_auth_separates_401_and_403() -> None:
    app = paso03.create_app()
    isolated_repo = paso03.RoomRepository(initial_rooms=[])
    app.dependency_overrides[paso03.get_room_repo] = lambda: isolated_repo
    client = TestClient(app)

    no_auth = client.post("/admin/rooms", json={"code": "sala-1", "name": "Sala 1"})
    assert no_auth.status_code == 401

    bad_token = client.post(
        "/admin/rooms",
        json={"code": "sala-1", "name": "Sala 1"},
        headers={"Authorization": "Bearer token.invalido.firma"},
    )
    assert bad_token.status_code == 401

    member_token = paso03.create_access_token(subject="ana", role="member")
    forbidden = client.post(
        "/admin/rooms",
        json={"code": "sala-1", "name": "Sala 1"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert forbidden.status_code == 403

    librarian_token = paso03.create_access_token(subject="carlos", role="librarian")
    created = client.post(
        "/admin/rooms",
        json={"code": "sala-1", "name": "Sala 1"},
        headers={"Authorization": f"Bearer {librarian_token}"},
    )
    assert created.status_code == 201
    assert created.json() == {"code": "sala-1", "name": "Sala 1"}


# --- PASO 4: Concurrencia y exclusión mutua con Lock (2 pruebas) ---


def test_paso04_concurrent_booking_protected_with_lock() -> None:
    service = paso04.RoomReservationService()
    successes, stored = run_concurrent_bookings(service, "sala-a", threads=5, delay_seconds=0.01)
    assert successes == 1
    assert stored == 1


def test_paso04_concurrent_booking_multiple_rooms_stays_consistent() -> None:
    service = paso04.RoomReservationService()
    res_a = run_concurrent_bookings(service, "sala-a", threads=5, delay_seconds=0.01)
    res_b = run_concurrent_bookings(service, "sala-b", threads=5, delay_seconds=0.01)
    assert res_a == (1, 1)
    assert res_b == (1, 1)


# --- PASO 5: Pruebas automatizadas desde cero con pytest (2 pruebas) ---


def _count_student_tests() -> int:
    tree = ast.parse(STUDENT_TEST_FILE.read_text(encoding="utf-8"))
    return sum(
        1
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


def _run_student_suite(use_buggy: bool) -> subprocess.CompletedProcess[str]:
    if not use_buggy:
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(STUDENT_TEST_FILE)],
            check=False,
            capture_output=True,
            text=True,
        )

    runner = (
        "import paso05_pruebas, pytest; "
        "paso05_pruebas.calculate_late_fee = paso05_pruebas.calculate_late_fee_buggy; "
        f"raise SystemExit(pytest.main(['-q', {str(STUDENT_TEST_FILE)!r}]))"
    )
    return subprocess.run(
        [sys.executable, "-c", runner],
        check=False,
        capture_output=True,
        text=True,
    )


def test_paso05_student_tests_pass_on_healthy_function() -> None:
    assert _count_student_tests() >= 3, (
        "Escribe al menos 3 funciones test_* en tests/test_paso05_estudiante.py."
    )
    healthy = _run_student_suite(use_buggy=False)
    assert healthy.returncode == 0, (
        "Tus pruebas en tests/test_paso05_estudiante.py deben pasar con calculate_late_fee:\n"
        f"{healthy.stdout}\n{healthy.stderr}"
    )


def test_paso05_student_tests_fail_on_buggy_function() -> None:
    healthy = _run_student_suite(use_buggy=False)
    assert healthy.returncode == 0, (
        "Primero haz que tus pruebas pasen con la función sana calculate_late_fee."
    )

    buggy = _run_student_suite(use_buggy=True)
    assert buggy.returncode == 1, (
        "Al sustituir calculate_late_fee por calculate_late_fee_buggy, al menos una prueba "
        "debe fallar (código 1) para demostrar que detecta el bug:\n"
        f"{buggy.stdout}\n{buggy.stderr}"
    )
