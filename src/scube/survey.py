from abc import ABC, abstractmethod
from copy import deepcopy
from collections import Counter
import datetime
from enum import Enum
from threading import Thread
import json
import logging
from pathlib import Path
from typing import Tuple
import sys
import time
import queue
import pickle

import cv2 as cv
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QObject, Signal, Qt
from PySide6 import QtCore, QtGui, QtMultimedia

from . import aruco
from . import voting
from .voting import questions

# from .voting.marker import MarkerType
# from .voting import sql
from .voting.questions import Question, SpecificQuestion, NSpecificQuestion, QuestionType, NQuestion
import numpy as np


logger = logging.getLogger(__name__)

QUESTION_JSON_FILENAME = 'fragen.json'
#DEFAULT_LIST = ['Geschlecht', 'Gruppe', 'Insgesamt', 'Begrüßung', 'Betreuung', 'Führung', 'OpenSchoolLab']
#STANDARD_LIST = ['Dauer', 'digitale Befragung', 'Geschlecht']
BEGIN_ITEMS_LENGTH = 6

class Survey(QObject):
    processed = QtCore.Signal(QImage, list) # tuple[QImage, list[tuple[QPolygonF, QColor, float]]] float: degree

    def advance(self):
        pass

    def stop(self):
        pass
    
    def start(self):
        pass

    @property
    def question(self) -> str:
        pass

    def process_markers(self, markers: list[np.ndarray], marker_ids: list[int], frame_time: float):
        pass

    @QtCore.Slot(QtGui.QImage, tuple, np.ndarray)
    def on_image_proccesed(self, image: QtGui.QImage, markers: list[np.ndarray], marker_ids: list[int]):
        # frame_time = time.monotonic()
        pass
    

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def process_frame(self, frame: QtMultimedia.QVideoFrame):
        pass

VALID_TIME = 1.

VALID_ANSWERS = {
    QuestionType.GENDER: [1, 3],
    QuestionType.GROUP: [0, 2, 3, 4, 5],
    QuestionType.COUNT: [0, 2, 3, 4, 5],
    QuestionType.RATE: [0, 1, 2, 3, 4, 5],
    QuestionType.RATE_3: [0, 1, 2, 3, 4, 5],
}

def flatten_questions(questions: list[Question]) -> list[Question]:
        # return [
        #     Question(f'{q} {sq}', QuestionType.RATE) for sq in q.question_list if type(q) == NSpecificQuestion else q for q in questions_
        # ]
        nested = [
            [Question(f'{q.name} {sq}', QuestionType.RATE) for sq in q.question_list]
            if type(q) == NSpecificQuestion or type(q) == NQuestion else [q]
            for q in questions
        ]
        flatten = [q for nq in nested for q in nq]
        return flatten

def flatten_nquestion(question: NQuestion) -> Question:
    assert type(question) == NQuestion
    return [Question(f'{question.name} {sq}', QuestionType.RATE) for sq in question.question_list]

class QuestionManager(QObject):

    def __init__(self, questions_: list[Question] = questions.load_questions('fragen.json'), parent: QtCore.QObject | None = None):
        super().__init__(parent)
        self._all_questions = {q.name: q for q in questions_}
        self._current_questions = {q.name: q for q in flatten_questions(questions_)}


    @property
    def display_names(self) -> list[str]:
        return [q.name for q in self._current_questions.values()]

    @property
    def flattened_questions(self) -> Question:
        return list(self._current_questions.values())
    

    def add_question_with_name(self, question_name: str):
        pass

    def remove_question_with_name(self, question_name: str):
        pass

    def remove_at_display_list(self, index: int):
        pass



class DLRSurvey(Survey):
    class MarkerType(Enum):
        VALID = 0
        PROCCESSED = 1
        UNVALID = 2
    

    def __init__(self, questions_: list[Question]=questions.load_questions('fragen.json')) -> None:
        super().__init__()
        # self.i = 0
        self.sema = QtCore.QSemaphore(2)
        self.marker_times = {}
        self.scanned = set()
        # self.questions = questions_
        self.all_questions = flatten_questions(questions_)
        self.questions = deepcopy(self.all_questions) #TODO: QObject with Signals
        # self.question_dict = 
        self.current_question_i = 0
        self.question_types = [q.type_ for q in self.questions]
        # self.voting_manager = voting.VoteManager(self.question_types)
        self.scanning = False
        self.image_queue = queue.PriorityQueue()
        self.answers = {}

    def advance(self) -> bool:
        # print('advance')
        # self.voting_manager.next_question()
        self.stop()
        if self.current_question_i >= len(self.questions):
        # if self.voting_manager.is_end():
            return True
        else:
            self.current_question_i += 1
            if self.current_question_i >= len(self.questions):
                return True
            return False


    def stop(self):
        self.scanning = False
        self.marker_times.clear()
    
    def start(self):
        self.scanning = True
        question_name = self.questions[self.current_question_i].name
        if question_name not in self.answers:
            self.answers[question_name] = {}

    def save(self, survey_info_data: dict[str, str]):
        # votes_df = self.voting_manager.get_votes(self.questions)

        # question_names = [q.name for q in self.questions]
        # vt = voting.VoteTransformer(votes_df, question_names[2:])

        # xlsx_saver = voting.XlsxSaver()
        # xlsx_saver.save_votes(votes_df, vt.get_means(), vt.get_group_means(), vt.get_histogram())
        time = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')
        destination_folder = Path.home() / 'Documents' / 'Umfragen'
        destination_folder.mkdir(exist_ok=True, parents=True)
        filename = destination_folder / f'umfrage-{time}.pickle'
        with open(filename, 'wb') as f:
            data = {
                'version': 0,
                'survey_info': survey_info_data,
                'answers': self.answers
            }
            pickle.dump(data, f, 5)

    def get_question_text(self) -> str:
        if self.current_question_i < len(self.questions):
            current_question = self.questions[self.current_question_i]
            if type(current_question) == SpecificQuestion:
                return current_question.question
            elif type(current_question) == Question:
                return current_question.name
            else:
                print(current_question)
                raise TypeError()
        else:
            return 'Fertig!'
        
    def delete_question_with_name(self, question_name: str):
        index = next(i for i, q in enumerate(self.questions) if q.name == question_name)
        del self.questions[index]

    def add_question_with_name(self, question_name: str):
        print(question_name)
        question = next(q for q in self.all_questions if q.name == question_name)
        self.questions.append(question)

    def _parse_aruco_markerid(aruco_markerid: int) -> tuple[int, int]:
        cubeid = aruco_markerid // 6
        voteid = aruco_markerid - cubeid * 6
        return cubeid, voteid
        

    def process_markerid(self, id_: int, save_vote: bool) -> MarkerType:
        # TODO: work with cube instance object
        if self.current_question_i < len(self.questions):
            current_question = self.questions[self.current_question_i]
            cube_id, vote_id = DLRSurvey._parse_aruco_markerid(id_)
            if vote_id in VALID_ANSWERS[current_question.type_]:
                if current_question.name in self.answers:
                    current_question_answers = self.answers[current_question.name]
                    if cube_id in current_question_answers:
                        return DLRSurvey.MarkerType.PROCCESSED
                    else:
                        if save_vote:
                            current_question_answers[cube_id] = vote_id
                            # TODO: return PROCCESSED here?
                        return DLRSurvey.MarkerType.VALID
                else:
                    if save_vote:
                        self.answers[current_question.name] = {cube_id: vote_id}
                    else:
                        self.answers[current_question.name] = {}
                    return DLRSurvey.MarkerType.VALID
            else:
                return DLRSurvey.MarkerType.UNVALID
        else:
            return DLRSurvey.MarkerType.PROCCESSED
    
    # def process_answer(self, cube_id: int, vote_id: int) -> bool:
        



    # @property
    # def question(self) -> str:
    #     question = self.questions[self.voting_manager.vote_counter]
    #     if isinstance(question, SpecificQuestion):
    #         return question.question
    #     else:
    #         return question.name

    # def process_markers(self, markers: list[np.ndarray], ids: list[int], frame_time: float) -> tuple:
    #     # markers, ids, image = data
    #     polys = [QtGui.QPolygonF([QtCore.QPointF(x, y) for x, y in marker[0]]) for marker in markers]
    #     # frame_time = time.monotonic()
    #     # print(frame_time)
    #     if self.scanning:
    #         scanned = self.update_marker_times(ids, frame_time)
    #     else:
    #         scanned = [False] * len(markers)
    #     # marker_types = [self.voting_manager.process_markerid(i, scanned) for i, scanned in zip(ids, scanned)]
    #     marker_types = [self.process_markerid(i, scanned) for i, scanned in zip(ids, scanned)]
    #     colors = [self.color(mt) for mt in marker_types]
    #     degrees = []
    #     for i, s in zip(ids, scanned):
    #         if i in self.marker_times and not s:
    #             print("not scanned")
    #             show_time = frame_time - self.marker_times[i]
    #             degree = 5760 * show_time/VALID_TIME
    #         else:
    #             print("scanned")
    #             degree = 0
    #         degrees.append(degree)
    #
    #    return polys, colors, degrees

    def process_markers(self, markers: list[np.ndarray], ids: list[int], frame_time: float) -> tuple:
        # markers, ids, image = data
        polys = [QtGui.QPolygonF([QtCore.QPointF(x, y) for x, y in marker[0]]) for marker in markers]
        if self.current_question_i < len(self.questions):
            cube_vote_ids = [DLRSurvey._parse_aruco_markerid(idx) for idx in ids]
            current_question = self.questions[self.current_question_i]
            valids = [vote_id in VALID_ANSWERS[current_question.type_] for _, vote_id in cube_vote_ids]
            counter = Counter([cube_id for cube_id, _ in cube_vote_ids])
            uniques = [counter[cube_id] == 1 for cube_id, _ in cube_vote_ids]
            process = [valid and unique for valid, unique in zip(valids, uniques)]

            # frame_time = time.monotonic()
            # print(frame_time)
            if self.scanning:
                scanned = self.update_marker_times(ids, process, frame_time)
                # current_question_answers = self.answers[current_question.name]
                # for valid, (cube_id, vote_id) in zip(valids, cube_vote_ids):
                #     assert cube_id in current_question_answers
                #     if valid:
                #         current_question_answers[cube_id] = vote_id
                print(scanned)
            else:
                scanned = [False] * len(markers)
            # marker_types = [self.voting_manager.process_markerid(i, scanned) for i, scanned in zip(ids, scanned)]
            marker_types = [self.process_markerid(i, scanned) for i, scanned in zip(ids, scanned)]
        else:
            marker_types = [DLRSurvey.MarkerType.PROCCESSED] * len(ids)
            scanned = [False] * len(markers)
        colors = [self.color(mt) for mt in marker_types]
        degrees = []
        for i, s in zip(ids, scanned):
            if i in self.marker_times and not s:
                print("not scanned")
                show_time = frame_time - self.marker_times[i]
                degree = 5760 * show_time/VALID_TIME
            else:
                # print("scanned")
                degree = 0
            degrees.append(degree)

        return polys, colors, degrees

    @QtCore.Slot(QtGui.QImage, tuple, np.ndarray)
    def on_image_proccesed(self, image: QtGui.QImage, marker_ids: list[int], markers: tuple[np.ndarray]):
        frame_time = time.monotonic()
        polys, colors, degrees = self.process_markers(markers, marker_ids, frame_time)
        marker_views = list(zip(polys, colors, degrees))
        self.processed.emit(image, marker_views)

    def color(self, marker_type: MarkerType) -> QtGui.QColor:
        if marker_type == DLRSurvey.MarkerType.VALID:
            return QtGui.QColor(0, 0, 255)
        elif marker_type == DLRSurvey.MarkerType.PROCCESSED:
            return QtGui.QColor(0, 255, 0)
        else:
            return QtGui.QColor(255, 0, 0)
    
    def update_marker_times(self, ids: np.ndarray, valids: list[bool], frame_time: float):
        if type(ids) != type(None):
            id_set = {idx for idx in ids}
            invalid = {idx for idx, valid in zip(ids, valids) if not valid}
            new = id_set - self.marker_times.keys() - invalid
            # print(id_set)
            for i in new:
                self.marker_times[i] = frame_time
            remove = self.marker_times.keys() - (id_set - invalid)
            for i in remove:
                del self.marker_times[i]
            # for idx, valid in zip(ids, valids):
            #     if not valid and idx in self.marker_times:
            #         del self.marker_times[idx]
            # check = self.marker_times.keys() & id_set
            scanned = []
            for i in ids:
                if i in self.marker_times:
                    time_diff = frame_time - self.marker_times[i]
                    print(time_diff)
                    if time_diff > VALID_TIME + 0.05:
                        # del self.marker_times[i]

                        scanned.append(True)
                    else:
                        scanned.append(False)
                else:
                    scanned.append(False)
            return scanned
            
    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def process_frame(self, frame: QtMultimedia.QVideoFrame):
        # return super().process_frame(frame)
        pool = QtCore.QThreadPool.global_instance()
        detect_task = aruco.MarkerDetect(frame, self.sema)
        detect_task.result.connect(self.on_image_proccesed)
        pool.start(detect_task)