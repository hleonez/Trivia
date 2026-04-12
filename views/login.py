"""Diálogo de acceso de administrador (solo para el panel de administración)."""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from controllers.auth_controller import AuthController


class AdminLoginDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._auth = AuthController()
        self.setWindowTitle("Quiz — Acceso administrador")
        self.resize(400, 140)

        self._user = QLineEdit()
        self._user.setPlaceholderText("Usuario")
        self._password = QLineEdit()
        self._password.setPlaceholderText("Contraseña")
        self._password.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Usuario:", self._user)
        form.addRow("Contraseña:", self._password)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._user.returnPressed.connect(self._try_accept)
        self._password.returnPressed.connect(self._try_accept)

    def _try_accept(self) -> None:
        u = self._user.text()
        p = self._password.text()
        if self._auth.validate(u, p):
            self.accept()
        else:
            QMessageBox.warning(self, "Acceso denegado", "Usuario o contraseña incorrectos.")
