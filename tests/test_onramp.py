"""Suite determinista de 12 pruebas para los 3 laboratorios de Backend Onramp."""

import sqlite3
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

import lab01_http_y_servidor as lab01
import lab02_sql_relacional as lab02
import lab03_di_jwt_y_carrera as lab03
from onramp_judge.helpers import run_concurrent_bookings

# --- LAB 01: HTTP, Pydantic y estado aislado (4 pruebas) ---


def test_lab01_create_and_get_book_status_and_decimal() -> None:
    client = TestClient(lab01.create_app())

    create_res = client.post("/books", json={"title": "Clean Architecture", "price": "125.50"})
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] == 1
    assert created["title"] == "Clean Architecture"
    assert Decimal(str(created["price"])) == Decimal("125.50")

    get_res = client.get("/books/1")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Clean Architecture"


def test_lab01_validation_422_extra_forbid_and_404_not_found() -> None:
    client = TestClient(lab01.create_app())

    extra_res = client.post(
        "/books",
        json={"title": "Libro con campo extra", "price": "45.00", "descuento": 10},
    )
    assert extra_res.status_code == 422

    negative_res = client.post("/books", json={"title": "Precio inválido", "price": "-5.00"})
    assert negative_res.status_code == 422

    missing_res = client.get("/books/999")
    assert missing_res.status_code == 404


def test_lab01_delete_returns_204_without_body() -> None:
    client = TestClient(lab01.create_app())

    create_res = client.post("/books", json={"title": "Refactoring", "price": "99.90"})
    assert create_res.status_code == 201
    book_id = create_res.json()["id"]

    delete_res = client.delete(f"/books/{book_id}")
    assert delete_res.status_code == 204
    assert delete_res.content == b""

    second_delete = client.delete(f"/books/{book_id}")
    assert second_delete.status_code == 404


def test_lab01_isolated_state_between_apps() -> None:
    client_a = TestClient(lab01.create_app())
    client_b = TestClient(lab01.create_app())

    create_res = client_a.post("/books", json={"title": "Solo en A", "price": "30.00"})
    assert create_res.status_code == 201

    list_b = client_b.get("/books")
    assert list_b.status_code == 200
    assert list_b.json() == []


# --- LAB 02: SQL relacional en SQLite puro (4 pruebas) ---


def test_lab02_foreign_key_enforcement() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        lab02.init_db(conn)
        with pytest.raises(sqlite3.IntegrityError):
            lab02.add_book(conn, "Libro sin autor válido", 2025, 9999)
    finally:
        conn.close()


def test_lab02_insert_and_inner_join() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        lab02.init_db(conn)
        author_id = lab02.add_author(conn, "Miguel Ángel Asturias")
        book_id = lab02.add_book(conn, "El Señor Presidente", 1946, author_id)

        rows = lab02.list_books_with_authors(conn)
        assert len(rows) == 1
        assert rows[0] == {
            "id": book_id,
            "title": "El Señor Presidente",
            "year": 1946,
            "author_name": "Miguel Ángel Asturias",
        }
    finally:
        conn.close()


def test_lab02_pagination_with_order_limit_offset_and_params() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        lab02.init_db(conn)
        author_id = lab02.add_author(conn, "Augusto Monterroso")
        lab02.add_book(conn, "Obras completas", 1959, author_id)
        lab02.add_book(conn, "La oveja negra", 1969, author_id)
        lab02.add_book(conn, "Lo demás es silencio", 1978, author_id)

        page = lab02.list_books_page(conn, limit=2, offset=1)
        assert [row["title"] for row in page] == ["Lo demás es silencio", "Obras completas"]

        # Un texto malicioso debe tratarse como valor, nunca como instrucción SQL.
        injected = lab02.list_books_page(
            conn,
            limit=5,
            offset=0,
            title_filter="'; DROP TABLE books; --",
        )
        assert injected == []
        assert len(lab02.list_books_with_authors(conn)) == 3
    finally:
        conn.close()


def test_lab02_index_changes_query_plan_from_scan_to_search() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        lab02.init_db(conn)
        author_id = lab02.add_author(conn, "Humberto Ak'abal")
        lab02.add_book(conn, "El animalero", 1990, author_id)

        plan_lines = lab02.explain_books_by_author(conn, author_id)
        plan_text = " ".join(plan_lines)
        assert "SEARCH" in plan_text
        assert "USING INDEX" in plan_text
        assert "SCAN books" not in plan_text
    finally:
        conn.close()


# --- LAB 03: Depends, JWT y condición de carrera (4 pruebas) ---


def test_lab03_dependency_overrides_isolates_tests() -> None:
    app = lab03.create_app()
    fake_repo = lab03.RoomRepository(initial_rooms=[{"code": "sala-test", "name": "Sala Test"}])
    app.dependency_overrides[lab03.get_room_repo] = lambda: fake_repo

    client = TestClient(app)
    response = client.get("/rooms")
    assert response.status_code == 200
    assert response.json() == [{"code": "sala-test", "name": "Sala Test"}]


def test_lab03_decode_jwt_payload_without_secret() -> None:
    token = lab03.create_access_token(subject="maria", role="member")
    payload = lab03.decode_jwt_payload_unverified(token)
    assert payload["sub"] == "maria"
    assert payload["role"] == "member"


def test_lab03_auth_separates_401_and_403() -> None:
    app = lab03.create_app()
    isolated_repo = lab03.RoomRepository(initial_rooms=[])
    app.dependency_overrides[lab03.get_room_repo] = lambda: isolated_repo
    client = TestClient(app)

    no_auth = client.post("/admin/rooms", json={"code": "sala-1", "name": "Sala 1"})
    assert no_auth.status_code == 401

    bad_token = client.post(
        "/admin/rooms",
        json={"code": "sala-1", "name": "Sala 1"},
        headers={"Authorization": "Bearer token.invalido.firma"},
    )
    assert bad_token.status_code == 401

    member_token = lab03.create_access_token(subject="ana", role="member")
    forbidden = client.post(
        "/admin/rooms",
        json={"code": "sala-1", "name": "Sala 1"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert forbidden.status_code == 403

    librarian_token = lab03.create_access_token(subject="carlos", role="librarian")
    created = client.post(
        "/admin/rooms",
        json={"code": "sala-1", "name": "Sala 1"},
        headers={"Authorization": f"Bearer {librarian_token}"},
    )
    assert created.status_code == 201
    assert created.json() == {"code": "sala-1", "name": "Sala 1"}


def test_lab03_concurrent_booking_protected_with_lock() -> None:
    service = lab03.RoomReservationService()
    successes, stored = run_concurrent_bookings(service, "sala-a", threads=5, delay_seconds=0.01)
    assert successes == 1
    assert stored == 1
