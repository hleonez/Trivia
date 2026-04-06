"""Business logic for CRUD on preguntas."""

from __future__ import annotations

import sqlite3

from database.db import DatabaseManager
from models.pregunta import Pregunta
from utils import validators


class PreguntaController:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def _enunciado_duplicado(self, enunciado: str, exclude_id: int | None = None) -> bool:
        t = enunciado.strip()
        for row in self._db.get_preguntas():
            if exclude_id is not None and int(row["id"]) == exclude_id:
                continue
            if row["enunciado"].strip() == t:
                return True
        return False

    def _row_to_pregunta(self, row: sqlite3.Row) -> Pregunta:
        return Pregunta(
            id=int(row["id"]),
            enunciado=row["enunciado"],
            opcion_a=row["opcion_a"],
            opcion_b=row["opcion_b"],
            opcion_c=row["opcion_c"],
            opcion_d=row["opcion_d"],
            respuesta_correcta=row["respuesta_correcta"],
        )

    def list_questions(self) -> list[Pregunta]:
        return [self._row_to_pregunta(r) for r in self._db.get_preguntas()]

    def create_question(
        self,
        enunciado: str,
        opcion_a: str,
        opcion_b: str,
        opcion_c: str,
        opcion_d: str,
        respuesta_correcta: str,
    ) -> tuple[bool, str]:
        ok, msg = validators.validate_pregunta_fields(
            enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta
        )
        if not ok:
            return False, msg

        if self._enunciado_duplicado(enunciado):
            return False, "Ya existe una pregunta con el mismo enunciado."

        letter = respuesta_correcta.strip().upper()
        self._db.insert_pregunta(enunciado.strip(), opcion_a.strip(), opcion_b.strip(), opcion_c.strip(), opcion_d.strip(), letter)
        return True, ""

    def update_question(
        self,
        pregunta_id: int,
        enunciado: str,
        opcion_a: str,
        opcion_b: str,
        opcion_c: str,
        opcion_d: str,
        respuesta_correcta: str,
    ) -> tuple[bool, str]:
        ok, msg = validators.validate_pregunta_fields(
            enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta
        )
        if not ok:
            return False, msg

        if self._enunciado_duplicado(enunciado, exclude_id=pregunta_id):
            return False, "Ya existe una pregunta con el mismo enunciado."

        letter = respuesta_correcta.strip().upper()
        self._db.update_pregunta(
            pregunta_id,
            enunciado.strip(),
            opcion_a.strip(),
            opcion_b.strip(),
            opcion_c.strip(),
            opcion_d.strip(),
            letter,
        )
        return True, ""

    def delete_question(self, pregunta_id: int) -> None:
        self._db.delete_pregunta(pregunta_id)
