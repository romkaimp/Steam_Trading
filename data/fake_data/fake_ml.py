import asyncio
import pickle

from data.fake_data.fake_orm import fake_get_prices
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import RidgeCV, LassoCV, LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingRandomSearchCV
from sklearn.ensemble import StackingRegressor, GradientBoostingRegressor
from matplotlib import pyplot as plt
from matplotlib.pyplot import imsave

from sklearn.metrics import r2_score

import numpy as np
import joblib


class Model:
    def __init__(self, name):
        self.name = name
        self.model = StackingRegressor(estimators=[('ridge', RidgeCV()),
                                      ('lasso', LassoCV(random_state=10)),
                                      ('lr', LinearRegression()),
                                      ],
                          final_estimator=GradientBoostingRegressor(n_estimators=25, subsample=0.5))

    def loads(self, model):
        self.model = model

    def train(self, data):
        X = np.array([data[i:i + 20] for i in range(data.size - 20)])
        Y = np.array([data[i] for i in range(20, data.size)])
        self.model.fit(X, Y)

        return self.model


    def predict_Y(self, data):
        #return data[data.size-20 : data.size]
        X_new = np.copy(data[data.size-20 : data.size]).reshape(1, -1)
        #return type(data)
        Y_preds = []
        # print(X_new)
        for j in range(20):
            X_pred = np.copy(X_new.reshape(1, -1))
            X_add = self.model.predict(X_pred)
            Y_preds.append(X_add[0])
            X_new = np.append(X_new, X_add)
            X_new = np.copy(X_new[1:])

        return Y_preds

    def plot(self, data):
        fig = plt.figure(1)
        ax = fig.add_subplot()
        Y_preds = self.predict_Y(data)
        ax.plot([i for i in range(len(data))], data)
        ax.plot([i for i in range(len(data), len(data)+20)], Y_preds[:20], color="red")
        plt.savefig(f"{self.name}.jpg")
        return f"{self.name}.jpg"


