import unittest
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

from . import processor

class ProcessorTestCase(unittest.TestCase):

    def test_filter_rate_votes(self):
        data = [
            ['männlich', 0, 2, 5],
            ['weiblich', 2, 1, 3],
            ['männlich', 3, 2, 1]
        ]
        columns = ['Geschlecht', 1, 2, 3]
        df = pd.DataFrame(data, columns=columns)
        rate_columns = columns[1:]
        filtered_df = processor.filter_rate_votes(df, rate_columns)
        expected_data = [
            [0, 2, 5],
            [2, 1, 3],
            [3, 2, 1]
        ]
        expected_df = pd.DataFrame(expected_data, columns=rate_columns)
        assert_frame_equal(expected_df, filtered_df, check_column_type=False)

    def test_split_by_gender(self):
        data = [
            ['männlich', 0, 2, 5],
            ['weiblich', 2, 1, 3],
            ['männlich', 3, 2, 1]
        ]
        df = pd.DataFrame(data, columns=['Geschlecht', 1, 2, 3])
        m_df, w_df = processor.split_by_gender(df)
        expected_m_df = pd.DataFrame({1: [0, 3], 2: [2, 2], 3: [5, 1]}, index=[0, 2])
        expected_w_df = pd.DataFrame({1: [2], 2: [1], 3: [3]}, index=[1])
        assert_frame_equal(expected_m_df, m_df)
        assert_frame_equal(expected_w_df, w_df)

    def test_split_by_column(self):
        data = [
            ['männlich', 0, 2, 5],
            ['weiblich', 2, 1, 3],
            ['männlich', 3, 2, 1]
        ]
        columns = ['Geschlecht', 1, 'Gruppe', 2]
        df = pd.DataFrame(data, columns=columns)
        group_names, grouped_dfs = processor.split_by_column(df, 'Gruppe')
        expected_group1_data = [
            ['weiblich', 2, 1, 3]
        ]
        expected_group2_data = [
            ['männlich', 0, 2, 5],
            ['männlich', 3, 2, 1]
        ]
        expected_group1_df = pd.DataFrame(expected_group1_data, columns=columns, index=[1])
        expected_group2_df = pd.DataFrame(expected_group2_data, columns=columns, index=[0, 2])
        expected_dfs = [expected_group1_df, expected_group2_df]
        self.assertEqual(len(expected_dfs), len(grouped_dfs))
        for i in range(len(expected_dfs)):
            assert_frame_equal(expected_dfs[i], grouped_dfs[i])

    def test_sort_by_column(self):
        data = [
            ['männlich', 0, 2, 5],
            ['weiblich', 2, 1, 3],
            ['männlich', 3, 2, 1]
        ]
        columns = ['Geschlecht', 1, 'Gruppe', 2]
        df = pd.DataFrame(data, columns=columns)
        sorted_df = processor.sort_by_column(df, 'Gruppe')
        expected_data = [
            ['weiblich', 2, 1, 3],
            ['männlich', 0, 2, 5],
            ['männlich', 3, 2, 1]
        ]
        expected_df = pd.DataFrame(expected_data, columns=columns, index= [1, 0, 2])
        assert_frame_equal(expected_df, sorted_df)

    def test_mean_dfs(self):
        data = [
            ['männlich', 0, 2, 5],
            ['weiblich', 2, 1, 3],
            ['männlich', 3, 2, 1]
        ]
        columns = ['Geschlecht', 1, 2, 3]
        df = pd.DataFrame(data, columns=columns)
        rate_columns = columns[1:]
        votes = df[rate_columns]
        mean_series = processor.mean_from_rate_votes(votes)
        expected_means = [5/3, 5/3, 3]
        expected_mean_series = pd.Series(expected_means, rate_columns)
        assert_series_equal(expected_mean_series, mean_series, check_index_type=False)

    def test_histogram_from_rate_votes(self):
        data = [
            [1, 2, 5],
            [2, 1, 3],
            [3, 2, 1]
        ]
        columns = ['A', 'B', 'C']
        df = pd.DataFrame(data, columns=columns)
        histogram = processor.histogram_from_rate_votes(df)
        histogram_list = [
            [1, 1, 1, 0, 0],
            [1, 2, 0, 0, 0],
            [1, 0, 1, 0, 1]
        ]
        expected_histogram = pd.DataFrame(histogram_list, columns, [1, 2, 3, 4, 5])
        assert_frame_equal(expected_histogram, histogram, check_dtype=False)

class VoteTransformerTestCase(unittest.TestCase):
    def setUp(self):
        """data = [
            ['männlich', 2, 5, 2],
            ['weiblich', 1, 4, 2],
            ['weiblich', 1, 3, 2],
            ['weiblich', 2, 2, 3],
            ['männlich', 1, 1, 3],    
            ['männlich', 2, 0, 3]
        ]"""
        data = [
            ['männlich', 'Gruppe 2', 5, 2],
            ['weiblich', 'Gruppe 1', 4, 2],
            ['weiblich', 'Gruppe 1', 3, 2],
            ['weiblich', 'Gruppe 2', 2, 3],
            ['männlich', 'Gruppe 1', 1, 3],    
            ['männlich', 'Gruppe 2', 0, 3]
        ]
        columns = ['Geschlecht', 'Gruppe', 3, 4]
        df = pd.DataFrame(data, columns=columns)
        self.vt = processor.VoteTransformer(df, [3, 4])

    def test_get_means(self):
        means = self.vt.get_means()
        expected_data = [
            [2.5, 2, 3],
            [2.5, 8/3, 7/3]
        ]
        index = [3, 4]
        columns = ['gesamt', 'männlich', 'weiblich']
        expected_means = pd.DataFrame(expected_data, index=index, columns=columns)
        assert_frame_equal(expected_means.T, means, check_index_type=False, check_column_type=False)

    def test_get_group_means(self):
        group_means = self.vt.get_group_means()
        expected_data = [
            [8/3, 7/3],
            [7/3, 8/3]
        ]
        columns=['Gruppe 1', 'Gruppe 2']
        index=[3, 4]
        expected_group_means = pd.DataFrame(expected_data, index=index, columns=columns)
        assert_frame_equal(expected_group_means.T, group_means, check_index_type=False, check_column_type=False)

    """def test_get_histogram(self):
        full_histogram, m_histogram, w_histogram = self.vt.get_histogram()
        expected_full_data = [
            [1, 1, 1, 1, 1],
            [0, 3, 3, 0, 0]
        ]
        expected_m_data = [
            [1, 0, 0, 0, 1],
            [0, 1, 2, 0, 0]
        ]
        expected_w_data = [
            [0, 1, 1, 1, 0],
            [0, 2, 1, 0, 0]
        ]
        index = [3, 4]
        columns = [1, 2, 3, 4, 5]
        expected_full_histogram = pd.DataFrame(expected_full_data, index=index, columns=columns)
        expected_m_histogram = pd.DataFrame(expected_m_data, index=index, columns=columns)
        expected_w_histogram = pd.DataFrame(expected_w_data, index=index, columns=columns)
        assert_frame_equal(expected_full_histogram, full_histogram, check_index_type=False, check_dtype=False)
        assert_frame_equal(expected_m_histogram, m_histogram, check_index_type=False, check_dtype=False)
        assert_frame_equal(expected_w_histogram, w_histogram, check_index_type=False, check_dtype=False)
    """

    def test_get_histogram_2(self):
        histograms = self.vt.get_histogram()
        histogram_2 = histograms[3]
        print(histogram_2)
        histogram_3 = histograms[4]
        columns = [1, 2, 3, 4, 5]
        index = ['gesamt', 'männlich', 'weiblich']
        expected_2_data = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [0, 1, 1, 1, 0]
        ]
        expected_3_data = [
            [0, 3, 3, 0, 0],
            [0, 1, 2, 0, 0],
            [0, 2, 1, 0, 0]
        ]
        expected_2_df = pd.DataFrame(expected_2_data, index=index, columns=columns)
        expected_3_df = pd.DataFrame(expected_3_data, index=index, columns=columns)
        assert_frame_equal(expected_2_df, histogram_2, check_index_type=False, check_dtype=False)
        assert_frame_equal(expected_3_df, histogram_3, check_index_type=False, check_dtype=False)
        

if __name__ == "__main__":
    unittest.main()
    