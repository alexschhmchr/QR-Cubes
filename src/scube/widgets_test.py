import unittest
from scube import widgets
from PySide6 import QtCore, QtWidgets, QtMultimedia, QtTest

class QuestionsWidgetTest(unittest.TestCase):

    def test_question_add(self):
        side_bar = widgets.QuestionsWidget(['Question 1', 'Question 2'])
        spy = QtTest.QSignalSpy(side_bar.questions_changed)
        side_bar.question_search_bar.text = 'Question 1'
        side_bar.add_button.click()
        self.assertEqual(spy.count(), 1)
        self.assertListEqual(side_bar.questions, ['Question 1'])
        side_bar.question_search_bar.text = 'Question 2'
        side_bar.add_button.click()
        self.assertEqual(spy.count(), 2)
        self.assertListEqual(side_bar.questions, ['Question 1', 'Question 2'])

    def test_question_remove(self):
        side_bar = widgets.QuestionsWidget(['Question 1', 'Question 2'])
        side_bar._add_question('Question 1')
        side_bar._add_question('Question 2')
        spy = QtTest.QSignalSpy(side_bar.questions_changed)
        side_bar.question_list.current_row = 0
        side_bar.delete_button.click()
        self.assertEqual(spy.count(), 1)
        self.assertListEqual(side_bar.questions, ['Question 2'])

class CameraOptionWidgetTest(unittest.TestCase):

    def test_emit_device_id(self):
        cameras = [widgets.Camera(b'0', "Device 1"), widgets.Camera(b'1', "Device 2")]
        camera_options = widgets.CameraOptionWidget(cameras)
        spy = QtTest.QSignalSpy(camera_options.camera_changed)
        camera_options._cam_combobox.current_index = 1
        self.assertEqual(spy.count(), 1)
        self.assertListEqual(spy.at(0), [b'1'])

    def test_camera(self):
        cameras = [widgets.Camera(b'0', "Device 1"), widgets.Camera(b'1', "Device 2")]
        camera_options = widgets.CameraOptionWidget(cameras)
        self.assertEqual(b'0', camera_options._camera())

class ControlWidgetTest(unittest.TestCase):

    def test_start_clicked(self):
        control = widgets.ControlWidget()
        control.is_init = True
        control.has_next_question = True
        spy = QtTest.QSignalSpy(control.start_clicked)
        control._start_button.click()
        self.assertEqual(spy.count(), 1)
        

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    unittest.main()