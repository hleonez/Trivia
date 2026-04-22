"""
Quiz desktop app entry point: SQLite + PySide6 (MVC).
Run from this folder:  python main.py
"""
from __future__ import annotations

import os
import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from database.db import DatabaseManager
from views.menu import MenuWindow


def main() -> None:
    app = QApplication(sys.argv)

    font = QFont("Courier New", 10)
    font.setStyleHint(QFont.Monospace)
    app.setFont(font)

    qss_path = os.path.join(os.path.dirname(__file__), "resources", "brutalist.qss")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    db = DatabaseManager()
    db.connect()
    db.create_tables()

    window = MenuWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
