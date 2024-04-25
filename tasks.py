import celery
from celery_settings import app
from data.parser.parser import table_update
from service.ml.ml import update_weights


@app.task
def table_update():
    table_update()


@app.task
def update_weights():
    update_weights()
