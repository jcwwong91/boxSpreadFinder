import datetime
import re
import requests
import typing

from bs4 import BeautifulSoup

import pprint


def get_options_data(ticker: str):
    content = fetch_options_data(ticker)
    dates = get_option_dates(content)
    now = datetime.datetime.now()
    data = dict()
    for date in dates:
        dt = datetime.datetime.fromtimestamp(date)
        if dt > now + datetime.timedelta(days=14):
            continue
        if len(data) != 0:
            content = fetch_options_data(ticker, date)
        calls, puts = parse_options_data(content)
        if calls is None or puts is None:
            dump(date, content)
            continue
        data[date] = {'calls': calls, 'puts': puts}
    return data


def fetch_options_data(ticker: str, date: int=None):
    ticker = ticker.upper()
    url = f'https://finance.yahoo.com/quote/{ticker}/options?p={ticker}'
    if date is not None:
        url += f'&date={date}'
    resp = requests.get(url)
    if resp.status_code != 200:
        print('Failed to fetch options data')
        return None
    return resp.content


def parse_options_data(content: bytes):
    soup = BeautifulSoup(content, 'html.parser')
    call_table = soup.find_all('table', re.compile('calls.*list-options$'))
    if len(call_table) != 1:
        print(f'Unable to find the call table: {len(call_table)}')
        return None, None
    put_table = soup.find_all('table', re.compile('puts.*list-options$'))
    if len(put_table) != 1:
        print(f'Unable to find the put table: {len(put_table)}')
        return None, None
    calls = parse_table(call_table[0])
    puts = parse_table(put_table[0])
    return calls, puts


def get_option_dates(content: bytes):
    soup = BeautifulSoup(content, 'html.parser')
    select = soup.find_all('select', re.compile('Fz\(s\).*'))
    if len(select) != 1:
        print(f'Incorrect number of elements found for getting option dates: {len(select)}')
        return None
    options = select[0].find_all('option')
    dates = list()
    for sd in options:
        try:
            dates.append(int(sd['value']))
        except:
            print('Could not find value of date')
            continue
    return dates


def parse_table(table):
    rows = table.find_all('tr', re.compile('data-row[0-9]+'))
    options = {'itm': {}, 'otm': {}}
    for row in rows:
        option = {
                'strike': get_value(row, 'data-col2'),
                'last_price': get_value(row, 'data-col3'),
                'bid': get_value(row, 'data-col4'),
                'ask': get_value(row, 'data-col5'),
                'volume': get_value(row, 'data-col8'),
                'open_interest': get_value(row, 'data-col9')
                }
        for k, v in option.items():
            if v is None:
                print(f'Skipping due to invalid {k}')
                continue
        state = in_the_money(row)
        if state is None:
            continue
        key = 'itm' if state else 'otm'
        options[key][option['strike']] = option
    return options


def get_value(row, key: str):
    try:
        entries = row.find_all('td', re.compile(f'{key}'))
        if len(entries) != 1:
            print(f'Incorrect number of elements returned: {len(entries)}')
            return None
        if str(entries[0].text) == '-':
            return 0
        return float(entries[0].text.replace(',', ''))
    except Exception as e:
        print(f'Unable to extract value for {key}: {e}')
        return None


def in_the_money(row):
    """Returns true if in the money for processing"""
    try:
        return 'in-the-money' in row['class']
    except Exception as e:
        print(f'Failed to get the itm/otm value')
        return None


def get_cost(option):
    """Estimates the cost to purchase a contract"""
    return (option['ask'] + option['bid']) / 2


def dump(date, content):
    with open(f'{date}.html', 'w') as f:
        f.write(str(content))
        f.close()

def load(filename: str):
    with open(filename, 'r') as f:
        content = f.read()
        f.close()
    return content
