import asyncio
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from chronos import ChronosPipeline

import numpy as np
import joblib


class Model:
    def __init__(self, prediction_length = 12):
        self.prediction_length = 12
        self.model = ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-tiny",
#            device_map="cuda",
            torch_dtype=torch.bfloat16,
        )

    def loads(self, model):
        self.model = model

    def predict_y(self, x):
        return self.model.predict(x, self.prediction_length)


