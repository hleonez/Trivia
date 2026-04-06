"""Result screen after a game."""

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ResultWindow(QWidget):
    def __init__(self, player_name: str, score: int, new_record: bool, admin_window: QWidget) -> None:
        super().__init__()
        self._admin = admin_window
        self.setWindowTitle("Quiz — Resultado")
        self.resize(420, 220)

        msg = (
            "New record achieved"
            if new_record
            else "You did not beat the current record"
        )

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Jugador: {player_name}"))
        layout.addWidget(QLabel(f"Puntaje final: {score}"))
        layout.addWidget(QLabel(msg))

        btn = QPushButton("Volver al panel de administración")
        btn.clicked.connect(self._back)
        layout.addWidget(btn)

    def _back(self) -> None:
        self._admin.show()
        self._admin.refresh_display()
        self.close()
