import fastapi
import torch
from pydantic import BaseModel
from typing import Tuple, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from joblib.memory import Memory
import data.fake_data
import json
import pandas as pd

import numpy as np
import data.fake_data.fake_ml as ml
from data.fake_data.fake_orm import curs, fake_get_prices, fake_get_all, fake_get_img_href
from async_lru import alru_cache

import boto3
from datetime import timedelta
from datetime import datetime

router = APIRouter(prefix='/predict')

class Prediction(BaseModel):
    answer: List[float]

class NameList(BaseModel):
    answer: List[List[str]]

class Request(BaseModel):
    gun_name: str

def get_db():
    return curs

model = ml.Model()
session = boto3.session.Session()
s3 = session.client(service_name='s3',endpoint_url='https://storage.yandexcloud.net')

@router.get("/")
async def get_cur(
        #cursor: Cursor = Depends(get_db)
):
    objects = list()
    for key in s3.list_objects(Bucket='test-actions')['Contents']:
        name = key["Key"]
        if name.startswith("test/") and name != "test/":
            objects.append(name[5:])

    json_answer = [{"name": j, "id": i} for i, j in enumerate(objects)]
    return json_answer


@alru_cache(maxsize=128, ttl=60)
@router.get("/{name}")
async def get_pred(
        name,
        #cursor: Cursor = Depends(get_db)
):
    if name[0] == "\'" and name[-1] == "\'":
        name = name[1:-1]

    print('test/'+name)
    get_object_response = s3.get_object(Bucket='test-actions', Key='test/'+name)
    df = pd.read_csv(get_object_response['Body'], sep=";")
    data = df['<CLOSE>'].to_numpy()

    df['<DATE>'] = pd.to_datetime(df['<DATE>']).dt.date
    df['<TIME>'] = pd.to_datetime(df['<TIME>']).dt.time

    # Объединяем `date` и `time` в одном объекте datetime
    combined = np.array([datetime.combine(d, t) for d, t in zip(df['<DATE>'], df['<TIME>'])])

    print(data)
    Y = model.predict_y(torch.tensor(data))[0][0].tolist()
    new_dates = [combined[-1] + timedelta(hours=i) for i in range(1, len(Y) + 1)]
    print(Y)
    #graphic = model.plot(data)

    Y_data = [{"cost": data[i], "time": combined[i]} for i in range(len(data))]
    Y = [{"cost": Y[i], "time": new_dates[i]} for i in range(len(Y))]

    return {"name": name, "costs": Y_data, "prediction": Y, "img": ''+'/62fx62f', 'href': ''}
