#!/usr/bin/env python3

import asyncio
import json
import tda
import configparser

from selenium import webdriver

config = configparser.ConfigParser()
config.read('config.ini')

token_path = config.get('secrets', 'token_path')
api_key = config.get('secrets', 'api_key')

redirect_uri = 'https://localhost'
primary_account_id = 123

c = tda.auth.easy_client(api_key, redirect_uri, token_path,
        webdriver_func=lambda: webdriver.Chrome())

client = tda.streaming.StreamClient(c, account_id=primary_account_id)

async def read_stream():
    await client.login()
    await client.quality_of_service(client.QOSLevel.EXPRESS)

    await client.nasdaq_book_subs(['GOOG'])
    client.add_nasdaq_book_handler(
            lambda msg: print(json.dumps(msg, indent=4)))

    while True:
        await client.handle_message()

asyncio.get_event_loop().run_until_complete(read_stream())
