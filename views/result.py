"""Result screen after a game."""

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from views.visual_fx import CRTOverlay, TelemetryPulse, fade_in


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
        self.setObjectName("rootFrame")
        self.resize(760, 420)
        self.setMinimumSize(700, 380)

        msg = (
            "New record achieved"
            if new_record
            else "You did not beat the current record"
        )

        layout = QVBoxLayout(self)

        title = QLabel("[ RESULTADO DE MISION ]")
        title.setProperty("telemetry", "true")
        self._title_pulse = TelemetryPulse(title, min_opacity=0.78, max_opacity=1.0)
        self._title_pulse.start()
        layout.addWidget(title)

        layout.addWidget(QLabel(f"OPERADOR: {player_name}"))
        
        lbl_score = QLabel(f"PUNTAJE FINAL: {score}")
        lbl_score.setProperty("heading", "true")
        layout.addWidget(lbl_score)

        status = QLabel(msg.upper())
        status.setProperty("telemetry", "true")
        layout.addWidget(status)

        btn = QPushButton(back_button_text)
        btn.setProperty("accent", "true")
        btn.clicked.connect(self._back)
        layout.addWidget(btn)
        self._crt_overlay = CRTOverlay(self)
        self._intro_anim = None

    def showEvent(self, event: QShowEvent) -> None:
        self._intro_anim = fade_in(self, 220)
        super().showEvent(event)

    def _back(self) -> None:
        self._return_to.show()
        refresh = getattr(self._return_to, "refresh_display", None)
        if callable(refresh):
            refresh()
        self.close()
