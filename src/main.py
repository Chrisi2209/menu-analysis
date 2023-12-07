from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import requests
import datetime as dt
import pandas as pd

from logger import logger
from pdf import get_days, save_new_pdf, read_date
from day import Day
from analyze import get_storage, write_storage, add_day


def get_files_in_directory(directory: str) -> List[str]:
    file_list = []

    # Iterate over all files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)

    return file_list


def add_to_storage_routine(pdf_path: str):
    print(f"Importing data from {pdf_path}.")
    days: List[Day] = get_days(pdf_path)

    logger.info(f"retrieving storage...")
    df: pd.DataFrame = get_storage()

    logger.info(f"Adding new data")
    for day in days:
        df = add_day(df, day)

    logger.info(f"Writing new dataframe to storage")
    print("writing to storage")
    write_storage(df)


def add_to_df(df: pd.DataFrame, pdf_path: str) -> pd.DataFrame:
    print(f"Importing data from {pdf_path}.")
    days: List[Day] = get_days(pdf_path)

    logger.info(f"Adding new data")
    for day in days:
        df = add_day(df, day)

    return df


def main():
    logger.info(f"new call: {' '.join(sys.argv)}")

    # check for cmd arguments
    if len(sys.argv) == 2:
        if sys.argv[1] in ("-h", "--help"):
            print("""Read the README for more information.
Execute this script to get the current menu plan of the htl mödling and
store it in the stored-menus directory. It then analyses the soup, lunch, dessert
and dinner based on the menus collected so far. Supply a path to an existing menu
as a command line argument to import the data from it into the analysis.""")

        elif os.path.exists(sys.argv[1]):
            if os.path.isfile(sys.argv[1]):
                # just a file
                logger.debug(f"importing menu from {sys.argv[1]}")
                path: str = sys.argv[1]

                if not path.endswith(".pdf"):
                    logger.debug(f"given file is no pdf")
                    print("The given path does not have the pdf file extension!")
                    print("Aborting.")
                    return

                add_to_storage_routine(path)

            else:
                # a whole directory was given
                files_in_dir: List[str] = get_files_in_directory(sys.argv[1])

                print(f"IMPORTING ALL MENUS FROM {sys.argv[1]}")
                logger.info(f"IMPORTING ALL MENUS FROM {sys.argv[1]}")

                df: pd.DataFrame = get_storage()

                for file in files_in_dir:
                    logger.debug(f"importing menu from {file}")

                    # check if it is a pdf file
                    if not file.endswith(".pdf"):
                        continue

                    df = add_to_df(df, file)

                if df is not None:
                    logger.info(f"Writing new dataframe to storage")
                    print("writing to storage")
                    write_storage(df)

        else:
            logger.info("Wrong arguments")
            print("Argument did not match any. Use -h or --help for help.")

        return

    elif len(sys.argv > 2):
        logger.info("wrong number of arguments.")
        print("only 1 argument is allowed!")

    logger.info("downloading pdf from web")
    url: str = "https://www.campusm.at/download/339/"
    response = requests.get(url, stream=True)

    if response.status_code != 200:
        logger.warning(f"download failed! url={url}")
        print(f"Request to {url} failed! Aborting.")
        return 1

    logger.debug("Request successful")
    print("Request successful")

    logger.debug("Saving the pdf")
    # save the pdf
    path: str = save_new_pdf(response)

    df: pd.DataFrame = add_to_storage_routine(path)


if __name__ == "__main__":
    main()
