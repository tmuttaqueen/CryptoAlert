
CRYPTO_LIST = [ 'Bitcoin', 'Ethereum', 'Cardano', 'Enjin Coin', 'Ripple', 'Polygon', 'Solana', 'Decentraland' ]

COIN_NAME = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Cardano': 'ADA',
    'Enjin Coin': 'ENJ', 
    'Ripple': 'XRP',
    'Polygon': 'MATIC',
    'Solana': 'SOL',
    'Decentraland': 'MANA',
}

COIN_LINK = {
    'Bitcoin': 'https://coinmarketcap.com/currencies/bitcoin/',
    'Ethereum': 'https://coinmarketcap.com/currencies/ethereum/',
    'Cardano': 'https://coinmarketcap.com/currencies/cardano/',
    'Enjin Coin': 'https://coinmarketcap.com/currencies/enjin-coin/', 
    'Ripple': 'https://coinmarketcap.com/currencies/xrp/',
    'Polygon': 'https://coinmarketcap.com/currencies/polygon/',
    'Solana': 'https://coinmarketcap.com/currencies/solana/',
    'Decentraland': 'https://coinmarketcap.com/currencies/decentraland/'
}

NICEHASH_FEE = 0.005

for crypto in CRYPTO_LIST:
    assert COIN_NAME.get(crypto) is not None, f'No coin name for crypto {crypto}'
    assert COIN_LINK.get(crypto) is not None, f'No coin link for crypto {crypto}'

