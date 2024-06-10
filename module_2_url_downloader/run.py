import argparse
import pandas as pd
import requests
import logging
import time
import os

start = time.time()

FILE_NAME = 'customs_data.csv'

def init_logging(level):
    levels = {'debug': logging.DEBUG, 'warning': logging.WARNING, 'error': logging.ERROR}
    logging.basicConfig(level=levels[level])

def check_url(url):
    with requests.head(url) as r:
        if r.status_code == 200:
            return True
        else:
            return False

def main():
    # Init output file
    current_dir = os.getcwd()

    parser = argparse.ArgumentParser(description='Donwload the data from api and save it to the local csv file')
    parser.add_argument('-u', '--url', type=str,
                    help='API web address and port')
    parser.add_argument('-w', '--wait', type=int,
                    help='Waiting time in seconds when getting throttling error message from api')
    parser.add_argument('-o', '--output', type=str, default=current_dir,
                    help='Output csv file path')
    parser.add_argument('-p', '--page', type=int, default=1,
                    help='Initial page number to download. Default is 1. If a page number is not 1 then Output csv file wont be overwriten')
    parser.add_argument('-l', '--level', type=str, default='error',
                    help='Logging level: debug, warning, error')

    # Parse args
    args = parser.parse_args()

    # Init logging
    init_logging(args.level)
    logger = logging.getLogger(__name__)

    # Init first page variable
    page_number = args.page

    # Init output file
    if page_number == 1 and os.path.exists(f"{args.output}\{FILE_NAME}"):
        os.remove(f"{args.output}\{FILE_NAME}")
        
    while True:
        if check_url(args.url):
            logger.debug(f"{args.url} is available")
            next_page_url = f"{args.url}?page={str(page_number)}"
            logger.debug(f"Downloading page number: {page_number}")

            try:
                df = pd.read_json(next_page_url, encoding='utf-8')
                items = pd.json_normalize(data = df['items'])

                if len(items) > 0:
                    items['page'] = df['page']

                    if page_number == 1:
                        header = True
                    else:
                        header = False
                    
                    items.to_csv(f"{args.output}\{FILE_NAME}", encoding='utf-8', index=False, mode='a', sep ='\t', header=header)
                    logger.debug(f"Page with number {page_number} downloaded and added to {args.output}\{FILE_NAME}")
                    page_number += 1
                else:
                    logger.debug(f"All pages donwloaded from {args.url}. Last page number: {page_number}")
                    end = time.time()
                    
                    logger.debug(f"Execution time: {end - start} seconds")
                    break
            except Exception as e:
                logger.error(f"Failed to load data for page number: {page_number}. Error: {str(e)}")
        else:
            logger.debug(f"Waiting for throttling timeout: {args.wait} sec")
            time.sleep(args.wait)

if __name__ == "__main__":
    main()