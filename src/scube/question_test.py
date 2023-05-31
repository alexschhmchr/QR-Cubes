import unittest
from scube.question import *

class QuestionTypeTest(unittest.TestCase):
    def test_init_from_value(self):
        result = QuestionType('geschlecht')
        expected = QuestionType.GENDER
        self.assertEqual(result, expected)

    @unittest.expectedFailure
    def test_fail_init_from_value(self):
        result = QuestionType('fail')

class QuestionTest(unittest.TestCase):
    def test_from_dict(self):
        result = Question.from_dict({
            'name': 'Geschlecht',
            'typ': 'geschlecht',
            'frage': 'Welches Geschlecht hast du?'
        })
        expected = Question('Geschlecht', QuestionType.GENDER, 'Welches Geschlecht hast du?')
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
        