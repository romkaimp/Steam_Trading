import fastapi
from pydantic import BaseModel
from typing import Tuple
from fastapi import APIRouter, Depends
from joblib.memory import Memory

router = APIRouter(prefix='predict/')


class Prediction(BaseModel):
    answer: Tuple[float, ...]


class Request(BaseModel):
    gun_name: str
    user_pass: str
    user_id: str

def get_user_pass(user_id: int):
    pass
def verify_cache(user_pass = Depends()):
    pass

@router.get(f"{id}")
def get_pred(hash: Request = Depends()):
    pass

