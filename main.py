import click
import datetime
from options import load, parse_options_data, get_options_data
from process import process


def test_flow():
    c = load('data.html')
    calls, puts = parse_options_data(c)
    date = datetime.datetime(2020, 12, 30, 12, 0, 0)
    data = {int(date.timestamp()): {'calls': calls, 'puts': puts}}
    process(data)


@click.command()
@click.option('-t', '--ticker', default=None, help='The ticker to pull data for')
def run(ticker: str):
    data = get_options_data(ticker)
    process(data)


if __name__ == '__main__':
    run()
