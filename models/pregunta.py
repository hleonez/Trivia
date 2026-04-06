"""Domain model: pregunta."""


class Pregunta:
    def __init__(
        self,
        id: int | None,
        enunciado: str,
        opcion_a: str,
        opcion_b: str,
        opcion_c: str,
        opcion_d: str,
        respuesta_correcta: str,
    ) -> None:
        self.id = id
        self.enunciado = enunciado
        self.opcion_a = opcion_a
        self.opcion_b = opcion_b
        self.opcion_c = opcion_c
        self.opcion_d = opcion_d
        self.respuesta_correcta = respuesta_correcta.upper()
