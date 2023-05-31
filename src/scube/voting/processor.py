from typing import List, Tuple
import pandas as pd
import numpy as np

SORT_BY = 'Gruppe'
GENDER_COLUMN = 'Geschlecht'

class VoteTransformer:
    def __init__(self, votes_df: pd.DataFrame, rate_names: List[str]):
        self.rate_names = rate_names
        self.sorted_votes = sort_by_column(votes_df, SORT_BY)
        self.male_split, self.female_split = split_by_gender(self.sorted_votes)
        self.all_sorted_rating = filter_rate_votes(self.sorted_votes, rate_names)
        self.male_rating = filter_rate_votes(self.male_split, rate_names)
        self.female_rating = filter_rate_votes(self.female_split, rate_names)
    
    def get_means(self):
        all_mean = mean_from_rate_votes(self.all_sorted_rating)
        male_mean = mean_from_rate_votes(self.male_rating)
        female_mean = mean_from_rate_votes(self.female_rating)
        means = concencate_dfs(all_mean, male_mean, female_mean, names=['gesamt', 'männlich', 'weiblich'])
        return means.T

    def get_group_means(self):
        group_names, group_dfs = split_by_column(self.sorted_votes, 'Gruppe')
        group_rate_dfs = map(lambda df: filter_rate_votes(df, self.rate_names), group_dfs)
        #group_histogram_dfs = list(map(lambda df: filter_rate_votes(df, self.rate_names), group_rate_dfs))
        group_mean_dfs = list(map(lambda df: mean_from_rate_votes(df), group_rate_dfs))
        group_means = concencate_df_list(group_mean_dfs, names=group_names)
        return group_means.T

    """
    def get_histogram(self):
        full_histogram = histogram_from_rate_votes(self.all_sorted_rating)
        m_histogram = histogram_from_rate_votes(self.male_rating)
        w_histogram = histogram_from_rate_votes(self.female_rating)

        #histograms = concencate_dfs(full_histogram, m_histogram, w_histogram, names=['gesamt', 'männlich', 'weiblich'])
        return full_histogram, m_histogram, w_histogram
    """

    def get_histogram(self):
        full_histogram = histogram_from_rate_votes(self.all_sorted_rating)
        m_histogram = histogram_from_rate_votes(self.male_rating)
        w_histogram = histogram_from_rate_votes(self.female_rating)
        histograms = {}
        for index in full_histogram.index:
            full_rate_histogram = full_histogram.loc[index]
            m_rate_histogram = m_histogram.loc[index]
            w_rate_histogram = w_histogram.loc[index]
            rate_histogram = pd.DataFrame([full_rate_histogram, m_rate_histogram, w_rate_histogram], index=['gesamt', 'männlich', 'weiblich'])
            histograms[index] = rate_histogram
        return histograms
            
def split_by_gender(data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    male_data = data.query('Geschlecht == "männlich"')
    female_data = data.query('Geschlecht == "weiblich"')
    columns = list(data.columns.copy())
    del columns[columns.index('Geschlecht')]
    male_data = male_data.loc[:, columns]
    female_data = female_data.loc[:, columns]
    return male_data, female_data

def split_by_column(data: pd.DataFrame, column_name: str) -> Tuple[List, List[pd.DataFrame]]:
    name, dfs = zip(*data.groupby([column_name]))
    return name, dfs

def sort_by_column(data: pd.DataFrame, column_name: str) -> pd.DataFrame:
    return data.sort_values(by=[column_name])

def filter_rate_votes(df: pd.DataFrame, ratenames: List[str]):
    return df[ratenames]

def mean_from_rate_votes(votes: pd.DataFrame) -> pd.Series:
    mean_df = votes.mean(0)
    return mean_df

def concencate_dfs(*dfs: pd.DataFrame, names: List[str]=None) -> pd.DataFrame:
    assert len(dfs) == len(names)
    rows = None
    if names == None:
        rows = range(len(dfs))
    else:
        rows = names
    concdfs_dict = dict(zip(rows, dfs))
    concdfs = pd.DataFrame(concdfs_dict)
    return concdfs

def concencate_df_list(dfs: List[pd.DataFrame], names: List[str]=None) -> pd.DataFrame:
    assert len(dfs) == len(names)
    rows = None
    if names == None:
        rows = range(len(dfs))
    else:
        rows = names
    concdfs_dict = dict(zip(rows, dfs))
    concdfs = pd.DataFrame(concdfs_dict)
    return concdfs

POSSIBLE_RATES = [1, 2, 3, 4, 5]

def histogram_from_rate_votes(votes: pd.DataFrame):
    col_names = []
    col_histogram_list = []
    for column, data_series in votes.items():
        col_histogram = data_series.value_counts(dropna=True)
        col_names.append(column)
        col_histogram_list.append(col_histogram)
    histogram = pd.DataFrame(col_histogram_list, col_names, POSSIBLE_RATES)
    histogram = histogram.fillna(0)
    
    histogram.astype(int)
    return histogram


