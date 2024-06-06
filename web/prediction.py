import fastapi
from pydantic import BaseModel
from typing import Tuple
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from joblib.memory import Memory
import data.fake_data
import pickle
import numpy as np
import data.fake_data.fake_ml as ml
from data.fake_data.fake_orm import curs, fake_get_prices

from sqlite3 import Cursor

router = APIRouter(prefix='/predict')


class Prediction(BaseModel):
    answer: Tuple[float, ...]


class Request(BaseModel):
    gun_name: str

def get_db():
    return curs

@router.get("/{name}")
async def get_pred(name, cursor: Cursor = Depends(get_db)):
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
        model = pickle.loads(f)
    Y = model.predict(data)
    #graphic = model.plot(data)

    return Y



