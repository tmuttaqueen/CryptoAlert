from typing import NoReturn
import requests
from bs4 import BeautifulSoup
from config import CRYPTO_LIST, COIN_LINK, COIN_NAME, NICEHASH_FEE
from prettytable import PrettyTable
from threading import Timer
import json 
import time

def normalize_price(price: str):
    price = price[1:].replace(',', '')
    return float(price)

def normalize_to_bitcoin(to_bitcoin: str):
    price = to_bitcoin.split()[0].replace(',', '')
    return float(price)


def get_info( crypto, link, conversions ):
    try:
        page = requests.get(link)
    except Exception as e:
        print(crypto, e)
        return None, None
    if page.status_code != 200:
        print(f"Couldn't parse {link}")
        return None, None 

    #print(f"{crypto} Downloaded")
    soup = BeautifulSoup(page.content, 'html.parser')
    summary_container = soup.find("div", class_='priceSection')
    try:
        price = normalize_price( summary_container.select('.priceTitle .priceValue span')[0].get_text() )
    except Exception as e:
        print(e)
        price = None 
    
    try:
        target_key = (COIN_NAME[crypto] + COIN_NAME['Bitcoin']).upper()
        to_bitcoin = 1
        if crypto != 'Bitcoin':
            to_bitcoin = conversions.get(target_key)
        bitcoin_to_crypto = (1.0/to_bitcoin)*(1-NICEHASH_FEE)
    except Exception as e:
        print(crypto, e)
        bitcoin_to_crypto = None
    return price, bitcoin_to_crypto


def print_table():
    #Timer(30, print_table).start()
    while True:
        prices = {}
        table = PrettyTable()
        table.add_column("Info", ["$Price", "From BTC (NiceHash)"])
        try:
            conversions_response = requests.get("https://api2.nicehash.com/exchange/api/v2/info/prices")
            conversions = None 
            if conversions_response.status_code == 200:
                conversions = json.loads(conversions_response.text)
        except Exception as e:
            print(e)
            continue
        
        for crypto in CRYPTO_LIST:
            price, from_bitcoin = get_info( crypto, COIN_LINK[crypto], conversions )
            price_pretty = "-1"
            if price is not None:
                prices[crypto] = price
                price_pretty = f"{price:.2f}"
            from_bitcoin_pretty = "-1"
            if from_bitcoin is not None:
                from_bitcoin_pretty = f"{from_bitcoin:.2f}"
            else:
                from_bitcoin = (prices['Bitcoin'] / price)*(1-NICEHASH_FEE)
                from_bitcoin_pretty = f"{from_bitcoin:.2f}"
            table.add_column(f"{crypto}", [price_pretty, from_bitcoin_pretty])
            table.align[crypto] = "r"
        print(table)
        time.sleep(10)


if __name__ == '__main__':
    print_table()
    