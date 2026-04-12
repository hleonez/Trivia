"""Admin panel: list/edit preguntas and launch game."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controllers.juego_controller import JuegoController
from controllers.pregunta_controller import PreguntaController
from database.db import DatabaseManager
from models.pregunta import Pregunta
from views.game import GameWindow


class PreguntaFormDialog(QDialog):
    """Modal form for create/update (no business logic)."""

    def __init__(self, parent: QWidget | None, title: str, pregunta: Pregunta | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 360)

        self._enunciado = QLineEdit()
        self._a = QLineEdit()
        self._b = QLineEdit()
        self._c = QLineEdit()
        self._d = QLineEdit()
        self._correcta = QLineEdit()
        self._correcta.setMaxLength(1)
        self._correcta.setPlaceholderText("A, B, C o D")

        form = QFormLayout()
        form.addRow("Enunciado:", self._enunciado)
        form.addRow("Opción A:", self._a)
        form.addRow("Opción B:", self._b)
        form.addRow("Opción C:", self._c)
        form.addRow("Opción D:", self._d)
        form.addRow("Respuesta correcta:", self._correcta)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if pregunta is not None:
            self._enunciado.setText(pregunta.enunciado)
            self._a.setText(pregunta.opcion_a)
            self._b.setText(pregunta.opcion_b)
            self._c.setText(pregunta.opcion_c)
            self._d.setText(pregunta.opcion_d)
            self._correcta.setText(pregunta.respuesta_correcta)

    def values(self) -> tuple[str, str, str, str, str, str]:
        return (
            self._enunciado.text(),
            self._a.text(),
            self._b.text(),
            self._c.text(),
            self._d.text(),
            self._correcta.text(),
        )


class AdminWindow(QWidget):
    def __init__(self, db: DatabaseManager) -> None:
        super().__init__()
        self._db = db
        self._controller = PreguntaController(db)
        self._juego_preview = JuegoController(db)
        self.setWindowTitle("Quiz — Administración de preguntas")
        self.resize(900, 480)

        self._record_label = QLabel()
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["ID", "Enunciado", "Respuesta", "Opciones (resumen)"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btn_add = QPushButton("Agregar")
        btn_edit = QPushButton("Editar")
        btn_del = QPushButton("Eliminar")
        btn_game = QPushButton("Ir al juego")
        btn_game.setProperty("accent", "true")

        btn_add.clicked.connect(self._on_add)
        btn_edit.clicked.connect(self._on_edit)
        btn_del.clicked.connect(self._on_delete)
        btn_game.clicked.connect(self._on_game)

        row = QHBoxLayout()
        row.addWidget(btn_add)
        row.addWidget(btn_edit)
        row.addWidget(btn_del)
        row.addStretch()
        row.addWidget(btn_game)

        layout = QVBoxLayout(self)
        layout.addWidget(self._record_label)
        layout.addWidget(self._table)
        layout.addLayout(row)

        self._refresh_table()
        self._refresh_record_label()

    def refresh_display(self) -> None:
        """Called when returning from the game so labels and table stay in sync."""
        self._refresh_table()

    def _refresh_record_label(self) -> None:
        rec = self._juego_preview.get_record_info()
        max_pts, holder = rec
        if holder is None:
            self._record_label.setText("Récord actual: — (aún no hay partidas guardadas).")
        else:
            self._record_label.setText(f"Récord actual: {max_pts} puntos ({holder}).")

    def _refresh_table(self) -> None:
        items = self._controller.list_questions()
        self._table.setRowCount(len(items))
        for row, p in enumerate(items):
            id_item = QTableWidgetItem(str(p.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 0, id_item)

            enun = QTableWidgetItem(p.enunciado[:120] + ("…" if len(p.enunciado) > 120 else ""))
            enun.setFlags(enun.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 1, enun)

            rc = QTableWidgetItem(p.respuesta_correcta)
            rc.setFlags(rc.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 2, rc)

            summary = f"A: {p.opcion_a[:40]}… | B: {p.opcion_b[:40]}…" if len(p.opcion_a) > 40 else f"A: {p.opcion_a} | B: {p.opcion_b} | …"
            sm = QTableWidgetItem(summary)
            sm.setFlags(sm.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 3, sm)

        self._refresh_record_label()

    def _selected_id(self) -> int | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        if item is None:
            return None
        return int(item.text())

    def _find_pregunta(self, pid: int) -> Pregunta | None:
        for p in self._controller.list_questions():
            if p.id == pid:
                return p
        return None

    def _on_add(self) -> None:
        dlg = PreguntaFormDialog(self, "Nueva pregunta")
        if dlg.exec() != QDialog.Accepted:
            return
        en, a, b, c, d, r = dlg.values()
        ok, msg = self._controller.create_question(en, a, b, c, d, r)
        if not ok:
            QMessageBox.warning(self, "Validación", msg)
            return
        self._refresh_table()

    def _on_edit(self) -> None:
        pid = self._selected_id()
        if pid is None:
            QMessageBox.information(self, "Editar", "Seleccione una fila.")
            return
        p = self._find_pregunta(pid)
        if p is None:
            return
        dlg = PreguntaFormDialog(self, "Editar pregunta", p)
        if dlg.exec() != QDialog.Accepted:
            return
        en, a, b, c, d, r = dlg.values()
        ok, msg = self._controller.update_question(pid, en, a, b, c, d, r)
        if not ok:
            QMessageBox.warning(self, "Validación", msg)
            return
        self._refresh_table()

    def _on_delete(self) -> None:
        pid = self._selected_id()
        if pid is None:
            QMessageBox.information(self, "Eliminar", "Seleccione una fila.")
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "¿Eliminar esta pregunta?",
        )
        if confirm != QMessageBox.Yes:
            return
        self._controller.delete_question(pid)
        self._refresh_table()

    def _on_game(self) -> None:
        self._game = GameWindow(self._db, self)
        self._game.show()
