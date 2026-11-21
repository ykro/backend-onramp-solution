"""Lab 03: Inyección de dependencias, JWT en Base64Url y protección contra carreras."""

import base64
import json
import threading
import time
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

JWT_SECRET = "clave-local-de-practica-32-bytes-segura"
JWT_ALGORITHM = "HS256"


class RoomCreate(BaseModel):
    """Datos de entrada para registrar una sala de estudio."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=80)


class RoomRepository:
    """Almacén en memoria para salas de estudio."""

    def __init__(self, initial_rooms: list[dict[str, str]] | None = None) -> None:
        self._rooms: list[dict[str, str]] = (
            list(initial_rooms)
            if initial_rooms is not None
            else [{"code": "sala-a", "name": "Sala A"}]
        )

    def list_rooms(self) -> list[dict[str, str]]:
        return list(self._rooms)

    def add_room(self, code: str, name: str) -> dict[str, str]:
        room = {"code": code, "name": name}
        self._rooms.append(room)
        return room


_default_repo = RoomRepository()


def get_room_repo() -> RoomRepository:
    """Dependencia por defecto que devuelve el repositorio de salas."""
    return _default_repo


def create_access_token(subject: str, role: str) -> str:
    """Firma un JWT HS256 con el usuario y su rol."""
    return jwt.encode({"sub": subject, "role": role}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_payload_unverified(token: str) -> dict[str, object]:
    """Decodifica el bloque central de un JWT usando Base64Url sin clave secreta."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("El token no tiene 3 segmentos separados por punto")
    payload_segment = parts[1]
    padding = "=" * (-len(payload_segment) % 4)
    raw_bytes = base64.urlsafe_b64decode(payload_segment + padding)
    data = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("El contenido del token no es un objeto JSON")
    return data


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el encabezado Authorization con Bearer token",
        )
    return authorization.removeprefix("Bearer ").strip()


def create_app() -> FastAPI:
    """Crea la aplicación FastAPI del Lab 03 con Depends y validación de JWT."""
    app = FastAPI(title="Biblioteca Onramp - Lab 03")

    @app.get("/rooms")
    def list_rooms(
        repo: Annotated[RoomRepository, Depends(get_room_repo)],
    ) -> list[dict[str, str]]:
        return repo.list_rooms()

    @app.post("/admin/rooms", status_code=status.HTTP_201_CREATED)
    def create_room(
        payload: RoomCreate,
        repo: Annotated[RoomRepository, Depends(get_room_repo)],
        authorization: Annotated[str | None, Header()] = None,
    ) -> dict[str, str]:
        token = _extract_bearer_token(authorization)
        try:
            claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o mal firmado",
            ) from exc

        if claims.get("role") != "librarian":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requiere rol librarian para crear salas",
            )

        return repo.add_room(code=payload.code, name=payload.name)

    return app


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
