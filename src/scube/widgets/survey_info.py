
from PySide6 import QtCore, QtWidgets
from __feature__ import snake_case, true_property

class SurveyInfoWidget(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None=None):
        super().__init__(parent)
        self._layout = QtWidgets.QFormLayout(self)
        self._school_type = QtWidgets.QComboBox()
        self._school_type.add_item("Grundschule")
        self._school_type.add_item("Gesamtschule")
        self._school_type.add_item("Realschule")
        self._school_type.add_item("Gymnasium")
        self._school_type.current_index = 1
        # self._grade_box.add_item("")
        self._grade_input = QtWidgets.QLineEdit()
        self._grade_input.input_mask = '99'
        self._grade_input.clear()
        self._grade_input.text = '10'
        self._layout.add_row("Schulform:", self._school_type)
        self._layout.add_row('Klassenstufe:', self._grade_input)

    def get_data(self) -> dict[str, str]:
        school_type = self._school_type.current_text
        grade = self._grade_input.text
        return {
            "school_type": school_type,
            "grade": grade
        }

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication()
    widget = SurveyInfoWidget()
    widget.show()
    sys.exit(app.exec())