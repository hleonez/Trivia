"""Game view: quiz session UI."""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from controllers.juego_controller import JuegoController
from database.db import DatabaseManager
from views.result import ResultWindow
from views.visual_fx import CRTOverlay, TelemetryPulse, fade_in


class GameWindow(QWidget):
    def __init__(
        self,
        db: DatabaseManager,
        return_to: QWidget,
        *,
        result_back_label: str = "Volver",
    ) -> None:
        super().__init__()
        self._db = db
        self._return_to = return_to
        self._result_back_label = result_back_label
        self._finished_to_result = False
        self._answer_locked = False
        self._juego = JuegoController(db)
        self.setWindowTitle("Quiz — Juego")
        self.setObjectName("rootFrame")
        self.resize(1080, 760)
        self.setMinimumSize(980, 700)

        # Setup screen
        self._name = QLineEdit()
        self._name.setPlaceholderText("NOMBRE DEL OPERADOR")
        self._count = QComboBox()
        for n in (10, 15, 20):
            self._count.addItem(str(n), n)
        self._record_label = QLabel()
        self._record_label.setProperty("telemetry", "true")
        self._record_pulse = TelemetryPulse(self._record_label, min_opacity=0.75, max_opacity=1.0)
        self._record_pulse.start()
        self._btn_start = QPushButton("Comenzar")
        self._btn_start.setProperty("accent", "true")
        self._btn_start.clicked.connect(self._start)

        cfg_title = QLabel("[ CONFIGURACION DE SESION ]")
        cfg_title.setProperty("telemetry", "true")

        setup_layout = QVBoxLayout()
        setup_layout.addWidget(cfg_title)
        setup_layout.addWidget(QLabel("OPERADOR:"))
        setup_layout.addWidget(self._name)
        setup_layout.addWidget(QLabel("PAQUETE DE PREGUNTAS:"))
        setup_layout.addWidget(self._count)
        setup_layout.addWidget(self._record_label)
        setup_layout.addWidget(self._btn_start)

        self._btn_back = QPushButton("/// VOLVER AL MENU")
        self._btn_back.clicked.connect(self.close)
        setup_layout.addWidget(self._btn_back)

        self._setup_page = QWidget()
        self._setup_page.setLayout(setup_layout)

        # Play screen
        self._progress = QLabel()
        self._progress.setProperty("telemetry", "true")
        self._enunciado = QLabel()
        self._enunciado.setWordWrap(True)
        btn_a = QPushButton("[A] // OPCION")
        btn_a.setProperty("answer_bg", "true")
        btn_b = QPushButton("[B] // OPCION")
        btn_b.setProperty("answer_bg", "true")
        btn_c = QPushButton("[C] // OPCION")
        btn_c.setProperty("answer_bg", "true")
        btn_d = QPushButton("[D] // OPCION")
        btn_d.setProperty("answer_bg", "true")
        btn_a.clicked.connect(lambda: self._answer("A"))
        btn_b.clicked.connect(lambda: self._answer("B"))
        btn_c.clicked.connect(lambda: self._answer("C"))
        btn_d.clicked.connect(lambda: self._answer("D"))

        grid = QGridLayout()
        grid.addWidget(btn_a, 0, 0)
        grid.addWidget(btn_b, 0, 1)
        grid.addWidget(btn_c, 1, 0)
        grid.addWidget(btn_d, 1, 1)

        self._btn_cancel = QPushButton("/// CANCELAR PARTIDA")
        self._btn_cancel.clicked.connect(self._cancel)
        self._answer_buttons = {"A": btn_a, "B": btn_b, "C": btn_c, "D": btn_d}

        play_layout = QVBoxLayout()
        play_layout.addWidget(QLabel("[ FEED DE TELEMETRIA ]"))
        play_layout.addWidget(self._progress)
        play_layout.addWidget(self._enunciado)
        play_layout.addLayout(grid)
        play_layout.addWidget(self._btn_cancel)

        self._play_page = QWidget()
        self._play_page.setLayout(play_layout)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._setup_page)
        self._stack.addWidget(self._play_page)

        outer = QVBoxLayout(self)
        outer.addWidget(self._stack)
        self._crt_overlay = CRTOverlay(self)
        self._intro_anim = None

        self._update_record_label()
        self._stack.setCurrentIndex(0)

    def showEvent(self, event: QShowEvent) -> None:
        self._intro_anim = fade_in(self, 240)
        super().showEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self._finished_to_result:
            self._return_to.show()
        super().closeEvent(event)

    def _update_record_label(self) -> None:
        pts, holder = self._juego.get_record_info()
        if holder is None:
            self._record_label.setText("[ RECORD ]: ---")
        else:
            self._record_label.setText(f"[ RECORD ]: {pts} PTS // {holder}")

    def _start(self) -> None:
        name = self._name.text()
        n = int(self._count.currentData())
        ok, msg = self._juego.start_game(name, n)
        if not ok:
            QMessageBox.warning(self, "No se puede iniciar", msg)
            return
        self._stack.setCurrentIndex(1)
        fade_in(self._play_page, 170)
        self._show_current_question()

    def _show_current_question(self) -> None:
        q = self._juego.current_question()
        if q is None:
            self._finish()
            return
        self._progress.setText(self._juego.progress_text())
        text = (
            f"{q.enunciado}\n\n"
            f"A) {q.opcion_a}\n"
            f"B) {q.opcion_b}\n"
            f"C) {q.opcion_c}\n"
            f"D) {q.opcion_d}"
        )
        self._enunciado.setText(text)

    def _answer(self, letter: str) -> None:
        if self._answer_locked:
            return
        self._answer_locked = True
        selected = self._answer_buttons[letter]
        selected.setProperty("answer_state", "hot")
        selected.style().unpolish(selected)
        selected.style().polish(selected)
        for btn in self._answer_buttons.values():
            btn.setEnabled(False)
        QTimer.singleShot(130, lambda: self._commit_answer(letter))

    def _commit_answer(self, letter: str) -> None:
        self._clear_answer_visual_state()
        has_next = self._juego.answer(letter)
        if has_next:
            self._show_current_question()
        else:
            self._finish()
        self._answer_locked = False

    def _clear_answer_visual_state(self) -> None:
        for btn in self._answer_buttons.values():
            btn.setProperty("answer_state", "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.setEnabled(True)

    def _cancel(self) -> None:
        self._juego.cancel()
        self._finish()

    def _finish(self) -> None:
        score = self._juego.final_score()
        pname = self._juego.player_name()
        new_rec = self._juego.is_new_record()
        self._juego.save_player_result()
        self._finished_to_result = True
        self._res = ResultWindow(
            pname, score, new_rec, self._return_to, back_button_text=self._result_back_label
        )
        self._res.show()
        self.close()
