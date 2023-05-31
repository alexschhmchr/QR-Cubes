
from enum import Enum
import logging
import sys
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from __feature__ import snake_case, true_property

from scube.voting.questions import QuestionType, Question, SpecificQuestion, NQuestion, NSpecificQuestion
from scube.voting import marker, votename_to_type, VoteType
from scube.survey import DLRSurvey, QuestionManager
from scube.aruco import MarkerDetect, MarkerCam
from scube.widgets import MainWidget, SideBar, WebCamSelect
from scube import widgets

fh = logging.FileHandler('log.txt')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
                    level=logging.DEBUG, handlers=[fh, ch])
logger = logging.getLogger(__name__)
logger.debug('App start.')


class MainWidget2(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        # self._app = App()
        self._survey = DLRSurvey()
        self._cam = MarkerCam()
        self._layout = QtWidgets.QHBoxLayout(self)
        self._main_layout = QtWidgets.QVBoxLayout()
        self._camera_widget = widgets.CameraWidget()
        self._control_widget = widgets.ControlWidget()
        self._main_layout.add_widget(self._camera_widget)
        self._main_layout.add_widget(self._control_widget)
        self._main_layout.set_stretch_factor(self._camera_widget, 1)
        self._layout.add_layout(self._main_layout)
        self._layout.set_stretch_factor(self._main_layout, 1)
        self._side_layout = QtWidgets.QVBoxLayout()
        # self._cam_opt_widget = widgets.CameraOptionWidget(self._app.cameras)
        
        # self._question_manager = QuestionManager()
        cameras = [widgets.Camera(d.id, d.description) for d in QtMultimedia.QMediaDevices.video_inputs]
        self._cam_opt_widget = widgets.CameraOptionWidget(cameras)
        self._survey_info_widget = widgets.SurveyInfoWidget()
        q_names = [q.name for q in self._survey.questions]
        self._questions_widget = widgets.QuestionsWidget(q_names)
        self._side_layout.add_widget(self._cam_opt_widget)
        self._side_layout.add_widget(self._survey_info_widget)
        self._side_layout.add_widget(self._questions_widget)
        self._layout.add_layout(self._side_layout)
        # self._layout.set_stretch_factor(self._side_layout, 0)
        self._cam.frame_received.connect(self._survey.process_frame)
        self._survey.processed.connect(self._camera_widget.update_marker_image)
        self._cam_opt_widget.camera_changed.connect(self.change_camera)
        # self._questions_widget.questions_changed.connect(self.on_question_changed)
        self._questions_widget.question_added.connect(self.on_question_added)
        self._questions_widget.question_removed.connect(self.on_question_removed)
        self._control_widget.is_init = True
        self._control_widget.has_next_question = True
        self._control_widget.start_clicked.connect(self.on_start)
        self._control_widget.stop_clicked.connect(self.on_stop)
        self._control_widget.next_clicked.connect(self.on_next)

        self._camera_widget.text = self._survey.get_question_text()

    @QtCore.Slot()
    def on_start(self):
        self._control_widget.is_running = True
        self._survey.start()

    @QtCore.Slot()
    def on_stop(self):
        self._control_widget.is_running = False
        self._survey.stop()

    @QtCore.Slot()
    def on_next(self):
        self._control_widget.is_running = False
        finished = self._survey.advance()
        self._camera_widget.text = self._survey.get_question_text()
        if finished:
            self._survey.save(self._survey_info_widget.get_data())
            self._control_widget.has_next_question = False

    @QtCore.Slot(QtCore.QByteArray)
    def change_camera(self, camera_id: QtCore.QByteArray):
        self._cam.set_camera_id(camera_id)

    # @QtCore.Slot()
    # def on_question_changed(self):
    #     q_names = self._questions_widget.get_questions()
    #     for name in q_names:
    #     q_dict = {q.name: q for q in self._survey.questions}
    #     q_types = [q_dict[name].type_ for name in q_names]
    #     self._survey.voting_manager.set_question_type_list(q_types)

    @QtCore.Slot(str)
    def on_question_removed(self, question_name: str):
        self._survey.delete_question_with_name(question_name)

    @QtCore.Slot(str)
    def on_question_added(self, question_name: str):
        self._survey.add_question_with_name(question_name)


def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWidget2()
    widget.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    widget = MainWidget2()
    widget.show()
    sys.exit(app.exec())