"""Pantalla inicial: título del juego, jugar sin login, acceso a administración."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.db import DatabaseManager
from views.admin import AdminWindow
from views.game import GameWindow
from views.leaderboard import LeaderboardDialog
from views.login import AdminLoginDialog
from views.visual_fx import CRTOverlay, TelemetryPulse, fade_in


class MenuWindow(QWidget):
    def __init__(self, db: DatabaseManager) -> None:
        super().__init__()
        self._db = db
        self.setWindowTitle("Quiz — Menú")
        self.setObjectName("rootFrame")
        self.resize(920, 640)
        self.setMinimumSize(860, 600)

        title = QLabel("[ QUIZ / TELEMETRY ]")
        title.setProperty("menuTitle", "true")

        subtitle = QLabel("UNIT // SOFTWARE ENGINEERING // REV 2.6")
        subtitle.setProperty("menuSubtitle", "true")

        marker = QLabel("STATUS: READY +++")
        marker.setProperty("status_green", "true")
        self._marker_pulse = TelemetryPulse(marker, min_opacity=0.72, max_opacity=1.0)
        self._marker_pulse.start()

        btn_play = QPushButton(">>> INICIAR MISION")
        btn_play.setProperty("accent", "true")
        btn_play.clicked.connect(self._open_game)
        btn_play.setMinimumWidth(260)

        center = QVBoxLayout()
        center.addStretch(1)
        center.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)
        btn_leaderboard = QPushButton("[ HISTORIAL DE OPERADORES ]")
        btn_leaderboard.clicked.connect(self._open_leaderboard)
        btn_leaderboard.setMinimumWidth(260)

        center.addWidget(marker, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addSpacing(30)
        center.addWidget(btn_play, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addSpacing(10)
        center.addWidget(btn_leaderboard, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addStretch(2)

        btn_admin = QPushButton("[ ADMIN / ACCESS ]")
        btn_admin.clicked.connect(self._open_admin_login)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_admin)

        layout = QVBoxLayout(self)
        layout.addLayout(center)
        layout.addLayout(bottom)
        self._crt_overlay = CRTOverlay(self)
        self._intro_anim = None

    def showEvent(self, event: QShowEvent) -> None:
        self._intro_anim = fade_in(self, 220)
        super().showEvent(event)

    def refresh_display(self) -> None:
        """Misma interfaz que AdminWindow para la pantalla de resultado."""
        pass

    def _open_game(self) -> None:
        self._game = GameWindow(self._db, self, result_back_label="Volver al menú")
        self._game.show()
        self.hide()

    def _open_admin_login(self) -> None:
        dlg = AdminLoginDialog(self._db, self)
        if dlg.exec() != QDialog.Accepted:
            return
        self._admin = AdminWindow(self._db, self)
        self._admin.show()
        self.hide()

    def _open_leaderboard(self) -> None:
        dlg = LeaderboardDialog(self._db, self)
        dlg.exec()
