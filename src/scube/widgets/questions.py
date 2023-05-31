from argparse import ArgumentError

from PySide6 import QtCore, QtWidgets, QtMultimedia
from __feature__ import snake_case, true_property

from scube.question import Question, QuestionType, QuestionManager


class QuestionsWidget(QtWidgets.QWidget):
    question_added = QtCore.Signal(str)
    question_removed = QtCore.Signal(str)
    questions_changed = QtCore.Signal()

    def __init__(self, question_manager: QuestionManager, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._questions = questions
        self._question_strs = [q.name for q in questions]

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # self.status_label = QtWidgets.QLabel("Warten...")
        # self.status_label.style_sheet = 'font-weight: bold;'
        # self.main_layout.add_widget(self.status_label)

        self.question_list = QtWidgets.QListWidget()
        # self.question_list.currentRowChanged.connect(self.check_selected_question)
        self.question_list.itemSelectionChanged.connect(self.check_selected_question)
        self.main_layout.add_widget(self.question_list, 1)

        self.question_search_bar = QtWidgets.QLineEdit()
        self.question_search_bar.set_completer(QtWidgets.QCompleter(self._question_strs))
        self.question_search_bar.textChanged.connect(self.check_question_input)
        self.main_layout.add_widget(self.question_search_bar)

        self.button_layout = QtWidgets.QHBoxLayout()

        self.main_layout.add_layout(self.button_layout)
        self.add_button = QtWidgets.QPushButton("Hinzufügen")
        self.add_button.clicked.connect(self.add_question)
        self.add_button.enabled = False
        self.button_layout.add_widget(self.add_button)

        self.delete_button = QtWidgets.QPushButton("Löschen")
        self.delete_button.clicked.connect(self.delete_question)
        self.delete_button.enabled = False
        self.button_layout.add_widget(self.delete_button)

        self.question_added.connect(self.questions_changed)
        self.question_removed.connect(self.questions_changed)

        self._current_questions: list[str] = []
        for q in questions:
            self._add_question(q) # TODO side effects on DLRSurvey?

        self._questions_manager = question_manager
        self._questions_manager.question_freeze.connect(self.on_question_freeze)

    #TODO: Validate question. Hide add button as long as question doesn't exist
    @QtCore.Slot()
    def add_question(self):
        question = self.question_search_bar.text
        self._add_question(question)

    @QtCore.Slot(int)
    def on_question_freeze(self, key: int):
        pass

    def _add_question(self, question_name: str):
        if question_name not in self._questions:
            raise InvalidQuestion(question_name)
        self.question_list.add_item(question_name)
        self._current_questions.append(question_name)
        self.question_added.emit(question_name) # TODO side effects on DLRSurvey?
        self.questions_changed.emit()

    @QtCore.Slot()
    def delete_question(self):
        index = self.question_list.current_row
        self._delete_question(index)

    def _delete_question(self, index: int):
        if index < 0:
            raise ValueError(f'"index" argument is under 0: {index}')
        self.question_list.take_item(index)
        question_name = self._current_questions[index]
        del self._current_questions[index]
        self.question_removed.emit(question_name)
        self.questions_changed.emit()

    def get_questions(self):
        return self._current_questions

    @QtCore.Slot(str)
    def check_question_input(self, question: str):
        if question in self._question_strs:
            self.add_button.enabled = True
        else:
            self.add_button.enabled = False

    @QtCore.Slot()
    def check_selected_question(self):
        index = self.question_list.current_row
        if index == -1:
            self.delete_button.enabled = False
        else:
            self.delete_button.enabled = True

    questions = QtCore.Property(list, get_questions, notify=questions_changed)

class InvalidQuestion(Exception):
    def __init__(self, question: str):
        super().__init__(f'"{question}" is an invalid question', question)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication()
    questions = [
        'Question 1',
        'Question 2',
        'Question 3',
    ]
    questions = [

    ]
    widget = QuestionsWidget(questions)
    widget.show()
    sys.exit(app.exec())
