import asyncio

from sklearn.preprocessing import QuantileTransformer, MinMaxScaler
from numpy import log
from pmdarima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX

from keras.src.layers import GRU, Dense, Input
from keras.src import Sequential, callbacks
from keras.src.metrics import MeanSquaredError
from typing import Tuple
import numpy as np
import data.orm.async_orm as orm

"https://vc.ru/u/1389654-machine-learning/580239-prognozirovanie-vremennyh-ryadov-kriptovalyut-dlya-chaynikov"
NEW_VAL_COUNT = 30
#sarimax_param = auto_arima(y_train, exogenous=X_train, m=7, start_p=0, d=1, start_q=0, start_P=0, D=1, start_Q=0, max_p=3, max_q=1, max_P=3, max_Q=1, trace=True, seasonal=True)
#model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 1))
class GRUModel:
    def __init__(self):
        #print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
        self.callbacks = [callbacks.EarlyStopping(patience=2)]
        self.model = Sequential([Input((20, 1), 1),
                                 GRU(128, return_sequences=True),
                                 GRU(64, return_sequences=False),
                                 Dense(25),
                                 Dense(1)])

        #TODO добавить коллбэк для переменного learning rate для обучения модели

    async def initialize_weights(self, name):
        self.name = name

        ml_weights, new_values = await orm.async_ml_weights_values(name=self.name)
        if ml_weights is not None:
            self.model.load_weights(ml_weights, skip_mismatch=False)
        while new_values > NEW_VAL_COUNT:
            data = await orm.async_select_ts(name=self.name)
            x_train = []
            y_train = []
            X = np.array(data["cost"]).reshape(len(data["cost"]), 1)

            X = X[len(X)-new_values-min(20, len(X)-new_values):len(X)-new_values-min(20, len(X)-new_values)+NEW_VAL_COUNT, :]
            for i in range(20, len(X)-1):
                x_train.append(X[i-20:i, 0])
                y_train.append(X[i, 0])

            x_train, y_train = np.array(x_train), np.array(y_train)
            x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
            self.model.compile(optimizer='adam', loss='mean_squared_error', metrics=[MeanSquaredError()])
            self.model.fit(x_train, y_train, batch_size=5, epochs=20, callbacks=self.callbacks)
            weights = self.model.save_weights
            await orm.async_update_weight(name=self.name, weights=weights)
            new_values -= NEW_VAL_COUNT
        return None

    async def predict(self, name) -> Tuple[float, ...]:
        self.name = name
        ml_weights, new_values = await orm.async_ml_weights_values(name=self.name)
        if ml_weights is not None:
            self.model.load_weights(ml_weights, skip_mismatch=False)

def get_values():
    pass


def update_weights():
    pass


def predict():
    pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    name = "USP-S | Jawbreaker (Minimal Wear)"
    model = GRUModel()
    loop.run_until_complete(model.initialize_weights(name))
