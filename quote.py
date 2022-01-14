#!/usr/bin/env python3

from tda import auth, client
from rich.console import Console
from rich.table import Table
from pprint import pprint
import configparser
import json
import sys
import os

config = configparser.ConfigParser()
confdir = os.path.dirname(os.path.realpath(__file__))

config.read(confdir + '/config.ini')

token_path = config.get('secrets', 'token_path')
api_key = config.get('secrets', 'api_key')
redirect_uri = config.get('secrets', 'redirect_uri')

try:
    c = auth.client_from_token_file(token_path, api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome() as driver:
        c = auth.client_from_login_flow(
            driver, api_key, redirect_uri, token_path)

symbols = sys.argv[1:]

if not symbols:
    symbols = ['AAPL', 'TSLA']

console = Console()
table = Table(show_header=True, header_style="yellow")
table.add_column("Symbol")
table.add_column("Price", justify="right", )
table.add_column("Change", justify="right")
table.add_column("% Change", justify="right")
table.add_column("Low", justify="right")
table.add_column("High", justify="right")
table.add_column("% Rng", justify="right")
table.add_column("P/E", justify="right")
table.add_column("% Div", justify="right")


r = c.get_quotes(symbols)
assert r.status_code == 200, r.raise_for_status()

for symbol, f in r.json().items():
    price = "{:.2f}".format(f['mark'])
    ch = f['netChange']
    if ch > 0:
        ccolor = "green"
    else:
        ccolor = "red"
    change = "[" + ccolor + "]" + "{:.2f}".format(f['netChange']) + "[/" + ccolor + "]"
    pctchange = "[" + ccolor + "]" + "{:.2f}".format(f['regularMarketPercentChangeInDouble']) + "[/" + ccolor + "]"
    low = str(f['52WkLow'])
    high = f['52WkHigh']
    rng = round((f['lastPrice'] / high) * 100)
    pe = round(f['peRatio'])
    div = "{:.2f}".format(f['divYield'])

    table.add_row(symbol, price, change, pctchange, low, str(high), str(rng), str(pe), div)

#print(json.dumps(r.json(), indent=4))
console.print(table)