# import unittest

# import pandas as pd

# from voting.xlsxsaver import XlsxSaver

# class XlsxsaveTestCase(unittest.TestCase):

#     def test_create_raw_sheet(self):
#         data = [
#             ['männlich', 2, 5, 2],
#             ['weiblich', 1, 4, 2],
#             ['weiblich', 1, 3, 2],
#             ['weiblich', 2, 2, 3],
#             ['männlich', 1, 1, 3],    
#             ['männlich', 2, 0, 3]
#         ]
#         columns = ['Geschlecht', 'Gruppe', 3, 4]
#         df = pd.DataFrame(data, columns=columns)
#         xlsx = XlsxSaver('test_raw.xlsx')
#         xlsx.create_raw_sheet(df)
#         xlsx.save()

#     """def test_create_group_sheet(self):
#         expected_data = [
#             [8/3, 7/3],
#             [7/3, 8/3]
#         ]
#         index=[1, 2]
#         columns=[3, 4]
#         group_means = pd.DataFrame(expected_data, index=index, columns=columns)
#         xlsx = XlsxSaver('test_group.xlsx')
#         xlsx.create_group_sheet(group_means)
#         xlsx.save()"""

#     def test_create_mean_sheet(self):
#         expected_data = [
#             [2.5, 2.5],
#             [2, 8/3],
#             [3, 7/3]
#         ]
#         columns = [3, 4]
#         index = ['gesamt', 'männlich', 'weiblich']
#         means = pd.DataFrame(expected_data, index=index, columns=columns)
#         expected_data = [
#             [8/3, 7/3],
#             [7/3, 8/3]
#         ]
#         columns=[1, 2]
#         index=[3, 4]
#         group_means = pd.DataFrame(expected_data, index=index, columns=columns)
#         xlsx = XlsxSaver('test_mean.xlsx')
#         #xlsx.create_group_sheet(means)
#         xlsx.create_mean_sheet(means, group_means.T)
#         xlsx.save()

#     """def test_create_histogram_sheet(self):
#         expected_full_data = [
#             [1, 1, 1, 1, 1],
#             [0, 3, 3, 0, 0]
#         ]
#         expected_m_data = [
#             [1, 0, 0, 0, 1],
#             [0, 1, 2, 0, 0]
#         ]
#         expected_w_data = [
#             [0, 1, 1, 1, 0],
#             [0, 2, 1, 0, 0]
#         ]
#         index = [3, 4]
#         columns = [1, 2, 3, 4, 5]
#         expected_full_histogram = pd.DataFrame(expected_full_data, index=index, columns=columns)
#         expected_m_histogram = pd.DataFrame(expected_m_data, index=index, columns=columns)
#         expected_w_histogram = pd.DataFrame(expected_w_data, index=index, columns=columns)
#         xlsx = XlsxSaver('test_histogram.xlsx')
#         xlsx.create_histogram_sheet(expected_full_histogram, expected_m_histogram, expected_w_histogram)
#         xlsx.save()"""

#     def test_create_histogram_sheet_2(self):
#         columns = [1, 2, 3, 4, 5]
#         index = ['gesamt', 'männlich', 'weiblich']
#         expected_2_data = [
#             [1, 1, 1, 1, 1],
#             [1, 0, 0, 0, 1],
#             [0, 1, 1, 1, 0]
#         ]
#         expected_3_data = [
#             [0, 3, 3, 0, 0],
#             [0, 1, 2, 0, 0],
#             [0, 2, 1, 0, 0]
#         ]
#         expected_2_df = pd.DataFrame(expected_2_data, index=index, columns=columns)
#         expected_3_df = pd.DataFrame(expected_3_data, index=index, columns=columns)
#         histograms = {
#             3: expected_2_df,
#             4: expected_3_df
#         }
#         xlsx = XlsxSaver('test_histogram2.xlsx')
#         xlsx.create_histogram_sheet(histograms, list(histograms.keys()))
#         xlsx.save()