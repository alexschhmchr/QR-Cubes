import unittest
from unittest.mock import Mock, patch
import time

import cv2

from scube.voting.questions import Question, SpecificQuestion, QuestionType, NSpecificQuestion, NQuestion
# import survey
# import aruco
import scube.survey
import numpy as np
from PySide6 import QtCore, QtGui, QtTest


test_img_path = 'test/one_marker_test.jpg'

class SurveyTestCase(unittest.TestCase):
    # class SurveyMock(survey.Survey):
    #     def __init__(self) -> None:
    #         super().__init__()
    #         self.i = 0

    #     def advance(self):
    #         self.i += 1

    #     def process_markers(self, data: tuple[tuple[np.ndarray], np.ndarray, QtGui.QImage]):
    #         super().process_markers(data)
    #         markers, ids, image = data
    #         for marker, id in zip(markers, ids):
    #             pass
    #         self.processed.emit()

    # def setUp(self):
    #     self.test_q = (
    #         Question(name='A', type_=QuestionType.GENDER),
    #         SpecificQuestion(name='B', type_=QuestionType.GROUP, question='G')
    #     )

    # def test_on_marker_detection(self):
    #     test_img = cv2.imread(test_img_path)
    #     survey_t = survey.SurveyThread(self.test_q)
    #     survey_t.detect(test_img)

    # def test_marker_procces(self):
    #     sv = survey.DLRSurvey()
    #     spy = QtTest.QSignalSpy(sv.processed)
    #     img = QtGui.QImage()
    #     markers = np.zeros((1, 4, 1, 2))
    #     ids = [0,]
    #     data = (markers, ids, img)
    #     sv.process_markers(data)
    #     self.assertEqual(spy.count(), 1)
    #     view = spy.at(0)[0]
    #     img_result, marker_view = view
    #     self.assertEqual(img_result, img)
    #     self.assertEqual(len(marker_view), 1)
    #     poly, color, deg = marker_view[0]
    #     self.assertListEqual(poly.toList(), QtGui.QPolygonF([QtCore.QPoint(0, 0)]).toList())
    #     self.assertEqual(color, QtGui.QColor(255, 0, 0))
    #     self.assertEqual(deg, 0)
    #     # self.assertTupleEqual(view, (img, [(QtGui.QPolygonF([QtCore.QPoint(0, 0)]), QtGui.QColor(255, 0, 0), 0)]))
    
    def test_marker_procces_no_deg_after_valid(self):
        sv = scube.survey.DLRSurvey(questions_=[Question(name='Geschlecht',type_=QuestionType.GENDER)])
        markers = np.zeros((1, 4, 1, 2))
        ids = [1,]
        sv.start()

        poly, color, deg = sv.process_markers(markers, ids, 0)
        self.assertListEqual([p.toList() for p in poly], [QtGui.QPolygonF([QtCore.QPoint(0, 0)]).toList()])
        self.assertListEqual(color, [QtGui.QColor(0, 0, 255)])
        self.assertListEqual(deg, [0])

        poly, color, deg = sv.process_markers(markers, ids, 0.5)
        self.assertListEqual([p.toList() for p in poly], [QtGui.QPolygonF([QtCore.QPoint(0, 0)]).toList()])
        self.assertListEqual(color, [QtGui.QColor(0, 0, 255)])
        self.assertListEqual(deg, [360*16*0.5])

        poly, color, deg = sv.process_markers(markers, ids, 1.05)
        self.assertListEqual([p.toList() for p in poly], [QtGui.QPolygonF([QtCore.QPoint(0, 0)]).toList()])
        self.assertListEqual(color, [QtGui.QColor(0, 0, 255)])
        self.assertListEqual(deg, [360*16*1.05])

        poly, color, deg = sv.process_markers(markers, ids, 1.1)
        self.assertListEqual([p.toList() for p in poly], [QtGui.QPolygonF([QtCore.QPoint(0, 0)]).toList()])
        self.assertListEqual(color, [QtGui.QColor(0, 0, 255)])
        self.assertListEqual(deg, [0])

        poly, color, deg = sv.process_markers(markers, ids, 2)
        self.assertListEqual([p.toList() for p in poly], [QtGui.QPolygonF([QtCore.QPoint(0, 0)]).toList()])
        self.assertListEqual(color, [QtGui.QColor(0, 255, 0)])
        self.assertListEqual(deg, [0])

        poly, color, deg = sv.process_markers(markers, ids, 2.5)
        self.assertListEqual([p.toList() for p in poly], [QtGui.QPolygonF([QtCore.QPoint(0, 0)]).toList()])
        self.assertListEqual(color, [QtGui.QColor(0, 255, 0)])
        self.assertListEqual(deg, [0])

    # def test_process_markers(self):
    #     survey = scube.survey.DLRSurvey()
    #     markers = np.array([[[0, 0]],])
    #     marker_ids = [0]
    #     frame_time = 0
    #     polys, colors, degrees = survey.process_markers(markers, marker_ids, frame_time)
    #     self.assertListEqual(polys, [QtGui.Q])


    # def test_mark

    def test_complete_survey(self):
        questions = [
            Question(name='Geschlecht',type_=QuestionType.GENDER),
            Question(name='Gruppe',type_=QuestionType.GROUP)
        ]
        sv = scube.survey.DLRSurvey(questions)
        sv.start()

        markers = np.zeros((2, 4, 1, 2))
        ids = [1, 7]
        poly, color, deg = sv.process_markers(markers, ids, 0)
        poly, color, deg = sv.process_markers(markers, ids, 1.2)
        
        sv.advance()
        
        markers = np.zeros((2, 4, 1, 2))
        ids = [5, 11]
        poly, color, deg = sv.process_markers(markers, ids, 2)
        poly, color, deg = sv.process_markers(markers, ids, 3.2)

        sv.advance()


    def test_load_pickled(self):
        import pickle
        from pathlib import Path
        with open(Path.home() / 'Documents' / 'Umfragen' / 'umfrage-15-11-2022-20-58.pickle', 'rb') as f:
            data = pickle.load(f)
            expected = {
                'Geschlecht': {
                    0: 1,
                    1: 1
                },
                'Gruppe': {
                    0: 5,
                    1: 11
                }
            }
            self.assertEqual(data, expected)
    
    def test_flatten_questions(self):
        questions = [
            Question(name='Geschlecht',type_=QuestionType.GENDER),
            NQuestion(name='Lageregelung', type_=QuestionType.RATE_3, question_list=['Gesamtbewertung', 'Interesse', 'Verständlichkeit'])
        ]
        expected = [
            Question(name='Geschlecht',type_=QuestionType.GENDER),
            Question(name='Lageregelung Gesamtbewertung', type_=QuestionType.RATE),
            Question(name='Lageregelung Interesse', type_=QuestionType.RATE),
            Question(name='Lageregelung Verständlichkeit', type_=QuestionType.RATE),
        ]
        result = scube.survey.flatten_questions(questions)
        print(result)
        self.assertListEqual(result, expected)

if __name__ == '__main__':
    unittest.main()