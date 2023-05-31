import datetime
import sqlite3
import sys
from pathlib import Path
from os import PathLike


import pandas as pd


DB_NAME = 'survey.db'


def save_df_to_sql(db_path: PathLike, df: pd.DataFrame):
    conn = sqlite3.connect(db_path)
    date_str = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')
    df.to_sql(date_str, conn)
    conn.close()