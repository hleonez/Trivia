"""Domain model: jugador."""


class Jugador:
    def __init__(self, nombre: str, puntaje: int = 0) -> None:
        self.nombre = nombre
        self.puntaje = puntaje
