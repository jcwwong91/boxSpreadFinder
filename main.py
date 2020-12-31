import datetime
from options import load, parse_options_data
from process import process


def test_flow():
    c = load('data.html')
    calls, puts = parse_options_data(c)
    date = datetime.datetime(2020, 12, 30, 12, 0, 0)
    data = {int(date.timestamp()) / 1000: {'calls': calls, 'puts': puts}}
    process(data)

test_flow()
