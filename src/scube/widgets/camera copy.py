import logging
import time

from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia, QtOpenGLWidgets
from __feature__ import snake_case, true_property
import numpy as np

logger = logging.getLogger(__name__)

VALID_TIME = 1.

# tasks: 
class CameraWidget(QtOpenGLWidgets.QOpenGLWidget):
    current_image: QtGui.QImage
    current_marker_views: list[tuple[QtGui.QPolygonF, QtGui.QColor, float]]
    last_frame_time: float
    frame_time: float
    marker_times: dict[int, float]
    # survey: survey.Survey
    
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        logger.debug('Start Camera Widget initialization.')
        super().__init__(parent)
        self.minimum_size = QtCore.QSize(800, 600)
        # self.survey: survey.Survey = survey_
        self.video_sink = QtMultimedia.QVideoSink()
        # self.video_sink.videoFrameChanged.connect(self.procces_frame)

        # self.video_sink.videoFrameChanged.connect(self.survey.process_frame)        
        # self.survey.processed.connect(self.update_view4)

        self.camera = QtMultimedia.QCamera(QtMultimedia.QMediaDevices.video_inputs[0])
        self.session = QtMultimedia.QMediaCaptureSession()
        self.session.camera = self.camera
        self.session.video_output = self.video_sink
        self.camera.start()
        # self.current_image = None
        self.current_marker_views = None
        self.frame_time = None
        self.last_frame_time = None
        self.marker_times = {}
        logger.debug('Camera Widget initialized.')

    def close_event(self, event: QtGui.QCloseEvent):
        self.camera.stop()
        super().close_event(event)
    
    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def update_view(self, frame: QtMultimedia.QVideoFrame):
        self.current_image = frame.to_image()
        self.update()

    @QtCore.Slot(QtGui.QImage)
    def update_view2(self, image: QtGui.QImage):
        self.current_image = image
        self.update()

    @QtCore.Slot(tuple)
    def update_view3(self, data: tuple[tuple[np.ndarray], np.ndarray, QtGui.QImage]):
        self.current_marker_views = data
        self.update_marker_times()
        self.update()

    @QtCore.Slot(tuple)
    def update_view4(self, image: QtGui.QImage, marker_views: list[tuple[QtGui.QPolygonF, QtGui.QColor, float]]):
        self.current_image = image
        self.current_marker_views = marker_views
        # self.update_marker_times()
        self.update()

    def update_marker_times(self):
        self.frame_time = time.monotonic()
        _, ids, _ = self.current_marker_views
        # print(ids)
        if type(ids) != type(None):
            id_set = {id for id in ids.reshape(ids.shape[0],)}
            new = id_set - self.marker_times.keys()
            for i in new:
                self.marker_times[i] = self.frame_time
            remove = self.marker_times.keys() - id_set
            for i in remove:
                del self.marker_times[i]
                


    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def procces_frame(self, frame: QtMultimedia.QVideoFrame):
        pool = QtCore.QThreadPool.global_instance()
        detect_task = MarkerDetect(frame)
        detect_task.result.connect(self.update_view3)
        pool.start(detect_task)

    def paint_event(self, e: QtGui.QPaintEvent):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.set_render_hint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.set_render_hint(QtGui.QPainter.RenderHint.TextAntialiasing)
        if self.current_marker_views != None:
            target = self.center_in_widget(self.current_image.size())
            painter.set_viewport(target)
            painter.set_window(QtCore.QRect(QtCore.QPoint(0, 0), self.current_image.size()))
            painter.draw_image(0, 0, self.current_image)
            for poly, color, degree in self.current_marker_views:
                pen = QtGui.QPen(color)
                pen.set_width(4)
                painter.set_pen(pen)
                painter.set_brush(QtCore.Qt.BrushStyle.NoBrush)
                painter.draw_polygon(poly)
                bound: QtCore.QRectF = poly.bounding_rect()
                span = max(bound.width(), bound.height())
                margin = span * 0.15
                margins = QtCore.QMarginsF(margin, margin, margin, margin)
                rect = bound - margins
                painter.set_pen(QtCore.Qt.PenStyle.NoPen)
                brush = QtGui.QBrush('green')
                painter.set_brush(brush)
                print(degree)
                painter.draw_pie(rect, 5760 * (90/360), -degree)
        painter.reset_transform()
        gradient = QtGui.QLinearGradient(self.size.width()/2, 0, self.size.width()/2, 150)
        gradient.set_color_at(0, QtGui.QColor(0, 0, 0, 255))
        gradient.set_color_at(1, QtGui.QColor(0, 0, 0, 0))
        painter.fill_rect(0, 0, self.size.width(), 150, gradient)
        font = QtGui.QFont()
        font.set_weight(QtGui.QFont.Weight.Medium)
        font.set_pixel_size(32)
        painter.set_font(font)
        pen = QtGui.QPen('#F6ED99')
        painter.set_pen(pen)
        # painter.draw_text(16, 42, self.survey.question) #TODO: use static text
        painter.end()

    def center_in_widget(self, image_size: QtCore.QSize) -> QtCore.QRect:
        image_ratio = image_size.width()/image_size.height()
        frame_ratio = self.size.width()/self.size.height()
        if frame_ratio < image_ratio:
            w = self.size.width()
            h = w/image_ratio
            x = 0
            y = (self.size.height() - h)/2
            return QtCore.QRect(x, y, w, h)
        elif frame_ratio > image_ratio:
            h = self.size.height()
            w = h*image_ratio
            y = 0
            x = (self.size.width() - w)/2
            return QtCore.QRect(x, y, w, h)
        else: # frame_ratio == image_ratio:
            return QtCore.QRect(QtCore.QPoint(0, 0), self.size)

    def set_camera(self, index: int):
        self.camera.stop()
        self.camera = QtMultimedia.QCamera(QtMultimedia.QMediaDevices.video_inputs[index])
        self.session.camera = self.camera
        self.camera.start()