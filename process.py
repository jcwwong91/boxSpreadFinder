

def process(data):
    for date, v in data.items():
        process_date(v)

def process_date(data):
    calls = data.get('calls')
    puts = data.get('puts')
    print(calls)
