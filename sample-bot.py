#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="endotech"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=1
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(exchange_hostname + ':' + str(port))
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    msg = json.loads(exchange.readline())
    # print(msg)
    return msg

stocks = {'BOND': 100,'VALBZ': 10, 'VALE': 10,'GS': 100, 'MS': 100, 'WFC': 100, 'XLF': 100}

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    print(stocks['BOND'])
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    symbols = hello_from_exchange['symbols']
    print('symbols:')
    print(symbols)
    positions = {s['symbol']: s['position'] for s in symbols}
    print('positions:')
    print(positions)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write msgs generate marketdata, this will cause an
    # exponential explosion in pending msgs. Please, don't do that!
    # print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    state = {}
    while True:
        msg = read_from_exchange(exchange)
        if(msg["type"] == "hello"):
            print(msg)
        if(msg["type"] == "ack"):
            print(msg)
        if(msg["type"] == "reject"):
            print(msg)
        if(msg["type"] == "error"):
            print(msg)
        if(msg["type"] == "out"):
            print(msg)
        if(msg["type"] == "fill"):
            print(msg)
        if(msg["type"] == "book"):
            state[msg['symbol']] = { 'sell': msg['sell'], 'buy': msg['buy'] }
            print('state:')
            print(state)
        if(msg["type"] == "trade"):
            print(msg)
        if(msg["type"] == "open"):
            print(msg)
        if(msg["type"] == "close"):
            print("The round has ended")

if __name__ == "__main__":
    main()
