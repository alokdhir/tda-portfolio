#!/usr/bin/env python3

from tda import auth, client
from rich.console import Console
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

redirect_uri = 'http://localhost'
try:
    c = auth.client_from_token_file(token_path, api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome() as driver:
        c = auth.client_from_login_flow(
            driver, api_key, redirect_uri, token_path)

sym = sys.argv[1]

if not sym:
    print('Usage: ' + sys.argv[0] + ': symbol')
    exit(255)
    
r = c.get_quote(sym)
assert r.status_code == 200, r.raise_for_status()

d = r.json()

x = next(iter(d))

pprint(x)

