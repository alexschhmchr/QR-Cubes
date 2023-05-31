import unittest
from . import questions
from .questions import QuestionType, Question, SpecificQuestion, NQuestion
from jsonschema import ValidationError

class QuestionParserTestCase(unittest.TestCase):
    def test_parse_gender_question(self):
        json_dict =  {
            'fragen' : [
                {
                    'name': 'Geschlecht',
                    'typ' : 'geschlecht',
                }
            ]
        }

        result_question_tuple = questions.parse_questions_from_json_dict(
            json_dict)

        expected_question_tuple = (
            Question(name='Geschlecht', type_=QuestionType.GENDER),
        )
        self.assertTupleEqual(expected_question_tuple, result_question_tuple)

    def test_parse_group_question(self):
        json_dict =  {
            'fragen' : [
                {
                    'name': 'Gruppe',
                    'typ' : 'gruppe',
                }
            ]
        }

        result_question_tuple = questions.parse_questions_from_json_dict(
            json_dict)

        expected_question_tuple = (
            Question(name='Gruppe', type_=QuestionType.GROUP),
        )
        self.assertTupleEqual(expected_question_tuple, result_question_tuple)

    def test_parse_rate_question(self):
        json_dict =  {
            'fragen' : [
                {
                    'name': 'Insgesamt',
                    'typ' : 'bewertung',
                }
            ]
        }

        result_question_tuple = questions.parse_questions_from_json_dict(
            json_dict)

        expected_question_tuple = (
            Question(name='Insgesamt', type_=QuestionType.RATE),
        )
        self.assertTupleEqual(expected_question_tuple, result_question_tuple)
    
    def test_parse_rate_n_question(self):
        json_dict =  {
            'fragen' : [
                {
                    'name': 'Eingangshalle',
                    'typ' : 'bewertung3',
                }
            ],
            'fragetypen' : {
                'bewertung3' : {
                    'fragen' : [
                        'Gesamtbewertung',
                        'Interesse',
                        'Verständlichkeit'
                    ]
                }
            }
        }

        result_question_tuple = questions.parse_questions_from_json_dict(
            json_dict)

        expected_question_tuple = (
            NQuestion(name='Eingangshalle', type_=QuestionType.RATE_3,
                     question_list=['Gesamtbewertung', 'Interesse',
                             'Verständlichkeit']
                    ),
        )
        self.assertTupleEqual(expected_question_tuple, result_question_tuple)
        
    def test_parse_specific_question(self):
        json_dict =  {
            'fragen' : [
                {
                    'name': 'Insgesamt',
                    'typ' : 'bewertung',
                    'frage' : 'Wie fandest du den Besuch im DLR_School_Lab '
                              'insgesamt?'
                }
            ]
        }

        result_question_tuple = questions.parse_questions_from_json_dict(
            json_dict)

        expected_question_tuple = (
            SpecificQuestion(name='Insgesamt', type_=QuestionType.RATE, 
                             question='Wie fandest du den Besuch im '
                             'DLR_School_Lab insgesamt?'),
        )
        self.assertTupleEqual(expected_question_tuple, result_question_tuple)

    def test_parse_question_missing_entry(self):
        json_dict = {}

        with self.assertRaises(ValidationError):
            questions.parse_questions_from_json_dict(
            json_dict)

    def test_parse_question_missing_name_entry(self):
        json_dict = {
            'fragen' : [
                {
                    'typ': 'bewertung'
                }
            ]
        }

        with self.assertRaises(ValidationError):
            questions.parse_questions_from_json_dict(json_dict)

    def test_parse_question_missing_typ_entry(self):
        json_dict = {
            'fragen' : [
                {
                    'name': 'Frage',
                }
            ]
        }

        with self.assertRaises(ValidationError):
            questions.parse_questions_from_json_dict(
            json_dict)

    def test_parse_question_missing_no_entries(self):
        json_dict = {
            'fragen' : [
                {}
            ]
        }

        with self.assertRaises(ValidationError):
            questions.parse_questions_from_json_dict(
            json_dict)
    
    
    def test_parse_question_missing_question_entry(self):
        json_dict = {
            'fragen' : [
                {
                    'name': 'Frage',
                    'typ': 'bewertung3'
                }
            ]
        }
        with self.assertRaises(ValidationError):
            questions.parse_questions_from_json_dict(
            json_dict)
    
    def test_parse_question_no_questions(self):
        json_dict = {
            'fragen' : [
            ]
        }
        with self.assertRaises(ValidationError):
            questions.parse_questions_from_json_dict(
            json_dict)

    def test_parse_question_rate_3_with_desc(self):
        json_dict = {
            'fragen' : [
                {
                    'name': 'Frage',
                    'typ': 'bewertung3',
                    'frage': 'Test'
                }
            ],
            "fragetypen" : {
                "bewertung3" : {
                    "fragen" : [
                        "Gesamtbewertung", "Interesse",
                        "Verständlichkeit"
                    ]
                }
            }
        }

        with self.assertRaises(ValidationError):
            questions.parse_questions_from_json_dict(
            json_dict)

    def test_load_questions(self):
        self.assertTrue(True)

    def test_types_from_questions(self):
        qs = (
            SpecificQuestion('Insgesamt', QuestionType.RATE, 'Insgesamt?'),
            Question('Geschlecht', QuestionType.GENDER),
            Question('Gruppe', QuestionType.GROUP)
            )

        q_types = questions.types_from_questions(qs)

        expected_types = (
            QuestionType.RATE,
            QuestionType.GENDER,
            QuestionType.GROUP
        )
        self.assertTupleEqual(expected_types, q_types)

    def test_real_question_len(self):
        q_types = (
            QuestionType.GENDER,
            QuestionType.RATE_3,
            QuestionType.RATE_3,
            QuestionType.RATE
        )

        amount = questions.real_question_len(q_types)

        self.assertEqual(8, amount)

    def test_get_all_question_names(self):
        rate3_list = [
            'Gesamtbewertung',
            'Interesse',
            'Verständlichkeit'
            ]
        qs = (
            SpecificQuestion('Insgesamt', QuestionType.RATE, 'Insgesamt?'),
            Question('Geschlecht', QuestionType.GENDER),
            NQuestion('BewertungN1', QuestionType.RATE_3, rate3_list),
            Question('Gruppe', QuestionType.GROUP),
            NQuestion('BewertungN2', QuestionType.RATE_3, rate3_list)
            )

        names = questions.get_all_question_names(qs)

        expected_names = (
            'Insgesamt',
            'Geschlecht',
            'BewertungN1 Gesamtbewertung',
            'BewertungN1 Interesse',
            'BewertungN1 Verständlichkeit',
            'Gruppe',
            'BewertungN2 Gesamtbewertung',
            'BewertungN2 Interesse',
            'BewertungN2 Verständlichkeit',
        )
        self.assertTupleEqual(expected_names, names)

    def test_to_only_questions(self):
        rate3_list = [
            'Gesamtbewertung',
            'Interesse',
            'Verständlichkeit'
            ]
        qs = (
            SpecificQuestion('Insgesamt', QuestionType.RATE, 'Insgesamt?'),
            Question('Geschlecht', QuestionType.GENDER),
            NQuestion('BewertungN1', QuestionType.RATE_3, rate3_list),
            Question('Gruppe', QuestionType.GROUP),
            NQuestion('BewertungN2', QuestionType.RATE_3, rate3_list)
            )

        only_qs = questions.to_only_questions(qs)

        expected_only_qs = (
            SpecificQuestion('Insgesamt', QuestionType.RATE, 'Insgesamt?'),
            Question('Geschlecht', QuestionType.GENDER),
            Question('BewertungN1 Gesamtbewertung', QuestionType.RATE),
            Question('BewertungN1 Interesse', QuestionType.RATE),
            Question('BewertungN1 Verständlichkeit', QuestionType.RATE),
            Question('Gruppe', QuestionType.GROUP),
            Question('BewertungN2 Gesamtbewertung', QuestionType.RATE),
            Question('BewertungN2 Interesse', QuestionType.RATE),
            Question('BewertungN2 Verständlichkeit', QuestionType.RATE),
            )
        self.assertTupleEqual(expected_only_qs, only_qs)

class QuestionTestCase(unittest.TestCase):

    def test_get_names(self):
        q_list = ['A', 'B', 'C']
        nq = NQuestion('?', QuestionType.RATE_3, q_list)
        
        names = nq.get_names()
        
        expected_names = ['? A', '? B', '? C']
        self.assertListEqual(expected_names, names)

