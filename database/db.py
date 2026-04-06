"""SQLite access layer (no ORM)."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class DatabaseManager:
    """Thin wrapper around sqlite3 for preguntas and jugadores."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        base = Path(__file__).resolve().parent
        self.db_path = Path(db_path) if db_path else base / "quiz.db"
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        return self._conn

    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    def create_tables(self) -> None:
        schema_file = Path(__file__).resolve().parent / "schema.sql"
        sql = schema_file.read_text(encoding="utf-8")
        self.connection.executescript(sql)
        self.connection.commit()

    def insert_pregunta(
        self,
        enunciado: str,
        opcion_a: str,
        opcion_b: str,
        opcion_c: str,
        opcion_d: str,
        respuesta_correcta: str,
    ) -> int:
        cur = self.connection.execute(
            """
            INSERT INTO preguntas (enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta),
        )
        self.connection.commit()
        return int(cur.lastrowid)

    def get_preguntas(self) -> list[sqlite3.Row]:
        cur = self.connection.execute(
            "SELECT id, enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta "
            "FROM preguntas ORDER BY id"
        )
        return list(cur.fetchall())

    def update_pregunta(
        self,
        pregunta_id: int,
        enunciado: str,
        opcion_a: str,
        opcion_b: str,
        opcion_c: str,
        opcion_d: str,
        respuesta_correcta: str,
    ) -> None:
        self.connection.execute(
            """
            UPDATE preguntas
            SET enunciado = ?, opcion_a = ?, opcion_b = ?, opcion_c = ?, opcion_d = ?, respuesta_correcta = ?
            WHERE id = ?
            """,
            (enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta, pregunta_id),
        )
        self.connection.commit()

    def delete_pregunta(self, pregunta_id: int) -> None:
        self.connection.execute("DELETE FROM preguntas WHERE id = ?", (pregunta_id,))
        self.connection.commit()

    def insert_jugador(self, nombre: str, puntaje: int) -> int:
        cur = self.connection.execute(
            "INSERT INTO jugadores (nombre, puntaje) VALUES (?, ?)",
            (nombre, puntaje),
        )
        self.connection.commit()
        return int(cur.lastrowid)

    def get_record(self) -> dict[str, Any] | None:
        """Best score (MAX puntaje) with a player row; None if no games played."""
        cur = self.connection.execute(
            """
            SELECT nombre, puntaje
            FROM jugadores
            WHERE puntaje = (SELECT MAX(puntaje) FROM jugadores)
            ORDER BY id ASC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if row is None:
            return None
        return {"nombre": row["nombre"], "puntaje": int(row["puntaje"])}
