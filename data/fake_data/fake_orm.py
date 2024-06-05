import asyncio
import sqlite3
import pandas as pd
import numpy as np
import pickle

connection = sqlite3.connect('my_database.db')

curs = connection.cursor()

def insert_listing():
    datas = [np.sin(i/10) + np.random.random()/10 for i in range(0, 100)]
    df = pd.DataFrame({"cost": datas, "time": [i for i in range(0, 100)]})
    insert_query = '''insert into Listings (name, ml_weights, pd_data) values(
                 ?, ?, ?)
                 '''
    curs.execute(insert_query, ("AWP", "null", pickle.dumps(df)))
    connection.commit()

def delete_listing():
    curs.execute("delete from Listings where name='AWP'")
    connection.commit()


async def fake_get_prices():
    a, b = curs.execute('''select pd_data, ml_weights from Listings where name="AWP"
    ''').fetchall()[0]
    #print(a)
    return(pickle.loads(a), b)


if __name__ == "__main__":
    insert_listing()
    #delete_listing()
    #loop = asyncio.get_event_loop()
    #print(loop.run_until_complete(fake_get_prices()))