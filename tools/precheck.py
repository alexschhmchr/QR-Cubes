import argparse
import sys
from time import time
from typing import Callable

from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia, QtOpenGLWidgets
from __feature__ import snake_case, true_property

from scube.aruco import MarkerDetect, MarkerCam
from scube.widgets import CameraWidget

class InitRunnable(QtCore.QObject, QtCore.QRunnable):
    initialized = QtCore.Signal(object) # tuple[tuple[np.ndarray], np.ndarray, QtGui.QImage]

    def __init__(self, ty: type) -> None:
        QtCore.QObject.__init__(self)
        QtCore.QRunnable.__init__(self)
        self._type = ty
    
    def run(self):
        obj = self._type()
        print('init cam')
        self.initialized.emit(obj)

def init_marker_cam() -> MarkerCam:
    pass

class VideoInputThread(QtCore.QThread):
    changed = QtCore.Signal(list)


    def run(self):
        while True:
            self.sleep(2)
            inputs = QtMultimedia.QMediaDevices.video_inputs
            self.changed.emit(inputs)

class MarkerCamThread(QtCore.QThread):
    frame_received = QtCore.Signal(QtMultimedia.QVideoFrame)

    def __init__(self, default_webcam: int = 0, parent: QtCore.QObject | None=None):
        super().__init__(parent)
        # QtMultimedia.QMediaDevices.videoInputsChanged.connect(QtMultimedia.QMediaDevices, self.on_video_inputs_changed)
        # self.video_input_thread = VideoInputThread()
        # self.video_input_thread.changed.connect(self.on_video_inputs_changed)
        # self.video_input_thread.start()
        self._default_webcam = default_webcam
        self.video_sink = QtMultimedia.QVideoSink()
        self.video_sink.videoFrameChanged.connect(self.frame_received)
        self.session = QtMultimedia.QMediaCaptureSession()
        self.session.set_video_sink(self.video_sink)
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.on_timer_tick)
        # self.timer.start(2000)

    @QtCore.Slot(list)
    def on_video_inputs_changed(self, video_inputs: list[QtMultimedia.QCameraDevice]):
        print(video_inputs)

    @QtCore.Slot(QtMultimedia.QCamera.Error, str)
    def on_error(self, error, error_str):
        print(f'{error}: {error_str}')

    @QtCore.Slot()
    def on_event(self):
        print("event")

    @QtCore.Slot(bool)
    def on_active_changed(self, active):
        print(active)

    def run(self):
        self.devices = QtMultimedia.QMediaDevices.video_inputs
        self.camera = QtMultimedia.QCamera(self.devices[self._default_webcam])
        self.camera.errorOccurred.connect(self.on_error)
        self.camera.errorChanged.connect(self.on_event)
        self.camera.cameraDeviceChanged.connect(self.on_event)
        self.camera.activeChanged.connect(self.on_active_changed)
        self.session.camera = self.camera
        self.camera.start()
        self.exec()

    @property
    def camera_device(self):
        return self.camera.camera_device
    
    @camera_device.setter
    def camera_device(self, camera_device: QtMultimedia.QCameraDevice):
        self.camera.camera_device = camera_device

    def set_camera_id(self, id: QtCore.QByteArray):
        cameras = {d.id: d for d in QtMultimedia.QMediaDevices.video_inputs}
        self.camera_device = cameras[id]

class MainWidget(QtWidgets.QWidget):

    def __init__(self, default_webcam: int, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        # self._gui_thread = QtCore.QThread.current_thread()
        # self._init_cam()
        self._layout = QtWidgets.QStackedLayout(self)
        self._camera_widget = CameraWidget(self)
        self._layout.add_widget(self._camera_widget)

        # self._camera_widget.full_screen = True

        # self._marker_cam = MarkerCam()
        # self._marker_cam.frame_received.connect(self.on_image)
        self._marker_cam = MarkerCamThread(default_webcam)
        self._marker_cam.frame_received.connect(self.on_image)
        self._marker_cam.start()
        self.sema = QtCore.QSemaphore(3)
        self.questions = [
            ("Antworte mit sehr schlecht", [5]),
            ("Antworte mit Gruppe 3", [0]),
            ("Antworte mit geht so", [1, 3]),
            ("Antworte mit Gruppe 1", [2]),
        ]
        self.current_question_index = 0

    def _init_cam(self):
        pool = QtCore.QThreadPool.global_instance()
        runnable = InitRunnable(MarkerCam)
        runnable.initialized.connect(self.on_cam_init)
        pool.start(runnable)

    @QtCore.Slot(MarkerCam)
    def on_cam_init(self, marker_cam: MarkerCam):
        assert type(marker_cam) == MarkerCam
        self._marker_cam = marker_cam
        self._marker_cam.move_to_thread(QtCore.QThread.current_thread())
        self._marker_cam.frame_received.connect(self.on_image)

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def on_image(self, image: QtMultimedia.QVideoFrame):
        pool = QtCore.QThreadPool.global_instance()
        detect_task = MarkerDetect(image, self.sema)
        detect_task.result.connect(self.on_markers)
        pool.start(detect_task)

    @QtCore.Slot(QtGui.QImage, list, tuple)
    def on_markers(self, image, ids, corners):
        if self.current_question_index < len(self.questions):
            text, expected = self.questions[self.current_question_index]
            self._camera_widget.text = text
            colors = [id_to_color(id, expected) for id in ids]
        else:
            self._camera_widget.text = ""
            colors = [QtGui.QColor(0, 0, 255) for id in ids]
        
        polys = [QtGui.QPolygonF([QtCore.QPointF(x, y) for x, y in marker[0]]) for marker in corners]
        radians = [0.] * len(colors)
        marker_views = list(zip(polys, colors, radians))
        self._camera_widget.update_marker_image(image, marker_views)

    def key_press_event(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Space:
            self.current_question_index += 1
        elif event.key() == QtCore.Qt.Key_Escape:
            self.current_question_index = 0
        elif event.key() == QtCore.Qt.Key_F11:
            if self.full_screen:
                self.show_normal()
            else:
                self.show_full_screen()

def id_to_color(id: int, expected: list[int]):
    marker_id = id % 6
    if any([marker_id == e for e in expected]):
        return QtGui.QColor(0, 255, 0)
    else:
        return QtGui.QColor(255, 0, 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', type=int, default=0)
    args = parser.parse_args()
    print(args)
    app = QtWidgets.QApplication()
    widget = MainWidget(args.w)
    widget.show()
    sys.exit(app.exec())