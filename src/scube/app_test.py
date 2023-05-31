import unittest
from time import sleep
from PySide6 import QtTest
from scube.app import App

class AppTest(unittest.TestCase):

    def test_init(self):
        app = App()
        spy = QtTest.QSignalSpy(app.frame_processed)
        sleep(4)
        self.assertTrue(spy.count() > 0)


if __name__ == '__main__':
    unittest.main()