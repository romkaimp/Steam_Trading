import sqlite3
connection = sqlite3.connect('C:/Users/Kuzne/PycharmProjects/Steam_Trading/data/fake_data/my_database.db')

curs = connection.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS Listings (
name TEXT PRIMARY KEY,
ml_weights BLOB,
pd_data BLOB)""")
connection.commit()