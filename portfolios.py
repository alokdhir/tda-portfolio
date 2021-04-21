#!/usr/bin/env python3

from pprint import pprint
from tda import auth, client
from rich.console import Console
from rich.table import Table
from datetime import datetime
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

#r = c.get_accounts()
r = c.get_accounts(fields=c.Account.Fields.POSITIONS)

assert r.status_code == 200, r.raise_for_status()

console = Console()
table = Table(show_header=True, header_style="yellow")
table.add_column("Account#")
table.add_column("", justify="right")
table.add_column("")
table.add_column("", justify="right")
table.add_column("Value", justify="right", width=10)
table.add_column("Change", justify="right", width=10)
table.add_column("% Change", justify="right")
table.add_column("", justify="right")
table.add_column('Avail Cash', justify="right")

total = 0

for idx, i in enumerate(r.json()):

    acct = i['securitiesAccount']
    cbal = acct['currentBalances']
    ibal = acct['initialBalances']
    diff = cbal['liquidationValue'] - ibal['liquidationValue']
    pct = (cbal['liquidationValue'] / ibal['liquidationValue']) - 1

    positions = acct['positions']

    if diff > 0:
        ccolor = "green"
    else:
        ccolor = "red"
    diffS = "[" + ccolor + "]" + "{:.2f}".format(diff) + "[/" + ccolor + "]"
    pctS = "[" + ccolor + "]" + "{:.2%}".format(pct) + "[/" + ccolor + "]"

    bpow = 0
    if "buyingPower" in cbal.keys():
        bpow = cbal['buyingPower']
    else:
        bpow = cbal['cashAvailableForTrading']
    
    # endrow = False
    # if idx >= (len(r.json()) - 1):
    #     endrow= True

    total += cbal['liquidationValue']

    table.add_row(acct['accountId'],
        "", "", 
        "{:,.2f}".format(cbal['liquidationValue']),
            diffS,
                pctS,
                  "",
                    '[bold green]' + "{:.2f}".format(bpow) + '[/bold green]', end_section=True)
            #sym exp daych, pnl, quan price cost mval

    table.add_row("symbol", "u/l", "exp", "day change (%)", "p/l", "quantity", "price", "cost", "market val", end_section=True, style="yellow")

    daytotal = 0
    pltotal = 0

    #for pidx, p in enumerate(positions):
    for pidx, p in enumerate(sorted(positions, key = lambda x: x['currentDayProfitLossPercentage'], reverse=True)):

        symcolor = "bold blue"
        inst = p['instrument']

        tp = inst['assetType']
        if (tp == "CASH_EQUIVALENT"):
            continue

        sym = inst['symbol']
        q = p['longQuantity']
        price = p['averagePrice']
        val = p['marketValue']
        daypl = p['currentDayProfitLoss']
        dayplpct = p['currentDayProfitLossPercentage']
        cost = q * price

        if (tp == "OPTION"):
            cost = 100 * cost
            symparts = sym.split('_')
            dt = symparts[1][0:6]
            strike = symparts[1][6:]
            symbol = symparts[0]

            #fix/format the date portion
            dobj = datetime.strptime(dt, '%m%d%y')
            fdt = dobj.strftime('%Y %b %d')

            symcolor = "bold cyan"

            #underlying
            r = c.get_quote(symbol)
            assert r.status_code == 200, r.raise_for_status()
            d = r.json()
            symkey = next(iter(d))
            underd = d[symkey]

            sym = symbol + ' ' + strike[1:] + strike[0]
            sp = float(strike[1:])
            if sp < underd['mark']:
                ulcolor = "green"
            else:
                ulcolor = "red"
            ulS = "[" + ulcolor + "]" + "{:.2f}".format(underd['mark']) + "[/" + ulcolor + "]"

        else:
            ulS = ""
            fdt = ""

        pnl = val - cost

        daytotal += daypl
        pltotal += pnl

        if daypl > 0:
           dcolor = "green"
        else:
           dcolor = "red"

        if pnl > 0:
           pcolor = "green"
        else:
           pcolor = "red"

        if daytotal > 0:
           dtcolor = "bold green"
        else:
           dtcolor = "bold red"

        if pltotal > 0:
           plcolor = "bold green"
        else:
           plcolor = "bold red"

        pnlS = "[" + pcolor + "]" + "{:,.2f}".format(pnl) + "[/" + pcolor + "]"
        dayplS = "[" + dcolor + "]" + "{:,.2f}".format(daypl) + " (" + "{:.0%}".format(dayplpct/100) + ")"+ "[/" + dcolor + "]"
        
        #end section if we are on last symbol
        pendrow = False
        if pidx >= (len(positions) - 1):
            pendrow= True

        table.add_row('[' + symcolor+ ']' + sym + '[/' + symcolor+ ']', ulS, fdt, dayplS, pnlS, "{:,.2f}".format(q), "{:,.2f}".format(price), "{:,.2f}".format(cost), "{:,.2f}".format(val), end_section=pendrow)

        #update totals
        daytotalS = '[' + dtcolor+ ']' + "{:,.2f}".format(daytotal) + '[/' + dtcolor+ ']'
        pltotalS = '[' + plcolor+ ']' + "{:,.2f}".format(pltotal) + '[/' + plcolor+ ']'

table.add_row("     TOTAL", "", "", daytotalS, pltotalS, "", "", "", "[bold]" + "{:,.2f}".format(total) + "[/bold]")

console.print(table)

