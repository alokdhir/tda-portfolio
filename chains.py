#!/usr/bin/env python3

from tda import auth, client
from rich.console import Console
from rich.table import Table
from pprint import pprint
import configparser
import json
import sys
import os

otypes = client.Client.Options.ContractType

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

arglen = len(sys.argv)
if arglen < 2:
    sys.exit('Need a symbol and an optional strike')

symbol = sys.argv[1].upper()

strikep = None
if arglen > 2:
    strikep = sys.argv[2]
    
console = Console()
table = Table(show_header=True, header_style="yellow")
table.add_column("Symbol")
table.add_column("Price", justify="right", width=10)
table.add_column("Change", justify="right", width=10)
table.add_column("% Change", justify="right")

if strikep is None:
    r = c.get_option_chain(symbol, include_quotes=True, strike_count=10, contract_type=otypes.ALL)
else:
    r = c.get_option_chain(symbol, strike=strikep, include_quotes=True, strike_count=1)

# hide ugly traceback
sys.tracebacklimit = 0
assert r.status_code == 200, r.raise_for_status()
assert r.json()['status'] == 'SUCCESS', 'Got status ' + r.json()['status'] + ' from call'

ul = r.json()['underlying']
data = r.json()['callExpDateMap']

optionitems = ['putCall', 'ask', 'bid', 'last', 'netChange', 'gamma', 'vega', 'theta', 'openInterest' ]

for datei, ddata in data.items():
    pprint(datei)
    for strikei, sdata in ddata.items():
        sdata = sdata[0]
        for i in optionitems:
            print(sdata[i])
            

sys.exit()

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
