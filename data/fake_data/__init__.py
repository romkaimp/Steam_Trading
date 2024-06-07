import sqlite3
import os
db_path = os.path.join(os.path.curdir, "/my_database.db")
connection = sqlite3.connect(db_path)

curs = connection.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS Listings (
name TEXT PRIMARY KEY,
ml_weights BLOB,
pd_data BLOB)""")
connection.commit()