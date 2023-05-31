from dataclasses import dataclass
from PySide6 import QtCore, QtGui, QtOpenGLWidgets, QtWidgets, QtMultimedia
from __feature__ import snake_case, true_property


from .camera import CameraWidget
from .camera_options import Camera, CameraOptionWidget
from .questions import QuestionsWidget
from .control import ControlWidget
from .survey_info import SurveyInfoWidget

class WebCamSelect(QtWidgets.QWidget):
    devices: list[QtMultimedia.QCameraDevice]
    # selected = QtCore.Signal(int)
    camera_changed = QtCore.Signal(QtMultimedia.QCameraDevice)

    def __init__(self, devices: list[QtMultimedia.QCameraDevice]) -> None:
        super().__init__()
        self.devices = devices
        self.webcam_layout = QtWidgets.QHBoxLayout(self)
        self.webcam_label = QtWidgets.QLabel("Webcam Auswahl:")
        self.webcam_combobox = QtWidgets.QComboBox()
        self.webcam_combobox.add_items([device.description for device in self.devices])
        self.webcam_layout.add_widget(self.webcam_label)
        self.webcam_layout.add_widget(self.webcam_combobox)
        self.webcam_combobox.currentIndexChanged.connect(self.emit_camera)


    #TODO: handle new devices
    def set_devices(self, devices: list[QtMultimedia.QCameraDevice]):
        self.devices = devices

    # won't trigger signal
    def set_camera(self, camera: QtMultimedia.QCameraDevice):
        i = self.devices.index(camera)
        self.webcam_combobox.current_index = i

    def emit_camera(self, index: int):
        device = self.devices[index]
        print(device)
        self.camera_changed.emit(device)

    def _camera(self):
        self.webcam_combobox.current_index

    camera = QtCore.Property(QtMultimedia.QCameraDevice, _camera, notify=camera_changed)


    #TODO: handle new devices
    # def set_devices(self, devices: list[QtMultimedia.QCameraDevice]):
    #     self.devices = devices

    # won't trigger signal
    # def set_camera(self, camera: QtMultimedia.QCameraDevice):
    #     i = self.devices.index(camera)
    #     self.webcam_combobox.current_index = i

    def emit_device_id(self, index: int):
        device_id = self.device_ids[index]
        print(device_id)
        self.camera_changed.emit(device_id)

    def _camera(self):
        self.device_ids[self.webcam_combobox.current_index]

    current_device_id = QtCore.Property(QtMultimedia.QCameraDevice, _camera, notify=camera_changed)
    
    
#TODO: Remove WebCamSelect widget from here. Put in Camera Widget
class SideBar(QtWidgets.QWidget):
    camera_changed: QtCore.Signal
    question_added = QtCore.Signal()
    question_removed = QtCore.Signal()
    questions_changed = QtCore.Signal()

    def __init__(self, webcam_widget: WebCamSelect, questions: list[str], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.status_label = QtWidgets.QLabel("Warten...")
        self.status_label.style_sheet = 'font-weight: bold;'
        self.main_layout.add_widget(self.status_label)
        self.web_cam_selection = WebCamSelect(QtMultimedia.QMediaDevices.video_inputs)
        self.camera_changed = self.web_cam_selection.camera_changed
        self.main_layout.add_widget(self.web_cam_selection)
        self.survey_list = QtWidgets.QListWidget()
        self.main_layout.add_widget(self.survey_list, 1)
        self.question_search_bar = QtWidgets.QLineEdit()
        self.question_search_bar.set_completer(QtWidgets.QCompleter(questions))
        self.main_layout.add_widget(self.question_search_bar)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.add_layout(self.button_layout)
        self.add_button = QtWidgets.QPushButton("Hinzufügen")
        self.add_button.clicked.connect(self.add_question)
        self.button_layout.add_widget(self.add_button)
        self.delete_button = QtWidgets.QPushButton("Löschen")
        self.delete_button.clicked.connect(self.delete_question)
        self.button_layout.add_widget(self.delete_button)
        self._current_questions = []

    #TODO: Validate question
    @QtCore.Slot()
    def add_question(self):
        question = self.question_search_bar.text
        self._add_question(question)

    def _add_question(self, question: str):
        self.survey_list.add_item(question)
        self._current_questions.append(question)
        self.questions_changed.emit()

    @QtCore.Slot()
    def delete_question(self):
        index = self.survey_list.current_row
        self._delete_question(index)

    def _delete_question(self, index: int):
        self.survey_list.take_item(index)
        del self._current_questions[index]
        self.questions_changed.emit()

    def get_questions(self):
        return self._current_questions

    questions = QtCore.Property(list, get_questions, notify=questions_changed)


class MainWidget(QtWidgets.QWidget):
    start_clicked = QtCore.Signal()
    stop_clicked = QtCore.Signal()
    next_clicked = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        # self.question_title = QtWidgets.QLabel('...')
        # self.question_title.style_sheet = "background-color: rgba(0, 0, 0, 0.5); border-radius: 8px; color: white; font-size: 14px; font-weight: bold"
        # self.question_title.margin = 8
        # self.main_layout.add_widget(self.question_title)
        # self.camera_widget = QtWidgets.QLabel()
        # self.main_layout.add_widget(self.camera_widget, 1)

        self.camera_widget = CameraWidget()
        self.main_layout.add_widget(self.camera_widget)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.add_layout(self.button_layout)
        self.start_button = QtWidgets.QPushButton('Start')
        self.button_layout.add_widget(self.start_button)
        self.start_button.clicked.connect(self.start_clicked)
        self.stop_button = QtWidgets.QPushButton('Stop')
        self.stop_button.enable = False
        self.button_layout.add_widget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_clicked)
        self.next_button = QtWidgets.QPushButton('Vorwärts')
        self.button_layout.add_widget(self.next_button)
        self.next_button.clicked.connect(self.next_clicked)
        self.button_layout.add_stretch(1)

    @QtCore.Slot()
    def start_scanning(self):
        self.start_button.enabled = False
        self.stop_button.enabled = True
        self.camera_widget.survey.start()

    @QtCore.Slot()
    def stop_scanning(self):
        self.start_button.enabled = True
        self.stop_button.enabled = False
        self.camera_widget.survey.stop()

    @QtCore.Slot()
    def next(self):
        self.start_button.enabled = True
        self.stop_button.enabled = False
        self.camera_widget.survey.advance()
