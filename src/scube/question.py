from dataclasses import dataclass
from enum import StrEnum
from os import PathLike
import json

from PySide6 import QtCore

class QuestionType(StrEnum):
    GENDER = 'geschlecht'
    GROUP = 'gruppe'
    RATE = 'bewertung'
    RATE_3 = 'bewertung3'
    COUNT = 'anzahl'

@dataclass
class Question:
    name: str
    type: QuestionType
    question: str | None = None

    @classmethod
    def from_dict(cls, dict: dict):
        if 'frage' in dict:
            q_str = dict['frage']
        else:
            q_str = None
        return cls(dict['name'], QuestionType(dict['typ']), q_str)

    def __str__(self) -> str:
        return f'{self.name}'

def load_questions(path: PathLike):
    with open(path) as f:
        questions_dict = json.load(f)
        return [Question.from_dict(q_dict) for q_dict in questions_dict['fragen']]

class QuestionManager(QtCore.QObject):
    question_freeze = QtCore.Signal(int)

    def __getitem__(self, key: int | slice):
        pass

    def ismutable(self, key: int) -> bool:
        pass
    
