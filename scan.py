from typing import NoReturn
import requests
from bs4 import BeautifulSoup
from config import CRYPTO_LIST, COIN_LINK, COIN_NAME, NICEHASH_FEE
from prettytable import PrettyTable
from threading import Timer
import json 
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed




class Main():

    def __init__(self, max_worker = 3):
        self.max_worker = max_worker
        self.conversions = {}

    def normalize_price(self, price: str):
        price = price[1:].replace(',', '')
        return float(price)

    def normalize_to_bitcoin(self, to_bitcoin: str):
        price = to_bitcoin.split()[0].replace(',', '')
        return float(price)
    
    def download_conversions(self):
        try:
            conversions_response = requests.get("https://api2.nicehash.com/exchange/api/v2/info/prices")
        except Exception as e:
            print("Error getting NiceHash Server Response: ", e)
            return False

        self.conversions = {}
        if conversions_response.status_code == 200:
            self.conversions = json.loads(conversions_response.text)

        return True
        
    def downloader(self, crypto, link):
        try:
            page = requests.get(link)
        except Exception as e:
            print(f"Error gettig {crypto} Link:", e)
            return crypto, None, None
        
        if page.status_code != 200:
            print(f"Couldn't parse {link}")
            return crypto, None, None 

        #print(f"{crypto} Downloaded")
        soup = BeautifulSoup(page.content, 'html.parser')
        summary_container = soup.find("div", class_='priceSection')
        try:
            price = self.normalize_price( summary_container.select('.priceTitle .priceValue span')[0].get_text() )
        except Exception as e:
            print("Price couldn't be parsed in downloaded page:", e)
            price = None 
        
        try:
            target_key = (COIN_NAME[crypto] + COIN_NAME['Bitcoin']).upper()
            to_bitcoin = 1
            if crypto != 'Bitcoin':
                to_bitcoin = self.conversions[target_key]
            bitcoin_to_crypto = (1.0/to_bitcoin)*(1-NICEHASH_FEE)
        except Exception as e:
            print(f"{crypto} conversion not found in NiceHash: {e}")
            bitcoin_to_crypto = None
        return crypto, price, bitcoin_to_crypto

    def download_multithread(self):
        results = {}
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_worker) as executor:
            for crypto, url in COIN_LINK.items():
                futures.append(executor.submit(self.downloader, crypto, url))

        for task in as_completed(futures):
            result = task.result()
            results[ result[0] ] = ( result[1], result[2] )
        
        return results

    def download_singlethread(self):
        results = {}
        for crypto, url in COIN_LINK.items():
            result = self.downloader( crypto, url )
            results[ result[0] ] = ( result[1], result[2] )
        return results

    def make_table(self, method):
        table = PrettyTable()
        table.add_column("Info", ["$Price", "From BTC (NiceHash)"])
        results = {}
        if method == 'multithread':
            results = self.download_multithread()
        else:
            results = self.download_singlethread()

        for crypto in CRYPTO_LIST:
            info = results[crypto]
            price, from_bitcoin = info[0], info[1]
            price_pretty = ""

            if price is not None:
                price_pretty = f"{price:.2f}"
            else:
                price = "-1.00"

            from_bitcoin_pretty = ""
            if from_bitcoin is not None:
                from_bitcoin_pretty = f"{from_bitcoin:.2f}"
            else:
                from_bitcoin = (results['Bitcoin'][0] / price)*(1-NICEHASH_FEE)
                from_bitcoin_pretty = f"{from_bitcoin:.2f}*"
            
            table.add_column(f"{crypto}", [price_pretty, from_bitcoin_pretty])
            table.align[crypto] = "r"
        
        return table



def print_table(worker):
    #Timer(30, print_table).start()
    while True:
        if worker.download_conversions():
            now = datetime.now()
            current_time = now.strftime("%d %b, %Y: %I:%M:%S %p")
            print("Current Time =", current_time)
            table = worker.make_table(method='multithread')
            print(table)
    
        time.sleep(30)


if __name__ == '__main__':
    worker = Main(max_worker=2)
    print_table(worker)
    