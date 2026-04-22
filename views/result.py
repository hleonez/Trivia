"""Result screen after a game."""

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from database.db import DatabaseManager
from views.visual_fx import CRTOverlay, TelemetryPulse, fade_in


class ResultWindow(QWidget):
    def __init__(
        self,
        player_name: str,
        score: int,
        new_record: bool,
        db: DatabaseManager,
        return_to: QWidget,
        *,
        back_button_text: str = "Volver",
        num_preguntas: int = 0,
    ) -> None:
        super().__init__()
        self._db = db
        self._player_name = player_name
        self._num_preguntas = num_preguntas
        self._return_to = return_to
        self.setWindowTitle("Quiz — Resultado")
        self.setObjectName("rootFrame")
        self.resize(760, 420)
        self.setMinimumSize(700, 380)

        msg = (
            "Nuevo récord logrado"
            if new_record
            else "No superaste el récord actual"
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

        btn_back = QPushButton(back_button_text)
        btn_back.setProperty("accent", "true")
        btn_back.clicked.connect(self._back)

        btn_new_game = QPushButton("JUGAR DE NUEVO")
        btn_new_game.clicked.connect(self._new_game)

        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_back)
        button_layout.addWidget(btn_new_game)
        layout.addLayout(button_layout)
        
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

    def _new_game(self) -> None:
        from views.game import GameWindow
        game_window = GameWindow(
            self._db, self._return_to, 
            result_back_label="Volver al menú",
            player_name=self._player_name
        )
        game_window._name.setText(self._player_name)
        game_window._count.setCurrentIndex(game_window._count.findData(self._num_preguntas))
        self.close()
        game_window.show()
