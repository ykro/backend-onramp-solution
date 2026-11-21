"""Utilidades para mostrar HTTP crudo, EXPLAIN QUERY PLAN y concurrencia con Barrier(5)."""

import threading
from typing import Protocol


class ReservationServiceProtocol(Protocol):
    """Interfaz mínima para ejecutar reservas concurrentes."""

    def reserve(self, room_code: str, user_id: str, delay_seconds: float = 0.01) -> bool: ...

    def reservation_count(self, room_code: str) -> int: ...


def format_http_exchange(
    method: str,
    path: str,
    status_code: int,
    content_type: str | None,
    body: bytes,
) -> str:
    """Formatea una petición y respuesta HTTP cruda para lectura en consola."""
    body_text = "<cuerpo vacío>" if not body else body.decode("utf-8", errors="replace")
    header_line = f"Content-Type: {content_type}" if content_type else "Content-Type: <ninguno>"
    return (
        f"  > {method} {path} HTTP/1.1\n"
        f"  < HTTP/1.1 {status_code}\n"
        f"  < {header_line}\n"
        f"  < Cuerpo: {body_text}"
    )


def format_query_plan(plan_lines: list[str]) -> str:
    """Formatea la salida de EXPLAIN QUERY PLAN e indica si usa índice o barrido completo."""
    if not plan_lines:
        return "  (sin plan de consulta)"
    joined = " | ".join(plan_lines)
    if "SEARCH" in joined and "USING INDEX" in joined:
        diagnosis = "OK (usa índice: SEARCH)"
    elif "SCAN" in joined:
        diagnosis = "PENDIENTE (recorre toda la tabla: SCAN)"
    else:
        diagnosis = "REVISAR"
    lines = "\n".join(f"  - {line}" for line in plan_lines)
    return f"{lines}\n  Diagnóstico: {diagnosis}"


def run_concurrent_bookings(
    service: ReservationServiceProtocol,
    room_code: str,
    threads: int = 5,
    delay_seconds: float = 0.01,
) -> tuple[int, int]:
    """Lanza varios hilos sincronizados con Barrier para intentar reservar la misma sala."""
    barrier = threading.Barrier(threads)
    results: list[bool] = [False] * threads

    def worker(index: int) -> None:
        barrier.wait()
        results[index] = service.reserve(
            room_code=room_code,
            user_id=f"user-{index}",
            delay_seconds=delay_seconds,
        )

    workers = [threading.Thread(target=worker, args=(i,)) for i in range(threads)]
    for thread in workers:
        thread.start()
    for thread in workers:
        thread.join()

    successes = sum(1 for item in results if item)
    stored = service.reservation_count(room_code)
    return successes, stored
