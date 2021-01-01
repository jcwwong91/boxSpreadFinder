import datetime
import logging
from options import get_cost


def process(data, show_all=False):
    for date, v in data.items():
        process_date(date, v, show_all=show_all)

def process_date(date, data, show_all=False):
    calls = data.get('calls')
    puts = data.get('puts')
    if not calls or not puts:
        print('Failed to get call/put data')
        return
    otm_calls = calls.get('otm')
    itm_calls = calls.get('itm')
    otm_puts = puts.get('otm')
    itm_puts = puts.get('itm')
    strike_prices = set(list(itm_calls.keys()) + list(otm_calls.keys()) + list(itm_puts.keys()) + list(otm_puts.keys()))
    for lower in strike_prices:
        for upper in strike_prices:
            check_bounds(date, lower, upper, itm_calls, otm_calls, itm_puts, otm_puts, show_all=show_all)

def check_bounds(date: int, lower: int, upper: int, itm_calls, otm_calls, itm_puts, otm_puts, show_all=False):
    if upper <= lower:
        return
    itm_call = itm_calls.get(lower)
    otm_call = otm_calls.get(upper)
    otm_put = otm_puts.get(lower)
    itm_put = itm_puts.get(upper)
    if itm_call is None or otm_call is None or otm_put is None or itm_put is None:
        logging.debug(f'Missing option for {lower} -> {upper}: itm_call: {itm_call} otm_call: {otm_call} otm_put: {otm_put} itm_put: {itm_put}')
        return
    cost = (get_cost(itm_call) + get_cost(itm_put)) * 100
    revenue = (get_cost(otm_call) + get_cost(otm_put)) * 100
    trade_costs = cost - revenue
    spread = (upper - lower) * 100
    profit = spread - trade_costs
    if profit > 0 or show_all:
        date2 = datetime.datetime.fromtimestamp(date)
        print(f'expiration: {date2} {lower} -> {upper}: Profit = {spread - trade_costs}')


def test():
    lower = 49
    upper = 53
    itm_calls = {49: {'bid': 3.29, 'ask': 3.29}}
    otm_calls = {53: {'bid': 1.23, 'ask': 1.23}}
    itm_puts = {53: {'bid': 2.69, 'ask': 2.69}}
    otm_puts = {49: {'bid': 0.97, 'ask': 0.97}}
    check_bounds(date, lower, upper, itm_calls, otm_calls, itm_puts, otm_puts)
