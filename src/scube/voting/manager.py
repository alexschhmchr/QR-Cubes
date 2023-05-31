import enum
import math
import typing
from typing import List, Tuple

import numpy as np
# import pandas as pd
from PySide6.QtCore import QObject, Signal

# import voting.xlsxsaver as xs
# from . import xlsxsaver as xs

from .marker import MarkerType

from .questions import QuestionType, Question, get_all_question_names

class VoteType(enum.Enum):
    GENDER = 0
    GROUP = 1
    RATE = 2
    YEAR = 3
    TIME = 4

VERBOSE = True
VOTE_GENDER_DICT = {3: "männlich", 1: "weiblich"}
VOTE_GROUP_DICT = {2: "Gruppe 1", 3: "Gruppe 5", 0: "Gruppe 3", 5: "Gruppe 2", 4: "Gruppe 4"}
VOTE_RATE_WORD_DICT = {2: "schlecht", 1: "geht so", 0: "gut", 3: "geht so", 5: "sehr schlecht", 4: "sehr gut"}
#VOTE_RATE_GRADE_DICT = {2: 4, 1: 3, 0: 2, 3: 3, 5: 5, 4: 1}
VOTE_RATE_GRADE_DICT = {2: 2, 1: 3, 0: 4, 3: 3, 5: 1, 4: 5}
VOTE_TIME_DICT = {2: '1 h', 3: '5 h oder mehr', 0: '3 h', 5: '2 h', 4: '4 h'}
VOTE_YEAR_DICT = {2: 1, 3: 5, 0: 3, 5: 2, 4: 4}
votename_to_type = {'Geschlecht': VoteType.GENDER, 'Gruppe': VoteType.GROUP, 'Insgesamt': VoteType.RATE, 'Begrüßung': VoteType.RATE, 'Betreuung': VoteType.RATE, 'Führung': VoteType.RATE, 'Robotik': VoteType.RATE, 'Lageregelung': VoteType.RATE, 'Probenanalyse': VoteType.RATE, 'Infrarot': VoteType.RATE, 'OpenSchoolLab': VoteType.RATE, 'Dauer': VoteType.TIME, 'digitale Befragung': VoteType.RATE}

VoteList = typing.List[str]

def id_to_vote_func(q_type: VoteType):
    dict_ = None
    if q_type == QuestionType.GENDER:
        dict_ = VOTE_GENDER_DICT
    elif q_type == QuestionType.RATE or q_type == QuestionType.RATE_3:
        dict_ = VOTE_RATE_GRADE_DICT
    elif q_type == QuestionType.GROUP:
        dict_ = VOTE_GROUP_DICT
    if dict_ == None:
        return lambda x: x
    else:
        return lambda x: dict_[x]


CUBES = 35 #total available cubes for voting
NO_VOTE_IDENTFIER = None

def parse_aruco_markerid(aruco_markerid: int) -> typing.Tuple[int, int]:
    cubeid = aruco_markerid // 6
    voteid = aruco_markerid - cubeid * 6
    return cubeid, voteid

class Votes:
    def __init__(self, questions_len: int):
        self.votes = {}
        self.raw_vote_list = [NO_VOTE_IDENTFIER for _ in range(questions_len)]
        self._questions_len = questions_len

    def _create_list(self):
        return self.raw_vote_list.copy()

    def set_vote(self, cube_id: int, vote_index: int, vote_id: int):
        if cube_id not in self.votes:
            self.votes[cube_id] = self._create_list()
        self.votes[cube_id][vote_index] = vote_id

    def get_vote(self, cube_id: int, vote_index: int):
        if cube_id not in self.votes:
            return NO_VOTE_IDENTFIER
        return self.votes[cube_id][vote_index]
    
    def has_voted(self, cube_id: int, question_index: int): 
        return self.get_vote(cube_id, question_index) != NO_VOTE_IDENTFIER

    # def get_votes(self, questions: Tuple[Question]) -> pd.DataFrame:
    #     question_names = get_all_question_names(questions)
    #     votes = self._to_df(question_names)
    #     for q in questions:
    #         transform_func = id_to_vote_func(q.type_)
    #         if q.type_ == QuestionType.RATE_3:
    #             for name in q.get_names():
    #                 series = votes[name]
    #                 self._transform_series(series, name, transform_func)
    #         else:
    #             series = votes[q.name]
    #             self._transform_series(series, q.name, transform_func)
    #     return votes

    # def _transform_series(self, series, col_name: 'str', transform_func):
    #     for i in series.index:
    #         val = series.loc[i]
    #         if val is not None:
    #             if math.isnan(val) == False:
    #                 series.loc[i] = transform_func(series.at[i])

    def set_questions_len(self, questions_len: int):
        if self.votes: # don't change running voting
            return

        old_len = self._questions_len
        len_diff = questions_len - old_len
        if len_diff < 0:
            del self.raw_vote_list[:abs(len_diff)]
        else:
            append_list = [NO_VOTE_IDENTFIER for _ in range(len_diff)]
            """for vote_values in self.votes.values():
                vote_values += append_list"""
            self.raw_vote_list += append_list
        self._questions_len = questions_len

    # def _to_df(self, question_names: List[str]) -> pd.DataFrame:
    #     return pd.DataFrame.from_dict(self.votes, orient='index', columns=question_names)
    
valid_answers = {
    QuestionType.GENDER: [1, 3],
    QuestionType.GROUP: [0, 2, 3, 4, 5],
    QuestionType.RATE: [0, 1, 2, 3, 4, 5],
    QuestionType.RATE_3: [0, 1, 2, 3, 4, 5],
}
    
class VoteManagerFunctional:
    def __init__(self, question_types: Tuple[QuestionType]):
        self.question_types = question_types
        self.votes = Votes(len(question_types))
        self.vote_counter = 0

    def next_question(self):
        self.vote_counter += 1
        return self.vote_counter

    def set_question_type_list(self, question_types: Tuple[QuestionType]):
        self.question_types = question_types
        self.votes.set_questions_len(len(question_types))

    def process_markerid(self, aruco_markerid: int, save_vote: bool) -> MarkerType:
        cubeid, voteid = parse_aruco_markerid(aruco_markerid)
        if cubeid < CUBES and self.vote_counter < len(self.question_types):
            current_question_type = self.question_types[self.vote_counter]
            if self.votes.get_vote(cubeid, self.vote_counter) != NO_VOTE_IDENTFIER: #check if the cube already answered the question
                return MarkerType.PROCCESSED
            if voteid not in valid_answers[current_question_type]: #check if the shown marker is a valid answer to current question
                return MarkerType.UNVALID
            if save_vote:
                self.votes.set_vote(cubeid, self.vote_counter, voteid)
            return MarkerType.VALID
        else:
            return MarkerType.UNVALID

    def get_votes(self, questions: Tuple[Question]):
        return self.votes.get_votes(questions)
    
    def is_end(self):
        return self.vote_counter >= len(self.question_types)

class SurveyManager:

    def process_marker(self, marker_id: int, save_vote: bool) -> MarkerType:
        pass