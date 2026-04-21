"""Game flow: random questions, scoring, persistence."""

from __future__ import annotations

import random

from database.db import DatabaseManager
from models.pregunta import Pregunta


class JuegoController:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._current_index = 0
        self._score = 0
        self._player_name = ""
        self._total_questions = 0
        self._preguntas: list[Pregunta] = []

    def get_record_info(self) -> tuple[int, str | None]:
        """Maximum score and holder name (if any)."""
        rec = self._db.get_record()
        if rec is None:
            return 0, None
        return rec["puntaje"], rec["nombre"]

    def start_game(self, nombre_jugador: str, num_preguntas: int) -> tuple[bool, str]:
        nombre = nombre_jugador.strip()
        if not nombre:
            return False, "Ingrese el nombre del jugador."

        rows = self._db.get_preguntas()
        all_q = [
            Pregunta(
                id=int(r["id"]),
                enunciado=r["enunciado"],
                opcion_a=r["opcion_a"],
                opcion_b=r["opcion_b"],
                opcion_c=r["opcion_c"],
                opcion_d=r["opcion_d"],
                respuesta_correcta=r["respuesta_correcta"],
            )
            for r in rows
        ]
        if not all_q:
            return False, "No hay preguntas en la base de datos. Agregue preguntas primero."

        if num_preguntas > len(all_q):
            return False, "Cantidad de preguntas insuficientes."

        self._preguntas = random.sample(all_q, num_preguntas)
        self._current_index = 0
        self._score = 0
        self._player_name = nombre
        self._total_questions = num_preguntas
        return True, ""

    def cancel(self) -> int:
        """Stop early; marks session ended with current score."""
        self._current_index = max(self._current_index, len(self._preguntas))
        return self._score

    def current_question(self) -> Pregunta | None:
        if self._current_index >= len(self._preguntas):
            return None
        return self._preguntas[self._current_index]

    def progress_text(self) -> str:
        if self._total_questions == 0:
            return ""
        return f"Pregunta {self._current_index + 1} de {self._total_questions}  |  Aciertos: {self._score}"

    def answer(self, choice: str) -> bool:
        """
        Validate answer for current question, advance. Returns True if there is a next question.
        """
        q = self.current_question()
        if q is None:
            return False

        if choice.strip().upper() == q.respuesta_correcta:
            self._score += 1

        self._current_index += 1
        return self.current_question() is not None

    def is_finished(self) -> bool:
        return self._total_questions > 0 and self._current_index >= self._total_questions

    def final_score(self) -> int:
        return self._score

    def player_name(self) -> str:
        return self._player_name

    def save_player_result(self) -> None:
        self._db.insert_jugador(self._player_name, self._score)

    def is_new_record(self) -> bool:
        """Call before save_player_result. First score in DB counts as record; else must beat max."""
        rec = self._db.get_record()
        if rec is None:
            return True
        return self._score > int(rec["puntaje"])
