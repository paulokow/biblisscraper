from datetime import datetime, timedelta
from biblisscraper.scraper import scrap_biblis_book_lents
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='Biblis account scanner')
    parser.add_argument("-c", "--config", action="store", type=argparse.FileType("r"), default=".settings", help="Config file (JSON)")

    args = parser.parse_args()

    with args.config as config:
        configobj = json.load(config)
        accounts = configobj["accounts"]

    allitems = [inneritem
                for outeritem
                in [scrap_biblis_book_lents(account["name"], account["user"], account["password"])
                        for account
                        in accounts]
                for inneritem in outeritem]
    shortitems = [x for x in allitems if x["date"] < datetime.now() + timedelta(days=10)]

    print(shortitems)

if __name__ == '__main__':
    main()
