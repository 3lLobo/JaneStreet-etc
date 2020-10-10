#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import math
import statistics
import numpy as np

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
test_exchange_index=0
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

def get_market_price(msg):
    prices = {}
    for stock in stocks.keys():
        sell_price = msg['stock']['sell'][0][0]
        buy_price = msg['stock']['buy'][-1][0]
        sell_vol = np.add(msg['stock']['sell'][:][1])
        buy_vol = np.add(msg['stock']['buy'][:][1])
        prices[stock] = {'sell': sell_price, 'buy': buy_price, 'sell_vol': sell_vol, 'buy_vol': buy_vol}
    return prices

def mean_over_orders(positions, default):
    # List[Tuple2[int price, int quantity]
    return statistics.mean([price for (price, qty) in positions]) if len(positions) else default

# TODO
def mean_over_things(positions):
    # List[Tuple2[int price, int quantity]
    pass

def closest_buy(positions):
    # List[Tuple2[int price, int quantity]
    return positions[0][0] if len(positions) else 0

def closest_sell(positions):
    # List[Tuple2[int price, int quantity]
    return positions[0][0] if len(positions) else math.inf


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
    n = 0
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

            # popularity metrics:
            # how many people
            # how many things
            # closest price
            closest_prices = { k: { 'buy': closest_buy(dic['buy']), 'sell': closest_sell(dic['sell']) } for k, dic in state.items() }
            print('closest_prices:')
            print(closest_prices)
            # mean price weighted over orders
            # mean price weighted over things

            # metrics:
            # gap size
            # velocity of buy/sell
            # expected_trading_prices
            expected_trading_prices = { k: statistics.mean([dic['buy'], dic['sell']]) for k, dic in closest_prices.items() }
            print('expected_trading_prices:')
            print(expected_trading_prices)

            mean_prices = { k: { 'buy': mean_over_orders(dic['buy'], 0), 'sell': mean_over_orders(dic['sell'], math.inf) } for k, dic in state.items() }
            print('mean_prices:')
            print(mean_prices)

            # trade fast
            # trade slow

            # bonds
            if(msg['symbol'] == 'BOND'):
                bond = state['BOND']
                buy = bond['buy']
                sell = bond['sell']
                bond_value = 1000
                if len(buy):
                    (buy_price, buy_qty) = buy[0]
                    if (buy_price > bond_value):
                        n += 1
                        write_to_exchange(exchange, {"type": "add", "symbol": 'BOND', "dir": "SELL", "price": buy_price, "size": buy_qty, "order_id": n})
                if len(sell):
                    (sell_price, sell_qty) = sell[0]
                    if (sell_price < bond_value):
                        n += 1
                        write_to_exchange(exchange, {"type": "add", "symbol": 'BOND', "dir": "BUY", "price": sell_price, "size": sell_qty, "order_id": n})

        if(msg["type"] == "trade"):
            print(msg)
        if(msg["type"] == "open"):
            print(msg)
        if(msg["type"] == "close"):
            print("The round has ended")

# def best_buy()

if __name__ == "__main__":
    main()
