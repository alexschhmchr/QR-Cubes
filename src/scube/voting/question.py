from enum import Enum
from dataclasses import dataclass

class QuestionType(Enum):
    GENDER = 0
    GROUP = 1
    RATE = 2
    YEAR = 3
    TIME = 4

@dataclass
class Question:
    name: str
    type: QuestionType
    question: str=None

    def question(self):
        if self.question is None:
            

questions = [
    Question('Geschlecht', QuestionType.GENDER, 'Welches Geschlecht hast du?'),
    Question('Lageregelung', QuestionType.RATE)
]
