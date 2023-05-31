import sys
from PySide6 import QtCore, QtWidgets, QtOpenGLWidgets, QtGui, QtMultimedia
from __feature__ import snake_case, true_property




class CameraWidget(QtOpenGLWidgets.QOpenGLWidget):
    current_image: QtGui.QImage
    
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.video_sink = QtMultimedia.QVideoSink()
        self.video_sink.videoFrameChanged.connect(self.update_view)
        self.camera = QtMultimedia.QCamera(QtMultimedia.QMediaDevices.video_inputs[0])
        self.session = QtMultimedia.QMediaCaptureSession()
        self.session.camera = self.camera
        self.session.video_output = self.video_sink
        self.camera.start()
        self.current_image = None

    def close_event(self, event: QtGui.QCloseEvent):
        self.camera.stop()
        super().close_event(event)
    
    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def update_view(self, frame: QtMultimedia.QVideoFrame):
        self.current_image = frame.to_image()
        self.update()

    def paint_event(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.set_render_hint(QtGui.QPainter.RenderHint.Antialiasing)
        if self.current_image != None:
            source = QtCore.QRect(0, 0, 1920, 1080)
            target = self.center_in_widget(self.current_image.size())
            # painter.fill_rect(target, QtGui.QColor('gray'))
            painter.draw_image(target, self.current_image)
        pen = QtGui.QPen('white')
        painter.set_pen(pen)
        # painter.font().set_bold(True)
        # painter.font().set_pixel_size(36)
        font = QtGui.QFont()
        font.set_bold(True)
        font.set_pixel_size(36)
        painter.set_font(font)
        painter.draw_text(16, 42, 'TEST TEST TEST TEST') #TODO: use static text
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

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_layout = QtWidgets.QStackedLayout(self)
        self.main_layout.stacking_mode = QtWidgets.QStackedLayout.StackAll
        self.camera_widget = CameraWidget()
        self.main_layout.add_widget(self.camera_widget)
        self.label = QtWidgets.QLabel("TEST TEST TEST TEST TEST TEST ")
        self.label.margin = 8
        self.label.size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.label.style_sheet = "background-color: rgba(0, 0, 0, 0.5); border-radius: 8px; color: white; font-size: 14px; font-weight: bold;"
        self.label.alignment = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop
        self.main_layout.add_widget(self.label)
        self.main_layout.current_index = 1
        print(self.label.size_hint())
        print(self.label.size)
    

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    camera_view = CameraWidget()
    camera_view.size = QtCore.QSize(1280, 720)
    camera_view.show()
    # camera_view.update()
    sys.exit(app.exec())
