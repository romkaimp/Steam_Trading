import celery
from celery_settings import app
from data.parser.parser import main
from service.ml.ml import update_weights


@app.task
def table_update():
    main()


@app.task
def update_weights():
    update_weights()
