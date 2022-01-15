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
if '-c' in symbols:
    print('bloop')

def set_color(val, base, hi_good = True):
    if hi_good:
        if (val >= base ):
            color = 'green'
        else:
            color = 'red'
    else:
        if (val == 0):
             color = 'red'
        elif (val <= base ):
            color = 'green'
        else:
            color = 'red'

    return "[" + color + "]"  + str(val) + "[" + color + "]" 

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
    price = "[" + 'cyan' + "]" + "{:.2f}".format(f['mark']) + "[" + 'cyan' + "]"
    ch = f['netChange']
    if ch > 0:
        ccolor = "green"
    else:
        ccolor = "red"
    change = "[" + ccolor + "]" + "{:.2f}".format(f['netChange']) + "[/" + ccolor + "]"
    pctchange = "[" + ccolor + "]" + "{:.2f}".format(f['regularMarketPercentChangeInDouble']) + "[/" + ccolor + "]"
    low = str(f['52WkLow'])
    high = f['52WkHigh']
    rng = set_color(round((f['lastPrice'] / high) * 100), 50)
    pe = set_color(round(f['peRatio']), 20, False)
    div = set_color(f['divYield'], 3)

    table.add_row(symbol, price, change, pctchange, low, str(high), str(rng), str(pe), div)

#print(json.dumps(r.json(), indent=4))
console.print(table)