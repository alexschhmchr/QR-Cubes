import logging
import sys
import time

from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia, QtOpenGLWidgets
from __feature__ import snake_case, true_property
import numpy as np

logger = logging.getLogger(__name__)

VALID_TIME = 1.

# tasks: 
class CameraWidget(QtOpenGLWidgets.QOpenGLWidget):
    #TODO: Thread safe?
    current_image: QtGui.QImage
    current_marker_views: list[tuple[QtGui.QPolygonF, QtGui.QColor, float]]
    
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        logger.debug('Start Camera Widget initialization.')
        super().__init__(parent)
        self.minimum_size = QtCore.QSize(800, 600)
        self.current_image = None
        self.current_marker_views = None
        self.text = ""
        logger.debug('Camera Widget initialized.')

    def update_marker_image(self, image: QtGui.QImage, marker_views: list[tuple[QtGui.QPolygonF, QtGui.QColor, float]]):
        self.current_image = image
        self.current_marker_views = marker_views
        self.update()

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
                pen.set_width(8)
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
        painter.draw_text(16, 42, self.text) #TODO: use static text
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

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    widget = CameraWidget()
    from pathlib import Path
    print(Path.cwd())
    image = QtGui.QImage('tests/one_marker_test.jpg')

    print(image.is_null())
    markers = [(QtGui.QPolygonF([
        QtCore.QPointF(100, 100),
        QtCore.QPointF(300, 100),
        QtCore.QPointF(300, 300),
        QtCore.QPointF(100, 300),
    ]), QtGui.QColor('green'), 16*90.)]
    widget.update_marker_image(image, markers)
    widget.show()
    sys.exit(app.exec())