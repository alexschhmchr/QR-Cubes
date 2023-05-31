import unittest
from . import manager
from .manager import VoteType, VoteManagerFunctional
from .questions import QuestionType, Question, SpecificQuestion, NQuestion

import pandas as pd
from pandas.testing import assert_frame_equal

class ManagerTestCase(unittest.TestCase):
    def test_parse_aruco_markerid(self):
        cube_id, vote_id = manager.parse_aruco_markerid(34)
        self.assertEqual(5, cube_id)
        self.assertEqual(4, vote_id)


class VotesTestCase(unittest.TestCase):
    def setUp(self):
        questions_len = 3
        self.votes = manager.Votes(questions_len)

    def test_init(self):
        nv_id = manager.NO_VOTE_IDENTFIER
        expected_raw_list = [nv_id, nv_id, nv_id]
        self.assertListEqual(expected_raw_list, self.votes.raw_vote_list)

    def test_set_questions_len(self):
        self.votes.set_questions_len(5)

        expected_raw_vote_list = [manager.NO_VOTE_IDENTFIER] * 5
        self.assertListEqual(expected_raw_vote_list, self.votes.raw_vote_list)

    def test_set_questions_len_running_voting(self):
        self.votes.votes = {
            0: [0, 1, 2]
        }

        self.votes.set_questions_len(5)

        expected_raw_vote_list = [manager.NO_VOTE_IDENTFIER] * 3
        self.assertListEqual(expected_raw_vote_list, self.votes.raw_vote_list)

    # don't change running voting
    """
    def test_set_questions_len(self):
        new_len = 5
        nv_id = manager.NO_VOTE_IDENTFIER
        filled_votes = {
            0: [0, 1, 2],
            1: [2, 1, 0],
            2: [1, 1, 1]
            }
        self.votes.votes = filled_votes

        self.votes.set_questions_len(new_len)

        expected_votes = {
            0: [0, 1, 2, nv_id, nv_id],
            1: [2, 1, 0, nv_id, nv_id],
            2: [1, 1, 1, nv_id, nv_id]
            }
        expected_raw_vote_list = [nv_id, nv_id, nv_id, nv_id, nv_id]
        self.assertListEqual(expected_raw_vote_list, self.votes.raw_vote_list)
        self.assertDictEqual(expected_votes, self.votes.votes)
    """

    """
    def test_get_votes(self):
        questions = [
            (VoteType.GENDER, 'Geschlecht'),
            (VoteType.GROUP, 'Gruppe'),
            (VoteType.RATE, 'Frage1'),
            (VoteType.RATE, 'Frage2')
            ]
        votes = manager.Votes(len(questions))
        votes.votes = {
            0: [1, 0, 2, 3],
            1: [3, 4, 5, 1],
            3: [1, 2, 3, 4]
        }
        result_df = votes.get_votes(questions)
        
        expected_data = [
            ['weiblich', 'Gruppe 3', 2, 3],
            ['männlich', 'Gruppe 4', 1, 3],
            ['weiblich', 'Gruppe 1', 3, 5]
        ]
        _, cols = zip(*questions)
        index = list(votes.votes.keys())
        expected_df = pd.DataFrame(expected_data, columns=cols, index=index)
        assert_frame_equal(expected_df, result_df)
    """
        
    def test_get_votes_2(self):
        rate3_list = ['A', 'B', 'C']
        questions = (
            SpecificQuestion('Geschlecht', QuestionType.GENDER, 'G'),
            SpecificQuestion('Gruppe', QuestionType.GROUP, 'Gruppe'),
            NQuestion('Frage1', QuestionType.RATE_3, rate3_list),
            NQuestion('Frage2', QuestionType.RATE_3, rate3_list)
            )
        votes = manager.Votes(len(questions))
    
        votes.votes = {
            0: [1, 0, 2, 3, 2, 3, 2, 3],
            1: [3, 4, 5, 1, 5, 1, 5, 1],
            3: [1, 2, 3, 4, 3, 4, 3, 4]
        }
        result_df = votes.get_votes(questions)
        
        expected_data = [
            ['weiblich', 'Gruppe 3', 2, 3, 2, 3, 2, 3],
            ['männlich', 'Gruppe 4', 1, 3, 1, 3, 1, 3],
            ['weiblich', 'Gruppe 1', 3, 5, 3, 5, 3, 5]
        ]
        names = (
            'Geschlecht', 
            'Gruppe',
            'Frage1 A',
            'Frage1 B',
            'Frage1 C',
            'Frage2 A',
            'Frage2 B',
            'Frage2 C',
        )
        index = list(votes.votes.keys())
        expected_df = pd.DataFrame(expected_data, columns=names, index=index)
        assert_frame_equal(expected_df, result_df, check_dtype=False)


class VoteManagerTestCase(unittest.TestCase):
    def setUp(self):
        questions = (
            QuestionType.GENDER,
            QuestionType.GROUP,
            QuestionType.RATE,
            QuestionType.RATE)
        self.votemanager = VoteManagerFunctional(questions)
    
    def test_init(self):
        pass

    def test_next_question(self):
        result = self.votemanager.next_question()
        self.assertEqual(1, result)
        self.assertEqual(1, self.votemanager.vote_counter)
        result = self.votemanager.next_question()
        self.assertEqual(2, result)
        self.assertEqual(2, self.votemanager.vote_counter)

    def test_set_question_type_list(self):
        new_questions = [
            QuestionType.GENDER, QuestionType.GROUP,
            QuestionType.RATE, VoteType.RATE,
            VoteType.RATE, VoteType.RATE]
        self.votemanager.set_question_type_list(new_questions)
        self.assertListEqual(new_questions, self.votemanager.question_types)

    def test_process_markerid_gender_unvalid(self):
        result = self.votemanager.process_markerid(32, False)

        self.assertEqual(manager.MarkerType.UNVALID, result)

    def test_process_markerid_group_unvalid(self):
        self.votemanager.next_question()
        result = self.votemanager.process_markerid(31, False)

        self.assertEqual(manager.MarkerType.UNVALID, result)

    def test_process_markerid_rate_no_unvalid(self):
        self.votemanager.next_question()
        self.votemanager.next_question()

        result = self.votemanager.process_markerid(31, False)

        self.assertNotEqual(manager.MarkerType.UNVALID, result)
        
    def test_process_markerid_processed(self):
        self.votemanager.votes.set_vote(5, 0, 0)

        result = self.votemanager.process_markerid(33, False)
        
        self.assertEqual(manager.MarkerType.PROCCESSED, result)

    def test_process_markerid_save(self):
        aruco_markerid = 33
        save_vote = True
        result = self.votemanager.process_markerid(aruco_markerid, save_vote)
        expected_vote_entry = 3 #vote_id
        expected_marker_type_result = manager.MarkerType.VALID
        self.assertEqual(expected_vote_entry, self.votemanager.votes.get_vote(5, 0))
        self.assertEqual(expected_marker_type_result, result)

