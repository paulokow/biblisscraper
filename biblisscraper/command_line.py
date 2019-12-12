from datetime import datetime, timedelta
from biblisscraper.scraper import scrap_biblis_book_lents


def main():
    accounts = [
        {
            "name": "Karolka",
            "user": "9027118",
            "password": "270378"
        },
        {
            "name": "Pawel",
            "user": "09027107",
            "password": "200579"
        },
        {
            "name": "Dominika",
            "user": "09029493",
            "password": "03102003"
        },
        {
            "name": "Kacper",
            "user": "09029563",
            "password": "150308"
        },
    ]

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
