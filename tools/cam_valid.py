from time import sleep
from PySide6.QtMultimedia import QMediaDevices

device = QMediaDevices.videoInputs()[0]
while True:
    print(device.isNull())
    sleep(0.2)