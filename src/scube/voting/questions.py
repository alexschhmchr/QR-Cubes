import json
from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys
import os

import jsonschema


class QuestionType(Enum):
    GENDER = 0
    GROUP = 1
    RATE = 2
    RATE_3 = 3
    YEAR = 4
    TIME = 5
    COUNT = 6

QUESTIONS = 'fragen'
QUESTION_NAME = 'name'
QUESTION_TYPE = 'typ'
QUESTION_DESC = 'frage'
QUESTION_TYPES_OBJ = 'fragetypen'
QUESTION_TYPE_3 = 'bewertung3'
QUESTION_TYPE_TO_NAME = {
    QuestionType.GENDER: 'geschlecht',
    QuestionType.GROUP: 'gruppe',
    QuestionType.RATE: 'bewertung',
    QuestionType.RATE_3: 'bewertung3',
    QuestionType.COUNT: 'anzahl'
}

QUESTION_NAME_TO_TYPE = {
    'geschlecht': QuestionType.GENDER,
    'gruppe': QuestionType.GROUP,
    'bewertung': QuestionType.RATE,
    'bewertung3': QuestionType.RATE_3,
    'anzahl': QuestionType.COUNT
}

JSON_SCHEMA = {
    'type': 'object',
    'properties': {
        QUESTIONS: {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties' : {
                    QUESTION_NAME : {
                        'type' : 'string'
                    },
                    QUESTION_TYPE : {
                        'type' : 'string',
                        'enum': list(QUESTION_NAME_TO_TYPE.keys())
                    },
                    QUESTION_DESC: {
                        'type': 'string'
                    }
                },
                'required': [QUESTION_NAME, QUESTION_TYPE],
                'additionalProperties': False,
            },
            'minItems': 1
        },
        QUESTION_TYPES_OBJ: {
            'type': 'object',
            'properties': {
                QUESTIONS: {
                    'type': 'array',
                    'minItems': 1
                }
            }
        }
    },
    'required': [QUESTIONS],
    'if': {
        'properties': {
            QUESTIONS: {
                'items': {
                    'type': 'object',
                    'properties': {
                        QUESTION_TYPE: {
                            'const': QUESTION_TYPE_TO_NAME[QuestionType.RATE_3]
                        }
                    }
                }
            } 
        }
    },
    'then': {
        'required': [QUESTION_TYPES_OBJ]
    }
}

# Generic question implementation. Not a class for every question type

@dataclass(frozen=True)
class Question:
    name: str
    type_: QuestionType

@dataclass(frozen=True)
class SpecificQuestion(Question):
    question: str

@dataclass(frozen=True)
class NQuestion(Question):
    question_list: List[str]

    def get_names(self) -> List[str]:
        return [f'{self.name} {q}' for q in self.question_list]

@dataclass(frozen=True)
class NSpecificQuestion(SpecificQuestion):
    question_list: List[str]

def parse_questions_from_json_dict(json_dict: Dict) -> Tuple[Question]:
    jsonschema.validate(json_dict, JSON_SCHEMA)
    questions = json_dict[QUESTIONS]
    question_list = list()
    rate3_questions = None
    for q in questions:
        name = q[QUESTION_NAME]
        type_ = QUESTION_NAME_TO_TYPE[q[QUESTION_TYPE]]
        question = None
        if QUESTION_DESC in q:
            description = q[QUESTION_DESC]
            question = SpecificQuestion(name, type_, description)
        elif type_ == QuestionType.RATE_3:
            if rate3_questions is None:
                rate3_questions = (
                    json_dict[QUESTION_TYPES_OBJ][QUESTION_TYPE_3][QUESTIONS]
                )
            question = NQuestion(name, type_, rate3_questions)
        else:
            question = Question(name, type_)
        question_list.append(question)
    return tuple(question_list)

def load_questions(json_filename) -> Tuple[Question]:
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            json_path = Path(sys.executable).parent.joinpath(json_filename)
        else:
            # we are running in a normal Python environment
            json_path = Path.cwd() / json_filename
        
        jsonfile = open(json_path, encoding='utf-8')
        questions_dict = json.load(jsonfile)
        questions = parse_questions_from_json_dict(questions_dict)
        return questions


def types_from_questions(questions: Tuple[Question]) -> Tuple[Question]:
    types = (q.type_ for q in questions)
    return tuple(types)

def real_question_len(question_types: Tuple[QuestionType]) -> int:
    amount = 0
    for type_ in question_types:
        if type_ == QuestionType.RATE_3:
            amount += 3
        else: 
            amount += 1
    return amount

def get_all_question_names(questions: Tuple[Question]) -> Tuple[str]:
    names = []
    for q in questions:
        if q.type_ == QuestionType.RATE_3:
            for q_str in q.question_list:
                names.append(q.name + ' ' + q_str)
        else:
            names.append(q.name)
    return tuple(names)

def to_only_questions(questions: Tuple[Question]) -> Tuple[Question]:
    filtered_questions = []
    for q in questions:
        if q.type_ == QuestionType.RATE_3:
            for q_question in q.question_list:
                new_q = Question(
                    name=f'{q.name} {q_question}',
                    type_=QuestionType.RATE
                )
                filtered_questions.append(new_q)
        else:
            filtered_questions.append(q)
    return tuple(filtered_questions)

"""   
class JSONMissingEntryError(Exception):
    def __init__(self, missing_entry: str):
        self.missing_entry = missing_entry
        self.message = f'{missing_entry} is not defined in the json file.'

class JSONInvalidEntryError(Exception):
    def __init__(self, question_pos: int, question):
        self.missing_entry = missing_entry
        self.message = f'{missing_entry} is not defined in the json file.'


class JSONMissingQuestionEntryError(Exception):
    def __init__(self, missing_entry: str):
        self.missing_entry = missing_entry
        self.message = f'{missing_entry} is not defined in "{QUESTIONS}"".'


class JSONInvalidType(Exception):
    def __init__(self, type_in_json: str):
        self.type_in_json = type_in_json
        self.message = f'{type_in_json} is not a defined question type.'

class JSONNoQuestionsError(Exception):
    def __init__(self):
        self.message = 'No questions in the json file.'
"""