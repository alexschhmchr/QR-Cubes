import numpy as np
import cv2 as cv
import logging
from typing import Callable
from threading import Lock
import platform
from PySide6 import QtCore, QtGui, QtMultimedia

from .voting import MarkerType

logger = logging.getLogger(__name__)

VERBOSE = True

MARKER_DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_250)
MARKER_SIZE = 400

class MarkerDetect(QtCore.QObject, QtCore.QRunnable):
    frame: QtMultimedia.QVideoFrame
    sema: QtCore.QSemaphore
    result = QtCore.Signal(QtGui.QImage, list, tuple) # tuple[tuple[np.ndarray], np.ndarray, QtGui.QImage]

    def __init__(self, frame: QtMultimedia.QVideoFrame, sema: QtCore.QSemaphore) -> None:
        QtCore.QObject.__init__(self)
        QtCore.QRunnable.__init__(self)
        self.frame = frame
        self.sema = sema
    
    def run(self):
        # self.move_to_thread(QtCore.QThread.current_thread())
        # self.frame.move_to_thread(QtCore.QThread.current_thread())
        if self.sema.try_acquire():
            img: QtGui.QImage = self.frame.to_image()
            # if img.format() != QtGui.QImage.Format.Format_RGB32:
            #     print(img.format())
            #     return
            # print(img.format())

            # assert img.format() == QtGui.QImage.Format.Format_RGBA8888_Premultiplied
            if img.format() == QtGui.QImage.Format.Format_RGBA8888_Premultiplied:
                arr = np.asarray(img.bits()).reshape(img.height(), img.width(), 4)[:,:, :-1]
            elif img.format() == QtGui.QImage.Format.Format_RGB32:
                arr = np.asarray(img.bits()).reshape(img.height(), img.width(), 4)[:,:, 1:]
            else:
                raise Exception(f'Image format not supported: {img.format()}')
            # assert(img.format() == QtGui.QImage.Format.Format_RGB32)
            # print(img)
            # arr = np.asarray(img.bits()).reshape(img.height(), img.width(), 4)[:,:, :-1]
            # arr = np.asarray(img.bits()).reshape(img.height(), img.width(), 4)[:,:, :-1]
            marker_corners, marker_ids, rej = cv.aruco.detectMarkers(arr, MARKER_DICT)
            if type(marker_ids) == type(None):
                marker_ids = []
            else:
                marker_ids = marker_ids.reshape(marker_ids.shape[0]).tolist()
            # print(type(marker_corners), marker_corners, type(marker_ids), marker_ids)
            self.result.emit(img, marker_ids, marker_corners)
            self.sema.release(1)
        else:
            # print("ignore")
            logger.info("ignore webcam frame.")
            # pass

class MarkerCam(QtCore.QObject):
    frame_received = QtCore.Signal(QtMultimedia.QVideoFrame)

    def __init__(self, parent: QtCore.QObject | None=None):
        super().__init__(parent)
        self.devices = QtMultimedia.QMediaDevices.video_inputs
        # self.device = self.devices[-1]
        self.device = QtMultimedia.QMediaDevices.default_video_input
        self.camera = QtMultimedia.QCamera(self.device)
        self.video_sink = QtMultimedia.QVideoSink()
        self.video_sink.videoFrameChanged.connect(self.frame_received)
        self.session = QtMultimedia.QMediaCaptureSession()
        self.session.set_video_sink(self.video_sink)
        self.session.camera = self.camera
        self.camera.start()

    @property
    def camera_device(self):
        return self.camera.camera_device
    
    @camera_device.setter
    def camera_device(self, camera_device: QtMultimedia.QCameraDevice):
        self.camera.camera_device = camera_device

    def set_camera_id(self, id: QtCore.QByteArray):
        cameras = {d.id: d for d in QtMultimedia.QMediaDevices.video_inputs}
        self.camera_device = cameras[id]

#Deprecated
class MarkerDetector:
    MARKER_DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_250)
    MARKER_SIZE = 400

    def __init__(self, cam_id, on_marker: Callable):
        self.cam_lock = Lock()
        self.cam = MarkerDetector.init_webcam(0)
        #self.cam_calib = np.load("calib.npz")
        self.on_marker = on_marker

    def init_webcam(cam_id: int) -> cv.VideoCapture:
        if platform.system() == 'Windows':
            logger.info("Detected Windows OS. Using DSHOW backend")
            backend = cv.CAP_DSHOW # faster switching to webcam on windows
        else:
            backend = cv.CAP_ANY
        backend = cv.CAP_ANY
        cam = cv.VideoCapture(cam_id, backend)
        cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        backend_name = cam.getBackendName()
        logger.info("Video capture device initialised with %s backend.", backend_name)
        return cam

    def set_webcam(self, cam_id: int):
        with self.cam_lock:
            self.cam.release()
            self.cam = MarkerDetector.init_webcam(cam_id)


    def detect_marker_and_apply(self, test_img: np.ndarray=None):
        img = None
        if test_img is None:
            with self.cam_lock:
                ret, img = self.cam.read()
        else:
            img = test_img
        #print(f'shape: {img.shape}, width: {self.cam.get(cv.CAP_PROP_FRAME_WIDTH)}, height: {self.cam.get(cv.CAP_PROP_FRAME_HEIGHT)}')
        marker_corners, marker_ids, rej = cv.aruco.detectMarkers(img, self.MARKER_DICT)
        if len(marker_corners) > 0:
            """
            rvecs, tvecs, objPoints = cv.aruco.estimatePoseSingleMarkers(marker_corners, self.MARKER_SIZE,
                                                                         self.cam_calib["arr_0"],
                                                                         self.cam_calib["arr_1"])
            """
            for i in range(len(marker_ids)):
                marker_id = marker_ids[i][0]  # [0] because marker_ids is 2d
                marker_type = self.on_marker(marker_id)
                img = self._draw_marker(img, marker_corners[i], marker_type)    
        return img
    
    def _draw_marker(self, img: np.ndarray, marker_corners: np.ndarray, marker_type: MarkerType):
        color = (0, 0, 0)
        if marker_type == MarkerType.VALID:
            color = (255, 0, 0)
        elif marker_type == MarkerType.UNVALID:
            color = (0, 0, 255)
        elif marker_type == MarkerType.PROCCESSED:
            color = (0, 255, 0)
        return cv.polylines(img, marker_corners.astype(np.int32), True, color, 2)

    def _get_orientation(self, rot_vec, ):
        rod_mtx, jab = cv.Rodrigues(rot_vec)
        proj_mtx = self._convert_rod_to_proj(rod_mtx)
        cameraMatrix, rotMatrix, transVect, rotMatrixX, rotMatrixY, rotMatrixZ, marker_angles = cv.decomposeProjectionMatrix(
            proj_mtx)
        return marker_angles

    def _convert_rod_to_proj(self, rod_mtx):
        row0 = rod_mtx[0].tolist()
        row0.append(0)
        row1 = rod_mtx[1].tolist()
        row1.append(0)
        row2 = rod_mtx[2].tolist()
        row2.append(0)
        proj_mtx = np.array([row0, row1, row2])
        return proj_mtx