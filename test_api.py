from app.core import data

# Test the API endpoint that the frontend calls
print('Testing API endpoint simulation...')
print('Fetching crypto assets with prices...')

# Test a few crypto symbols
crypto_symbols = ['BTC-USD', 'ETH-USD', 'SOL-USD']
quotes = data.get_quotes(crypto_symbols)

for symbol, quote in quotes.items():
    if quote:
        print(f'{symbol}: ${quote.get("price", 0):.2f} ({quote.get("change_pct", 0):.2f}%)')
    else:
        print(f'{symbol}: No quote')
