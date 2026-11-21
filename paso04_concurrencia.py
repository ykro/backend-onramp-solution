"""Paso 4: Concurrencia y exclusión mutua con `threading.Lock`."""

import threading
import time


class RoomReservationService:
    """Gestiona reservas exclusivas de salas protegiendo la sección crítica con Lock."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._reservations: dict[str, list[str]] = {}

    def reserve(self, room_code: str, user_id: str, delay_seconds: float = 0.01) -> bool:
        """Reserva una sala solo si sigue libre; devuelve True si ganó el cupo."""
        with self._lock:
            if self._reservations.get(room_code):
                return False
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            self._reservations.setdefault(room_code, []).append(user_id)
            return True

    def reservation_count(self, room_code: str) -> int:
        """Devuelve cuántas reservas quedaron registradas para la sala."""
        with self._lock:
            return len(self._reservations.get(room_code, []))
