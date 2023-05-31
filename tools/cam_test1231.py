import sys

import cv2 as cv
from PySide6 import QtMultimedia, QtCore, QtWidgets, QtGui
import numpy as np

from __feature__ import snake_case, true_property


# def main():
#     cap = cv.VideoCapture()
#     cap.open(2, cv.CAP_DSHOW)
#     cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
#     cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
#     running = True
#     while running:
#         ret_val, img = cap.read()
#         # print(ret_val, img)
#         # print(img.shape)
#         cv.imshow('', img)
#         key = cv.waitKey(1)
#         if key == 27:
#             running = False

class CvWindow(QtCore.QObject):
    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def show(self, frame):
        img: QtGui.QImage = frame.to_image()
        print(img.format())
        assert(img.format() == QtGui.QImage.Format.Format_RGB32)
        arr = np.asarray(img.bits()).reshape(img.height(), img.width(), 4)[:,:, :-1]
        # arr = cv.cvtColor(arr, cv.COLOR_RGB2BGR)
        cv.imshow('', arr)
        key = cv.waitKey(1)
        if key == 27:
            camera.stop()

cv_win = CvWindow()
video_sink = QtMultimedia.QVideoSink()
video_sink.videoFrameChanged.connect(cv_win.show)
camera = QtMultimedia.QCamera(QtMultimedia.QMediaDevices.video_inputs[0])
session = QtMultimedia.QMediaCaptureSession()
session.camera = camera
session.video_output = video_sink
# camera.start()


# sys.exit(QtWidgets.QApplication().exec())

# if __name__ == '__main__':
#     main()