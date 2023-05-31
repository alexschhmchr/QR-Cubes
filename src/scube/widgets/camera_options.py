from dataclasses import dataclass
import sys

from PySide6 import QtCore, QtWidgets, QtMultimedia
from __feature__ import snake_case, true_property

@dataclass
class Camera:
    id: bytes | bytearray
    name: str

    # def __init__(self, id: bytes, name: str):
    #     self.id = id
    #     self.name = name

    # def __init__(self, camera_device: QtMultimedia.QCameraDevice):
    #     self.id = camera_device.id
    #     self.name = camera_device.description

    @property
    def id_qt(self):
        return QtCore.QByteArray(self.id)


#TODO: Support hotswap camera devices
class CameraOptionWidget(QtWidgets.QWidget):
    camera_ids: list[QtCore.QByteArray]
    # selected = QtCore.Signal(int)
    camera_changed = QtCore.Signal(QtCore.QByteArray)

    def __init__(self, cameras: list[Camera]) -> None:
        super().__init__()
        self.camera_ids = [cam.id_qt for cam in cameras]
        self._layout = QtWidgets.QHBoxLayout(self)
        self._cam_label = QtWidgets.QLabel("Webcam Auswahl:")
        self._cam_combobox = QtWidgets.QComboBox()
        self._cam_combobox.add_items([cam.name for cam in cameras])
        self._layout.add_widget(self._cam_label)
        self._layout.add_widget(self._cam_combobox)
        self._cam_combobox.currentIndexChanged.connect(self._emit_camera_id)


    #TODO: handle new devices
    # def set_devices(self, devices: list[QtMultimedia.QCameraDevice]):
    #     self.devices = devices

    # won't trigger signal
    # def set_camera(self, camera: QtMultimedia.QCameraDevice):
    #     i = self.devices.index(camera)
    #     self.webcam_combobox.current_index = i

    def _emit_camera_id(self, index: int):
        cam_id = self.camera_ids[index]
        print(cam_id)
        print(type(cam_id))
        self.camera_changed.emit(cam_id)

    def _camera(self):
        return self.camera_ids[self._cam_combobox.current_index]

    current_device_id = QtCore.Property(QtMultimedia.QCameraDevice, _camera, notify=camera_changed)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    cameras = [Camera(b'0', "Device 1"), Camera(b'1', "Device 2")]
    widget = CameraOptionWidget(cameras)
    widget.show()
    sys.exit(app.exec())