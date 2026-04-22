"""Visual-only effects for tactical telemetry UX."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


def fade_in(widget: QWidget, duration: int = 220) -> QPropertyAnimation:
    """Fade a widget in without touching business state."""
    fx = widget.graphicsEffect()
    if not isinstance(fx, QGraphicsOpacityEffect):
        fx = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(fx)
    fx.setOpacity(0.0)
    anim = QPropertyAnimation(fx, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    return anim


class TelemetryPulse:
    """Subtle pulse helper for telemetry labels."""

    def __init__(self, widget: QWidget, min_opacity: float = 0.66, max_opacity: float = 1.0) -> None:
        self._fx = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(self._fx)
        self._anim = QPropertyAnimation(self._fx, b"opacity", widget)
        self._anim.setDuration(1450)
        self._anim.setStartValue(min_opacity)
        self._anim.setKeyValueAt(0.5, max_opacity)
        self._anim.setEndValue(min_opacity)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)

    def start(self) -> None:
        self._anim.start()


class CRTOverlay(QWidget):
    """Transparent overlay with scanlines and moving scan beam."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._scan_y = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())
        self.raise_()

    def _tick(self) -> None:
        self._scan_y = (self._scan_y + 3) % max(self.height(), 1)
        self.update()

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        if watched is self.parent() and event.type() == QEvent.Type.Resize:
            parent = self.parentWidget()
            if parent is not None:
                self.setGeometry(parent.rect())
                self.raise_()
        return super().eventFilter(watched, event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        h = self.height()

        scanline = QColor(0, 0, 0, 28)
        for y in range(0, h, 4):
            painter.fillRect(0, y, w, 1, scanline)

        noise = QColor(255, 255, 255, 4)
        for y in range(1, h, 22):
            painter.fillRect(0, y, w, 1, noise)

        beam = QColor(230, 25, 25, 24)
        painter.fillRect(0, self._scan_y, w, 2, beam)
        painter.end()
