import threading
import sys
import PySide6
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from __feature__ import snake_case, true_property
import numpy as np
import cv2

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)

print(PySide6.__version__)

# print(QtMultimedia.QMediaDevices.video_inputs)

# for i in range(len(QtMultimedia.QMediaDevices.video_inputs)):
#     video_capture = cv2.VideoCapture(i)
#     prop = video_capture.get(cv2.CAP_PROP_GUID)
#     print(prop)


class MyVideoSink(QtMultimedia.QVideoSink):

    video_frame_changed = QtCore.Signal(QtMultimedia.QVideoFrame)

    def set_video_frame(self, frame: PySide6.QtMultimedia.QVideoFrame | PySide6.QtMultimedia.QVideoFrameFormat) -> None:
        super().set_video_frame(frame)
        self.video_frame_changed.emit(frame)
        print("frame")

    def video_sink():
        print("here 1")

    def videoSink():
        print("here 2")


class MyWidget(QtWidgets.QWidget):
    layout: QtWidgets.QVBoxLayout
    label: QtWidgets.QLabel
    camera_combo_box: QtWidgets.QComboBox
    video_widget: QtMultimediaWidgets.QVideoWidget
    video_sink: QtMultimedia.QVideoSink
    graphics_view: QtWidgets.QGraphicsView
    graphics_scene: QtWidgets.QGraphicsScene
    camera: QtMultimedia.QCamera
    cameras: list[QtMultimedia.QCameraDevice]
    session: QtMultimedia.QMediaCaptureSession
    image_label: QtWidgets.QLabel
    lock: threading.Lock
    in_process: bool

    def __init__(self, cameras: list[QtMultimedia.QCameraDevice]) -> None:
        super().__init__()
        self.cameras = cameras
        self.lock = threading.Lock()
        self.in_process = False
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("Hello World")
        self.image_label = QtWidgets.QLabel()
        self.camera_combo_box = QtWidgets.QComboBox()
        for c in cameras:
            self.camera_combo_box.add_item(c.description)

        # self.image_label = QtWidgets.QLabel()
        self.video_widget = QtMultimediaWidgets.QVideoWidget()
        # self.video_graphic = QtMultimediaWidgets.QGraphicsVideoItem()
        # self.video_graphic.video_sink.videoFrameChanged.connect(
        #     self.process_frame)
        # self.video_graphic.size = QtCore.QSizeF(640, 480)
        # self.graphics_scene = QtWidgets.QGraphicsScene()
        # self.graphics_scene.add_item(self.video_graphic)
        # # self.graphics_scene.foreground_brush = QtGui.QBrush(QtGui.QColor('red'))
        # self.graphics_scene.add_polygon(QtGui.QPolygonF([
        #     QtCore.QPointF(0, 0), 
        #     QtCore.QPointF(100, 0), 
        #     QtCore.QPointF(100, 100), 
        #     QtCore.QPointF(0, 100), 
        #     QtCore.QPointF(0, 0)]), QtGui.QPen(QtGui.QColor('red')))
        # print(self.graphics_scene.scene_rect)
        # self.graphics_view = QtWidgets.QGraphicsView()
        # self.graphics_view.set_scene(self.graphics_scene)

        self.layout.add_widget(self.video_widget, 1)
        # self.layout.add_widget(self.graphics_view)
        # self.layout.add_widget(self.image_label, 1)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.camera_combo_box)

        self.session = QtMultimedia.QMediaCaptureSession()
        self.camera = QtMultimedia.QCamera(cameras[0])
        # self.video_sink = MyVideoSink()
        # self.video_sink = QtMultimedia.QVideoSink()
        # self.video_sink.videoFrameChanged.connect(self.process_frame, QtCore.Qt.DirectConnection)
        # self.video_sink.video_frame_changed.connect(self.process_frame)
        self.session.camera = self.camera
        # self.session.set_video_sink(self.video_sink)
        # self.session.video_output = self.video_graphic
        # self.session.video_output = self.video_sink
        self.session.video_output = self.video_widget
        # self.session.
        self.camera.start()
        self.camera_combo_box.currentIndexChanged.connect(self.change_camera)

    @QtCore.Slot(int)
    def change_camera(self, index: int):
        self.camera.stop()
        self.camera = QtMultimedia.QCamera(self.cameras[index])
        self.session.camera = self.camera
        self.camera.start()
        

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def process_frame(self, frame: QtMultimedia.QVideoFrame):
        # frame.map(QtMultimedia.QVideoFrame.MapMode.ReadOnly)
        # arr1 = np.asarray(frame.bits(0)).reshape(frame.height(), frame.width())
        # arr2 = np.asarray(frame.bits(1)).reshape(frame.height()//2, frame.width()//2, 2)
        # arr3 = cv2.cvtColorTwoPlane(arr1, arr2, cv2.COLOR_YUV2RGB_NV12)
        # frame.unmap()
        # corners, ids, rej = cv2.aruco.detectMarkers(arr1, aruco_dict)
        do = False
        with self.lock:
            if not self.in_process:
                do = True
                self.in_process = True
        if do:
            print("in slot")
            qimg: QtGui.QImage = frame.to_image()
            print("to imaged")
            arr1 = np.asarray(qimg.bits()).reshape(qimg.height(), qimg.width(), 4)[:,:, 1:]
            print("to arrayed")
            corners, ids, rej = cv2.aruco.detectMarkers(arr1, aruco_dict)
            print("detected marker")
            pixmap = QtGui.QPixmap.from_image(qimg)
            print("transformed pixmap")
            pixmap = pixmap.scaled_to_width(self.image_label.width)
            print("scaled pixmap")
            self.image_label.pixmap = pixmap
            print("set pixmap")
            self.image_label.update()
            with self.lock:
                self.in_process = False

                



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # cameras = QtMultimedia.QMediaDevices.videoInputs()
    widget = MyWidget(QtMultimedia.QMediaDevices.video_inputs)
    # widget.resize(800, 600)
    widget.size = QtCore.QSize(800, 600)
    widget.show()

    sys.exit(app.exec())
