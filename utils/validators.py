"""Validation helpers for preguntas (no UI or DB dependencies)."""

from __future__ import annotations

# Single-letter answers only
_VALID_ANSWERS = frozenset({"A", "B", "C", "D"})


def validate_pregunta_fields(
    enunciado: str,
    opcion_a: str,
    opcion_b: str,
    opcion_c: str,
    opcion_d: str,
    respuesta_correcta: str,
) -> tuple[bool, str]:
    """
    Rules:
    - No empty fields
    - Exactly four options (all non-empty strings)
    - Exactly one correct answer: must be A, B, C, or D
    """
    fields = [enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta]
    if any(s is None or not str(s).strip() for s in fields):
        return False, "Todos los campos son obligatorios."

    letter = str(respuesta_correcta).strip().upper()
    if letter not in _VALID_ANSWERS:
        return False, "La respuesta correcta debe ser A, B, C o D."

    return True, ""
