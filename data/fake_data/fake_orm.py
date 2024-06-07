import asyncio
import os.path
import sqlite3
import pandas as pd
import numpy as np
import pickle
from os import path
db_path = os.path.join(os.path.curdir, "/my_database.db")
connection = sqlite3.connect(db_path)

curs = connection.cursor()

def insert_listing():
    datas = [np.sin(i/10) + np.random.random()/10 for i in range(0, 100)]
    df = pd.DataFrame({"cost": datas, "time": [i for i in range(0, 100)]})
    insert_query = '''insert into Listings (name, ml_weights, pd_data) values(
                 ?, ?, ?)
                 '''
    curs.execute(insert_query, ("AWP", None, pickle.dumps(df)))
    connection.commit()

def insert_all():
    names = ["AWP", "AK", "Deagle", "pp", "Berettas", "M4", "Benelli", "Sg708", "Scout"]
    datas = [[np.sin(i/10) + np.random.random()/10 + j for i in range(0, 100)] for j in range(0, 10)]

    for j, i in enumerate(names):

        if len(a := curs.execute(f"SELECT * FROM Listings WHERE name='{i}'").fetchall()) == 0:
            insert_query = '''insert into Listings (name, ml_weights, pd_data) values(
                             ?, ?, ?)
                             '''
            df = pd.DataFrame({"cost": datas[j], "time": [i for i in range(0, 100)]})
            curs.execute(insert_query, (i, None, pickle.dumps(df)))
            connection.commit()
        print(a)

def delete_listing():
    curs.execute("delete from Listings where name='AWP'")
    connection.commit()


async def fake_get_prices(curs: sqlite3.Cursor, name: str):
    try:
        a = curs.execute(f'''select pd_data, ml_weights from Listings where name="{name}"
        ''').fetchall()[0]
    except IndexError as err:
        return "Not really name"

    return a

async def fake_get_all(curs: sqlite3.Cursor):
    try:
        b = curs.execute("SELECT name FROM Listings").fetchall()
        b = [i[0] for i in b]
        return b
    except:
        return


if __name__ == "__main__":
    #insert_listing()
    #insert_all()

    #delete_listing()
    loop = asyncio.get_event_loop()
    #print(loop.run_until_complete(fake_get_prices(curs, "AK")))
    print(loop.run_until_complete(fake_get_all(curs)))