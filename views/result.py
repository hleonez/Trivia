"""Result screen after a game."""

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ResultWindow(QWidget):
    def __init__(
        self,
        player_name: str,
        score: int,
        new_record: bool,
        return_to: QWidget,
        *,
        back_button_text: str = "Volver",
    ) -> None:
        super().__init__()
        self._return_to = return_to
        self.setWindowTitle("Quiz — Resultado")
        self.resize(420, 220)

        msg = (
            "New record achieved"
            if new_record
            else "You did not beat the current record"
        )

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Jugador: {player_name}"))
        
        lbl_score = QLabel(f"Puntaje final: {score}")
        lbl_score.setProperty("heading", "true")
        layout.addWidget(lbl_score)
        
        layout.addWidget(QLabel(msg))

        btn = QPushButton(back_button_text)
        btn.setProperty("accent", "true")
        btn.clicked.connect(self._back)
        layout.addWidget(btn)

    def _back(self) -> None:
        self._return_to.show()
        refresh = getattr(self._return_to, "refresh_display", None)
        if callable(refresh):
            refresh()
        self.close()
