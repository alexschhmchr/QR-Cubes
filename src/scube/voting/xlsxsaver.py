import xlsxwriter as xs
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Dict
import datetime


TABLE_STRIDE = 2
DATA_OFFSET = 1
CHART_OFFSET = 1

BAR_CHART_TYPE = 'bar'
COLUMN_CHART_TYPE = 'column'

DESTINATION_FOLDER = 'Umfragen'

class XlsxSaver:
    def __init__(self, filename: str=None):
        if filename == None:
            time = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')
            destination_folder = Path.home().joinpath('Umfragen')
            destination_folder.mkdir(exist_ok=True, parents=True)
            filename = destination_folder.joinpath(f'umfrage-{time}.xlsx')
        self.writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        self.wb = self.writer.book
        self.histo_name_format = self.wb.add_format({'bold': True})
    
    def save_votes(self, votes: pd.DataFrame, means: pd.DataFrame, group_means: pd.DataFrame, rate_histograms: Dict[str, pd.DataFrame]):
        names = votes.index
        self.create_raw_sheet(votes)
        self.create_mean_sheet(means, group_means)
        self.create_histogram_sheet(rate_histograms, names)
        self.save()

    def save(self):
        # self.writer.save()
        self.writer.close()

    def create_raw_sheet(self, votes: pd.DataFrame):
        votes.to_excel(self.writer, 'Umfragedaten')
        self.insert_dataframes(votes, sheetname='Umfragedaten')

    def create_mean_sheet(self, means: pd.DataFrame, group_means: pd.DataFrame):
        series = self.insert_dataframes(means, group_means, sheetname='Durchschnitt')
        names = ['Insgesamt', 'Pro Gruppe']
        self.insert_chart('Durchschnitt', BAR_CHART_TYPE, names, *series)

    def create_histogram_sheet(self, rate_histograms: Dict[str, pd.DataFrame], names: List[str]):
        names = list(rate_histograms.keys())
        dfs = rate_histograms.values()
        series = self.insert_dataframes(*dfs, sheetname='Histogramm', names=names)
        self.insert_chart('Histogramm', COLUMN_CHART_TYPE, names, *series, chart_per_series=True)

    def insert_dataframes(self, *dfs: pd.DataFrame, sheetname: str, names: List[str]=None, draw_charts:bool=False):
        sheet_pointer = 0
        series = []
        for i, df in enumerate(dfs):
            df_data_rows, df_data_cols = df.shape
            table_rows = df_data_rows + DATA_OFFSET
            table_cols = df_data_cols + DATA_OFFSET

            val_rowstart = sheet_pointer+DATA_OFFSET
            val_rowend = val_rowstart
            val_colstart = DATA_OFFSET
            val_colend = DATA_OFFSET+df_data_cols
            cat_rowstart = sheet_pointer
            cat_rowend = cat_rowstart
            cat_colstart = DATA_OFFSET
            cat_colend = DATA_OFFSET + df_data_cols

            df.to_excel(self.writer, sheetname, startrow=sheet_pointer)

            if names is not None:
                sheet = self.wb.get_worksheet_by_name(sheetname)
                sheet.write(sheet_pointer, 0, names[i], self.histo_name_format)

            sheet_pointer += table_rows + TABLE_STRIDE
            table_series = {}
            for i in range(df_data_rows):
                seriesname = str(df.index[i])
                series_info = {
                    'values': [sheetname, val_rowstart+i, val_colstart, val_rowend+i, val_colend],
                    'categories': [sheetname, cat_rowstart, cat_colstart, cat_rowend, cat_colend],
                    'name': seriesname
                }
                table_series[seriesname] = series_info
            series.append(table_series)
        return series

    def insert_chart(self, sheetname: str, chart_type: str, names: List, *series, chart_per_series: bool=False):
        sheet_row_pointer = CHART_OFFSET
        sheet_col_pointer = 0
        sheet = self.wb.get_worksheet_by_name(sheetname)
        for histo_name, s in zip(names, series):
            if chart_per_series:
                colpos = None
                info_writen = False
                for name, series_info in s.items():
                    chart = self.wb.add_chart({'type': chart_type})
                    if colpos == None:
                        table_colend = series_info['values'][4]
                        colpos = table_colend + TABLE_STRIDE
                        sheet.write(sheet_row_pointer -1, colpos, histo_name, self.histo_name_format) 
                    chart.add_series(series_info)       
                    sheet.insert_chart(sheet_row_pointer, colpos+sheet_col_pointer, chart)
                    sheet_col_pointer += 8
                sheet_row_pointer += 6
                sheet_col_pointer = 0
            else:
                chart = self.wb.add_chart({'type': chart_type})
                colpos = None
                for name, series_info in s.items():
                    if colpos == None:
                        table_colend = series_info['values'][4]
                        colpos = table_colend + TABLE_STRIDE
                    chart.add_series(series_info)
                sheet.insert_chart(sheet_row_pointer, colpos, chart)
            sheet_row_pointer += 15