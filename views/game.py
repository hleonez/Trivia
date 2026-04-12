"""Game view: quiz session UI."""

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


class GameWindow(QWidget):
    def __init__(self, db: DatabaseManager, admin_window: QWidget) -> None:
        super().__init__()
        self._db = db
        self._admin = admin_window
        self._juego = JuegoController(db)
        self.setWindowTitle("Quiz — Juego")
        self.resize(640, 420)

        # Setup screen
        self._name = QLineEdit()
        self._name.setPlaceholderText("Nombre del jugador")
        self._count = QComboBox()
        for n in (10, 15, 20):
            self._count.addItem(str(n), n)
        self._record_label = QLabel()
        self._btn_start = QPushButton("Comenzar")
        self._btn_start.setProperty("accent", "true")
        self._btn_start.clicked.connect(self._start)

        setup_layout = QVBoxLayout()
        setup_layout.addWidget(QLabel("Nombre del jugador:"))
        setup_layout.addWidget(self._name)
        setup_layout.addWidget(QLabel("Cantidad de preguntas:"))
        setup_layout.addWidget(self._count)
        setup_layout.addWidget(self._record_label)
        setup_layout.addWidget(self._btn_start)

        self._setup_page = QWidget()
        self._setup_page.setLayout(setup_layout)

        # Play screen
        self._progress = QLabel()
        self._enunciado = QLabel()
        self._enunciado.setWordWrap(True)
        btn_a = QPushButton("A")
        btn_a.setProperty("answer_bg", "true")
        btn_b = QPushButton("B")
        btn_b.setProperty("answer_bg", "true")
        btn_c = QPushButton("C")
        btn_c.setProperty("answer_bg", "true")
        btn_d = QPushButton("D")
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

        self._btn_cancel = QPushButton("Cancelar partida")
        self._btn_cancel.clicked.connect(self._cancel)

        play_layout = QVBoxLayout()
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

        self._update_record_label()
        self._stack.setCurrentIndex(0)

    def _update_record_label(self) -> None:
        pts, holder = self._juego.get_record_info()
        if holder is None:
            self._record_label.setText("Récord actual: —")
        else:
            self._record_label.setText(f"Récord actual: {pts} ({holder})")

    def _start(self) -> None:
        name = self._name.text()
        n = int(self._count.currentData())
        ok, msg = self._juego.start_game(name, n)
        if not ok:
            QMessageBox.warning(self, "No se puede iniciar", msg)
            return
        self._stack.setCurrentIndex(1)
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
        has_next = self._juego.answer(letter)
        if has_next:
            self._show_current_question()
        else:
            self._finish()

    def _cancel(self) -> None:
        self._juego.cancel()
        self._finish()

    def _finish(self) -> None:
        score = self._juego.final_score()
        pname = self._juego.player_name()
        new_rec = self._juego.is_new_record()
        self._juego.save_player_result()
        self._res = ResultWindow(pname, score, new_rec, self._admin)
        self._res.show()
        self.close()
