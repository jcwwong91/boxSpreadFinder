import datetime
import logging
from filters import pre_filters, post_filters
from options import get_cost


def process(data, show_all=False):
    opportunities = list()
    for date, v in data.items():
        new_opportunities = process_date(date, v, show_all=show_all)
        opportunities.extend(new_opportunities)

    display_opportunities(opportunities)


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
    opportunities = list()
    for lower in strike_prices:
        for upper in strike_prices:
            stats = check_bounds(lower, upper, itm_calls, otm_calls, itm_puts, otm_puts)
            if not stats:
                continue

            stats['expiration'] = date
            if show_all:
                opportunitites.append(stats)
                continue
            for filter_func in post_filters:
                filter_out = filter_func(stats)
                if filter_out:
                    break
            if not filter_out:
                opportunities.append(stats)
    return opportunities

def check_bounds(lower: int, upper: int, itm_calls, otm_calls, itm_puts, otm_puts):
    if upper <= lower:
        return
    itm_call = itm_calls.get(lower)
    otm_call = otm_calls.get(upper)
    otm_put = otm_puts.get(lower)
    itm_put = itm_puts.get(upper)
    if itm_call is None or otm_call is None or otm_put is None or itm_put is None:
        logging.debug(f'Missing option for {lower} -> {upper}: itm_call: {itm_call} otm_call: {otm_call} otm_put: {otm_put} itm_put: {itm_put}')
        return None
    bought = (get_cost(itm_call) + get_cost(itm_put)) * 100
    sold = (get_cost(otm_call) + get_cost(otm_put)) * 100
    spread = (upper - lower) * 100
    trade_costs = bought - sold
    return {
            'bought': bought,
            'sold': sold,
            'trade_costs': trade_costs,
            'spread': spread,
            'profit': spread - trade_costs,
            'lower': lower,
            'upper': upper,
            'margin_of_safety': lower * 100 + upper * 100
            }


def display_opportunities(opportunities):
    for op in opportunities:
        date = op['expiration']
        lower = op['lower']
        upper = op['upper']
        profit = op['profit']
        mos = lower * 100 + upper * 100
        print(f'Expiration: {date}: {lower} -> {upper} - Profit: {profit} ({profit / mos}) -- Margin of Safety: {mos}')


def test():
    lower = 49
    upper = 53
    itm_calls = {49: {'bid': 3.29, 'ask': 3.29}}
    otm_calls = {53: {'bid': 1.23, 'ask': 1.23}}
    itm_puts = {53: {'bid': 2.69, 'ask': 2.69}}
    otm_puts = {49: {'bid': 0.97, 'ask': 0.97}}
    check_bounds(date, lower, upper, itm_calls, otm_calls, itm_puts, otm_puts)

