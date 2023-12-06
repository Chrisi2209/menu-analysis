from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import datetime as dt
import pandas as pd
import shutil

from day import get_soup, get_main, get_dessert, get_dinner

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
        df: pd.DataFrame = pd.read_excel(ANALYSIS_FILE_PATH).set_index("date")
        # df = df.set_index("date")

        df = df.astype(dtypes)

        return df

    else:
        print("storage file not existing yet")
        print("creating default DataFrame.")
        df: pd.DataFrame = pd.DataFrame(
            {
                "date": [],
                "soup": [],
                "main": [],
                "dessert": [],
                "dinner": [],
                "comment": [],
            }
        ).set_index("date")

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
        os.makedirs(BACKUP_PATH)

    # override old excel file
    with pd.ExcelWriter(ANALYSIS_FILE_PATH, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    # create backup of new excel file
    shutil.copy(
        ANALYSIS_FILE_PATH,
        os.path.realpath(os.path.join(
            BACKUP_PATH,
            dt.datetime.today().strftime('%Y-%m-%d_%H-%M-%S.xlsx')
        ))
    )


def add_day(df: pd.DataFrame, day: List[str], date: dt.datetime):
    """
    Adds the day as a new row to the dataframe
    """
    row = {"date": date,
           "soup": get_soup(day),
           "main": get_main(day),
           "dessert": get_dessert(day),
           "dinner": get_dinner(day),
           "comment": "empty", }

    df = df.append(row)
