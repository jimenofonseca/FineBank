import datetime
from currency_converter import CurrencyConverter
from flask import request
import json
import pandas as pd

c = CurrencyConverter('http://www.ecb.int/stats/eurofxref/eurofxref-hist.zip')


def get_database(type, data):
    datasets = json.loads(data)
    dff = pd.read_json(datasets[type], orient='split')
    return dff

def calculate_rate_exact_day_cop(to_currency):
    if to_currency == "SGD":
        return 0.00043
    if to_currency == "CHF":
        return 0.00031
    if to_currency == "USD":
        return 0.00031

def calculate_rate_exact_day_cop_inversed(from_currency):
    if from_currency == "SGD":
        return 1/0.00043
    if from_currency == "CHF":
        return 1/0.00031
    if from_currency == "USD":
        return 1/0.00031


def calculate_rate_exact_day(from_currency, month, year, to_currency):
    year = str(year)
    for day in range(1, 10):
        days = '0' + str(day)
        date = datetime.datetime.strptime(days + ' ' + month + ' ' + year, '%d %b %Y')
        try:
            rate = c.convert(1, from_currency, to_currency, date)
        except:
            continue
        if rate > 0.0:
            return rate

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()