import asyncio
from data.fake_data.fake_orm import fake_get_prices
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import RidgeCV, LassoCV, LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingRandomSearchCV
from sklearn.ensemble import StackingRegressor, GradientBoostingRegressor

from sklearn.metrics import r2_score

import numpy as np

loop = asyncio.get_event_loop()
data = np.array(loop.run_until_complete(fake_get_prices())[0]["cost"])
X = np.array([data[i:i+20] for i in range(data.size-40)])
Y = np.array([data[i] for i in range(20, data.size-20)])
X_test = np.array([data[i: i+20] for i in range(data.size - 40, data.size-20)])
#print(X_test)
Y_test = np.array([data[i] for i in range(data.size-20,data.size)])
#print(Y_test)

model = StackingRegressor(estimators=[('ridge', RidgeCV()),
                                      ('lasso', LassoCV(random_state=10)),
                                      ('lr', LinearRegression()),
#                               ('knr', KNeighborsRegressor(n_neighbors=10))
                                      ],
                          final_estimator=GradientBoostingRegressor(n_estimators=25, subsample=0.5))

model.fit(X, Y)
print(model.predict(X_test))

print(score := r2_score(Y_test, model.predict(X_test)))
