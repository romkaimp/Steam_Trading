from celery import shared_task
from pybit.unified_trading import HTTP
from data.fake_data.fake_orm import update_currencies, import_all
from service.celery_settings import app
import json


@shared_task
def table_update():
    cl = HTTP()
    with open("coins.json", "r") as file:
        data = json.load(file)["coins"]
    for symbol in data:
        data = cl.get_tickers(category="spot", symbol=symbol)
        data = data.get('result', {}).get('list', [])["lastPrice"]
        update_currencies(symbol, data)

@app.task()
def table_import():
    cl = HTTP()
    with open("coins.json", "r") as file:
        data = json.load(file)["coins"]
    for symbol in data:
        data = cl.get_kline(category="spot", symbol=symbol, interval=1)
        data = data.get("result", {}).get("list", [])[::-1][-20:]
        import_all()

