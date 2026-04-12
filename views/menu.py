"""Pantalla inicial: título del juego, jugar sin login, acceso a administración."""

from PySide6.QtCore import Qt
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
from views.login import AdminLoginDialog


class MenuWindow(QWidget):
    def __init__(self, db: DatabaseManager) -> None:
        super().__init__()
        self._db = db
        self.setWindowTitle("Quiz — Menú")
        self.resize(520, 380)

        title = QLabel("QUIZ")
        title.setProperty("menuTitle", "true")

        subtitle = QLabel("Ingeniería de software")
        subtitle.setProperty("menuSubtitle", "true")

        btn_play = QPushButton("Jugar")
        btn_play.setProperty("accent", "true")
        btn_play.clicked.connect(self._open_game)

        center = QVBoxLayout()
        center.addStretch(1)
        center.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addSpacing(24)
        center.addWidget(btn_play, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addStretch(2)

        btn_admin = QPushButton("Administración")
        btn_admin.clicked.connect(self._open_admin_login)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_admin)

        layout = QVBoxLayout(self)
        layout.addLayout(center)
        layout.addLayout(bottom)

    def refresh_display(self) -> None:
        """Misma interfaz que AdminWindow para la pantalla de resultado."""
        pass

    def _open_game(self) -> None:
        self._game = GameWindow(self._db, self, result_back_label="Volver al menú")
        self._game.show()
        self.hide()

    def _open_admin_login(self) -> None:
        dlg = AdminLoginDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        self._admin = AdminWindow(self._db, self)
        self._admin.show()
        self.hide()
