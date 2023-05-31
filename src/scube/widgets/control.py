import sys

from PySide6 import QtCore, QtWidgets
from __feature__ import snake_case, true_property


#TODO: add back and reset functionality
class ControlWidget(QtWidgets.QWidget):
    start_clicked = QtCore.Signal()
    stop_clicked = QtCore.Signal()
    next_clicked = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QtWidgets.QHBoxLayout(self)
        
        self._start_button = QtWidgets.QPushButton('Start')
        self._start_button.enabled = False
        self._start_button.clicked.connect(self.start_clicked)
        self._layout.add_widget(self._start_button)
        
        self._stop_button = QtWidgets.QPushButton('Stop')
        self._stop_button.enabled = False
        self._stop_button.clicked.connect(self.stop_clicked)
        self._layout.add_widget(self._stop_button)

        self._next_button = QtWidgets.QPushButton('Beenden')
        self._next_button.enabled = False
        self._next_button.clicked.connect(self.next_clicked)
        self._layout.add_widget(self._next_button)

        self._layout.add_stretch(1)

        self._is_running = False
        self._has_next_question = False
        self._is_init = False

    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value: bool):
        self._is_running = value
        self._check()

    @property
    def has_next_question(self):
        return self._has_next_question

    @has_next_question.setter
    def has_next_question(self, value: bool):
        self._has_next_question = value
        self._check()

    @property
    def is_init(self):
        return self._is_init

    @is_init.setter
    def is_init(self, value: bool):
        self._is_init = value
        self._check()

    def _check(self):
        if self._is_running:
            if self._is_init:
                self._start_button.enabled = False
            self._stop_button.enabled = True
        else:
            if self._is_init:
                self._start_button.enabled = True
            self._stop_button.enabled = False
        if self._has_next_question:
            self._next_button.text = 'Vorwärts'
            if self._is_init:
                self._next_button.enabled = True
            else:
                self._next_button.enabled = False
        else:
            self._next_button.text = 'Beenden'
            if self._is_init:
                self._next_button.enabled = True
            else:
                self._next_button.enabled = False

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    widget = ControlWidget()
    widget.is_init = True
    widget.has_next_question = True
    widget.show()
    sys.exit(app.exec())
