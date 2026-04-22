"""Admin panel: list/edit preguntas and launch game."""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QShowEvent
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
from views.visual_fx import CRTOverlay, TelemetryPulse, fade_in


class PreguntaFormDialog(QDialog):
    """Modal form for create/update (no business logic)."""

    def __init__(self, parent: QWidget | None, title: str, pregunta: Pregunta | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setObjectName("rootFrame")
        self.resize(760, 520)
        self.setMinimumSize(700, 480)

        self._enunciado = QLineEdit()
        self._a = QLineEdit()
        self._b = QLineEdit()
        self._c = QLineEdit()
        self._d = QLineEdit()
        self._correcta = QLineEdit()
        self._correcta.setMaxLength(1)
        self._correcta.setPlaceholderText("A / B / C / D")

        form = QFormLayout()
        form.addRow("ENUNCIADO:", self._enunciado)
        form.addRow("OPCION A:", self._a)
        form.addRow("OPCION B:", self._b)
        form.addRow("OPCION C:", self._c)
        form.addRow("OPCION D:", self._d)
        form.addRow("RESPUESTA:", self._correcta)

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
    def __init__(self, db: DatabaseManager, menu: QWidget) -> None:
        super().__init__()
        self._db = db
        self._menu = menu
        self._controller = PreguntaController(db)
        self._juego_preview = JuegoController(db)
        self.setWindowTitle("Quiz — Administración de preguntas")
        self.setObjectName("rootFrame")
        self.resize(1320, 860)
        self.setMinimumSize(1220, 760)

        self._record_label = QLabel()
        self._record_label.setProperty("telemetry", "true")
        self._record_pulse = TelemetryPulse(self._record_label, min_opacity=0.72, max_opacity=1.0)
        self._record_pulse.start()
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["ID", "ENUNCIADO", "RESP", "OPCIONES // RESUMEN"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        title = QLabel("[ PANEL DE TELEMETRÍA ADMIN ]")
        title.setProperty("telemetry", "true")

        btn_menu = QPushButton("<<< MENU")
        btn_menu.clicked.connect(self._back_to_menu)

        btn_add = QPushButton("[ + ] AGREGAR")
        btn_edit = QPushButton("[ / ] EDITAR")
        btn_del = QPushButton("[ X ] ELIMINAR")
        btn_game = QPushButton(">>> IR AL JUEGO")
        btn_game.setProperty("accent", "true")

        btn_add.clicked.connect(self._on_add)
        btn_edit.clicked.connect(self._on_edit)
        btn_del.clicked.connect(self._on_delete)
        btn_game.clicked.connect(self._on_game)

        row = QHBoxLayout()
        row.addWidget(btn_menu)
        row.addWidget(btn_add)
        row.addWidget(btn_edit)
        row.addWidget(btn_del)
        row.addStretch()
        row.addWidget(btn_game)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self._record_label)
        layout.addWidget(self._table)
        layout.addLayout(row)
        self._crt_overlay = CRTOverlay(self)
        self._intro_anim = None

        self._refresh_table()
        self._refresh_record_label()

    def showEvent(self, event: QShowEvent) -> None:
        self._intro_anim = fade_in(self, 250)
        super().showEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._menu.show()
        super().closeEvent(event)

    def _back_to_menu(self) -> None:
        self._menu.show()
        self.close()

    def refresh_display(self) -> None:
        """Called when returning from the game so labels and table stay in sync."""
        self._refresh_table()

    def _refresh_record_label(self) -> None:
        rec = self._juego_preview.get_record_info()
        max_pts, holder = rec
        if holder is None:
            self._record_label.setText("[ RÉCORD ]: --- // SIN PARTIDAS")
        else:
            self._record_label.setText(f"[ RECORD ]: {max_pts} PTS // {holder}")

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
            self._table.setRowHidden(row, True)

        self._refresh_record_label()
        self._animate_table_rows()

    def _animate_table_rows(self) -> None:
        for row in range(self._table.rowCount()):
            delay = min(18 * row, 300)
            QTimer.singleShot(delay, lambda r=row: self._table.setRowHidden(r, False))

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
        QMessageBox.information(self, "Guardado", "Pregunta guardada exitosamente.")
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
        QMessageBox.information(self, "Guardado", "Pregunta guardada exitosamente.")
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
        self.hide()
        self._game = GameWindow(self._db, self, result_back_label="Volver al panel de administración")
        self._game.show()
