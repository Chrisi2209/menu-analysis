from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import datetime as dt
import pandas as pd
import shutil

from logger import logger
from day import Day

"""
This package includes whole analyzation part of
the program.
"""

ANALYSIS_FILE_PATH: str = os.path.realpath(os.path.join(
    os.path.dirname(__file__), "..", "analysis", "storage.xlsx"))
# has to be inside the analyze path (write storage does only check backup path existing)
BACKUP_PATH: str = os.path.realpath(os.path.join(
    os.path.dirname(ANALYSIS_FILE_PATH),
    "backups"
))


def get_storage() -> pd.DataFrame:
    """
    Returns a dataframe from the excel sheet in analysis/storage.xlsx.
    Columns: [date, soup, main, desert, dinner, comment]
    main course is ; seperated
    """

    dtypes: Dict = {"soup": str,
                    "main": str,  # ; seperated
                    "dessert": str,
                    "dinner": str,
                    "comment": str,
                    }

    if os.path.exists(ANALYSIS_FILE_PATH):
        logger.debug("reading from excel")
        df: pd.DataFrame = pd.read_excel(ANALYSIS_FILE_PATH, index_col='date')

        df = df.astype(dtypes)

        return df

    else:
        logger.debug("storage file not existing, creating default")
        print("storage file not existing yet")
        print("creating default DataFrame.")
        df: pd.DataFrame = pd.DataFrame(
            {
                "soup": [],
                "main": [],
                "dessert": [],
                "dinner": [],
                "comment": [],
            },
            index=pd.to_datetime([])
        )

        df = df.astype(dtypes)

        return df


def write_storage(df: pd.DataFrame) -> None:
    """
    Writes the given dataframe into analysis/analysis.xlsx.
    It will also create a backup file named with its creation 
    time to prevent data loss.
    """
    # BACKUP_PATH exists, BACKUP_PATH is a path to a dir
    if not os.path.exists(BACKUP_PATH):
        logger.debug("backup path not existing, creating dirs to backup path")
        os.makedirs(BACKUP_PATH)

    # override old excel file
    with pd.ExcelWriter(ANALYSIS_FILE_PATH, engine='xlsxwriter') as writer:
        logger.debug("writing to storage file...")
        df.to_excel(writer, index=True, index_label="date")

    logger.debug("creating backup")
    # create backup of new excel file
    shutil.copy(
        ANALYSIS_FILE_PATH,
        os.path.realpath(os.path.join(
            BACKUP_PATH,
            dt.datetime.today().strftime('%Y-%m-%d_%H-%M-%S.xlsx')
        ))
    )


def add_day(df: pd.DataFrame, day: Day) -> pd.DataFrame:
    """
    Adds the day as a new row to the dataframe
    """
    logger.debug(f"adding day: {day}")
    # Check if the index already exists
    if day.date not in df.index:

        print(f"Adding new day: {day.date.strftime('%d-%m-%Y')}")
        # Create a new DataFrame with the new row
        new_row = pd.DataFrame(day.description, index=[day.date])

        # Concatenate the original DataFrame with the new DataFrame
        df = pd.concat([df, new_row])

        # Sort the DataFrame by the index (if necessary)
        df = df.sort_index()
    else:
        logger.debug(
            f"date already exists, overriding old entry: {dict(df.loc[day.date])}")
        print(
            f"trying to add duplicate date: {day.date.strftime('%d-%m-%Y')}, overriding")
        # Index already exists, update the existing row
        df.loc[day.date] = day.description

    return df
