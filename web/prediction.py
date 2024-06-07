import fastapi
from pydantic import BaseModel
from typing import Tuple, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from joblib.memory import Memory
import data.fake_data
import json
import pickle
import numpy as np
import data.fake_data.fake_ml as ml
from data.fake_data.fake_orm import curs, fake_get_prices, fake_get_all
from async_lru import alru_cache

from sqlite3 import Cursor

router = APIRouter(prefix='/predict')


class Prediction(BaseModel):
    answer: List[float]

class NameList(BaseModel):
    answer: List[List[str]]

class Request(BaseModel):
    gun_name: str

def get_db():
    return curs

@alru_cache(maxsize=32)
@router.get("/")
async def get_cur(cursor: Cursor = Depends(get_db)):
    names = await fake_get_all(cursor)
    json_answer = [{"name": j, "id": i} for i, j in enumerate(names)]
    return json_answer


@alru_cache(maxsize=32)
@router.get("/{name}")
async def get_pred(name, cursor: Cursor = Depends(get_db)):
    if name[0] == "\'" and name[-1] == "\'":
        name = name[1:-1]
    data, weights = await fake_get_prices(cursor, name)
    if data is not None:
        print(True)
        data = np.array(pickle.loads(data)["cost"])
    else:
        raise HTTPException(status_code=403)
    if weights is None:
        model = ml.Model(name)
        koef = model.train(data)
        update_query = f"UPDATE Listings SET ml_weights=(?) WHERE name='{name}'"

        cursor.execute(update_query, (pickle.dumps(koef), ))
    else:
        f = cursor.execute(f"SELECT ml_weights FROM Listings where name='{name}'").fetchall()[0]
        model = ml.Model(name)
        model.loads(pickle.loads(f[0]))
        #model = pickle.loads(f[0])
    Y = model.predict_Y(data)
    #graphic = model.plot(data)

    Y_data = [{"cost": data[i], "time": i} for i in range(len(data))]
    Y = [{"cost": Y[i], "time": i} for i in range(len(Y))]

    return {"name": name, "costs": Y_data, "prediction": Y}
