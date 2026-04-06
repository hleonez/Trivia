"""
Quiz desktop app entry point: SQLite + PySide6 (MVC).
Run from this folder:  python main.py
"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from database.db import DatabaseManager
from views.login import LoginWindow


def main() -> None:
    app = QApplication(sys.argv)

    db = DatabaseManager()
    db.connect()
    db.create_tables()

    window = LoginWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
