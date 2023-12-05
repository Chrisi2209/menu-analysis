from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import requests
import datetime as dt
import pandas as pd

from pdf import get_days, save_pdf, get_soup, get_lunches, get_dessert, get_dinner


def setup_logging(name: str) -> logging.Logger:
    path_to_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "logs"))
    path_to_log = os.path.abspath(os.path.join(path_to_dir, f"{name}.log"))

    if not os.path.exists(path_to_dir):
        os.mkdir(path_to_dir)

    file_handler = logging.FileHandler(path_to_log)
    file_handler.setFormatter(logging.Formatter(
        "%(levelname)-7s %(processName)s %(threadName)s %(asctime)s %(funcName)s: %(message)s"))

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    return logger


def main():
    # check for cmd arguments
    if len(sys.argv) == 2:
        if sys.argv[1] in ("-h", "--help"):
            print("""Read the README for more information.
Execute this script to get the current menu plan of the htl mödling and
store it in the stored-menus directory. It then analyses the soup, lunch, dessert
and dinner based on the menus collected so far. Supply a path to an existing menu
as a command line argument to import the data from it into the analysis.""")

        elif os.path.exists(sys.argv[1]):
            path: str = sys.argv[1]

            if not path.endswith(".pdf"):
                print("The given path does not have the pdf file extension!")
                print("Aborting.")
                return

            print(f"Importing data from {path}.")
            days: List[List[str]] = get_days(path)

            print()
            for day in days:
                if len(day) > 3:
                    print("soup:   \t", get_soup(day), sep="")
                    print("lunches:\t", ", ".join(get_lunches(day)), sep="")
                    print("desert: \t", get_dessert(day), sep="")
                    print("dinner: \t", get_dinner(day), sep="")
                    print()

        else:
            print("Argument did not match any. Use -h or --help for help.")

        return

    url: str = "https://www.campusm.at/download/339/"
    response = requests.get(url, stream=True)

    if response.status_code != 200:
        print(f"Request to {url} failed! Aborting.")
        return 1

    print("Request successful")

    # save the pdf
    path = save_pdf(response)

    days = get_days(path)

    print()
    for day in days:
        if len(day) > 3:
            print("soup:   \t", get_soup(day), sep="")
            print("lunches:\t", ", ".join(get_lunches(day)), sep="")
            print("desert: \t", get_dessert(day), sep="")
            print("dinner: \t", get_dinner(day), sep="")
            print()


if __name__ == "__main__":
    main()
