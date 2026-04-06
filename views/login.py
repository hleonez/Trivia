"""Login view (MVC: only UI; auth via controller)."""

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controllers.auth_controller import AuthController
from database.db import DatabaseManager
from views.admin import AdminWindow


class LoginWindow(QWidget):
    def __init__(self, db: DatabaseManager) -> None:
        super().__init__()
        self._db = db
        self._auth = AuthController()
        self.setWindowTitle("Quiz — Inicio de sesión")
        self.resize(380, 160)

        self._user = QLineEdit()
        self._user.setPlaceholderText("Usuario")
        self._password = QLineEdit()
        self._password.setPlaceholderText("Contraseña")
        self._password.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Usuario:", self._user)
        form.addRow("Contraseña:", self._password)

        btn_login = QPushButton("Ingresar")
        btn_login.clicked.connect(self._try_login)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Use las credenciales de administrador (admin / admin)."))
        layout.addLayout(form)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(btn_login)
        layout.addLayout(row)

        self._user.returnPressed.connect(self._try_login)
        self._password.returnPressed.connect(self._try_login)

    def _try_login(self) -> None:
        u = self._user.text()
        p = self._password.text()
        if self._auth.validate(u, p):
            self._admin = AdminWindow(self._db)
            self._admin.show()
            self.close()
        else:
            QMessageBox.warning(self, "Acceso denegado", "Usuario o contraseña incorrectos.")
