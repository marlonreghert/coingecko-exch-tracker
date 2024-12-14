VS_CURRENCY_MAPPING = {
    "USDT": "usd",
    "USDC": "usd",
    "USD": "usd",
    "EUR": "eur",
    "GBP": "gbp",
    "JPY": "jpy",
    "AUD": "aud",
    "CAD": "cad",
    "CHF": "chf",
    "BTC": "btc",
    "ETH": "eth",
    "BNB": "bnb"
}

COINGECKO_SYMBOLS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "USDC": "usd-coin",
    "BNB": "binancecoin",
    "ADA": "cardano",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "SOL": "solana",
    "DOT": "polkadot",
    "MATIC": "polygon",
    "LTC": "litecoin",
    "SHIB": "shiba-inu",
    "AVAX": "avalanche-2",
    "TRX": "tron",
    "LINK": "chainlink",
    "ATOM": "cosmos",
    "XMR": "monero",
    "BUSD": "binance-usd"
}

def get_vs_currency(symbol):
    return VS_CURRENCY_MAPPING.get(symbol.upper(), f"Unsupported vs_currency: {symbol}")


def get_coingecko_id(symbol):
    return COINGECKO_SYMBOLS.get(symbol.upper(), f"Unknown symbol: {symbol}")