# import datetime
# from pathlib import Path
# import sqlite3
# import unittest

# from pandas import DataFrame

# import voting.sql as sql


# class SQLTestCase(unittest.TestCase):

#     def test_save_df_to_sql(self):
#         db_path = Path('test.db')
#         test_df = DataFrame([
#             [True, False],
#             [False, False]
#         ], columns=['A', 'B'])
    
#         sql.save_df_to_sql(db_path, test_df)

#         conn = sqlite3.connect(db_path)
#         c = conn.cursor()
#         c.execute("SELECT name FROM sqlite_master WHERE type='table'ORDER BY name;")
#         table_result = c.fetchall()
#         tablename = table_result[0][0]
#         c.execute(f"SELECT * FROM '{tablename}';")
#         vote_result = c.fetchall()
#         c.execute(f"PRAGMA table_info('{tablename}')")
#         print(c.fetchall())

#         date = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')
#         print(vote_result)

#         conn.close()
#         db_path.unlink()

#         self.assertEqual(tablename, date)

