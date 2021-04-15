#!/usr/bin/env python3

from tda import auth, client
from rich.console import Console
from rich.table import Table
import configparser
import json
import sys

config = configparser.ConfigParser()
config.read('config.ini')

token_path = config.get('secrets', 'token_path')
api_key = config.get('secrets', 'api_key')

redirect_uri = 'http://localhost'
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
table.add_column("Price", justify="right", width=10)
table.add_column("Change", justify="right", width=10)
table.add_column("% Change", justify="right")

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
    pctchange = "[" + ccolor + "]" + "{:.2%}".format(f['markPercentChangeInDouble']/100) + "[/" + ccolor + "]"
    table.add_row(symbol, price, change, pctchange)
 
console.print(table)

#print(json.dumps(r.json(), indent=4))
