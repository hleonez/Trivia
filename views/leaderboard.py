"""Diálogo de historial de operadores (Leaderboard)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

from database.db import DatabaseManager
from views.visual_fx import CRTOverlay, fade_in


class LeaderboardDialog(QDialog):
    def __init__(self, db: DatabaseManager, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self.setWindowTitle("Quiz — Historial de Operadores")
        self.setObjectName("rootFrame")
        self.resize(560, 340)
        self.setMinimumSize(520, 320)

        layout = QVBoxLayout(self)

        title = QLabel("--- TOP 5 REGISTROS ---")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(20)

        top_scores = self._db.get_top_5_scores()
        if not top_scores:
            lbl_empty = QLabel("NO DATA FOUND")
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(lbl_empty)
        else:
            for i, score in enumerate(top_scores, start=1):
                lbl_score = QLabel(f"{i}. {score['nombre'].upper()} - {score['puntaje']} PTS")
                lbl_score.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                layout.addWidget(lbl_score)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._crt_overlay = CRTOverlay(self)
        self._intro_anim = None

    def showEvent(self, event: QShowEvent) -> None:
        self._intro_anim = fade_in(self, 180)
        super().showEvent(event)
