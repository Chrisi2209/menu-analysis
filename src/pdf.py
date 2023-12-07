from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import requests
import PyPDF2
import datetime as dt
import re
import shutil

from logger import logger
from day import Day


"""
Library for reading and writing pdf for Menus.
Call get_days to instantly receive a List[str]
for each day. Then call getter functions from day.py
of a particular day to receive the courses of a day.
"""


def get_monday_and_friday(date: Optional[dt.datetime] = None):
    """
    returns datetime objects for the monday and friday dates
    of the current week.
    """
    if date is None:
        today = dt.datetime.today()
    else:
        today = date
    current_weekday = today.weekday()  # Monday is 0 and Sunday is 6

    # Calculate the difference between today and Monday
    days_to_monday = current_weekday
    monday = today - dt.timedelta(days=days_to_monday)

    # Calculate the difference between today and Friday
    days_to_friday = 4 - current_weekday
    friday = today + dt.timedelta(days=days_to_friday)

    return monday, friday


def save_new_pdf(response: requests.Response) -> str:
    """
    This function saves the pdf responded from Lindic's server.
    The PDFs are stored in the stored-menus directory. If the file
    already exists, it is overriden. The name of the file is not
    taken from the response but generated based on the current date.
    """
    # get monday and friday dates for name of file
    monday, friday = get_monday_and_friday()
    # get path to file
    path_to_file: str = os.path.realpath(os.path.join(os.path.dirname(
        __file__), "..", "stored-menus", f"Speiseplan_{monday.strftime('%d_%m')}_{friday.strftime('%d_%m_%y')}.pdf"))
    dirpath: str = os.path.dirname(path_to_file)

    # create directory if it doesn't exist yet
    if not os.path.exists(dirpath):
        logger.debug("Analysis directory not existing, creating...")
        os.mkdir(dirpath)

    # if the file already exists, make a warning that is will be
    # overridden
    if os.path.exists(path_to_file):
        # file already exists!
        logger.warning("PDF attempting to save already exists!")
        overridden_path: str = os.path.realpath(
            os.path.join(dirpath, "/overridden"))

        # create overriden directory if not existing
        if not os.path.exists(overridden_path):
            logger.debug("creating overridden directory...")
            os.mkdir(overridden_path)

        # copy file that will be overridden there
        shutil.copy(path_to_file, os.path.realpath(os.path.join(
            overridden_path,
            dt.datetime.now().strftime("%Y%m%d-%H%M%s_") + os.path.basename(path_to_file))))

        print("File already exists! Overwriting...")

    logger.debug("writing file")
    # write the file
    with open(path_to_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)

    return path_to_file


def read_pdf(pdf_path: str) -> str:
    """
    Reads a PDF file and returns all the text in it.
    This function uses the PyPDF2 module to accomplish this.
    """
    logger.debug(f"reading {pdf_path}")
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        # menu only has one page
        text: str = pdf_reader.pages[0].extract_text((0, 90))

    return text


def read_date(pdf_path: str) -> Optional[dt.datetime]:
    """
    Reads the pdf and returns the date of monday of the week.
    """
    logger.debug(f"extracting date from {pdf_path}")
    logger.debug(f"reading text from file")
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        # menu only has one page
        text: str = pdf_reader.pages[0].extract_text((0, 90))

    logger.debug(f"getting date as string")
    # getting date as a string
    lines = text.splitlines()

    # find line where MENÜPLAN is
    menüplan: int = 0
    for line in lines:
        line = line.replace(" ", "")

        # new format
        if (matching := re.search(r"\d{2}.\d{2}.–\d{2}.\d{2}.\d{4}", line)) is not None:
            date_string = matching.group()
            date_string = date_string[7:]
            date: dt.datetime = dt.datetime.strptime(date_string, "%d.%m.%Y")
            # return monday of that day
            return get_monday_and_friday(date)[0]

        # old format
        elif (matching := re.search(r"\d{2}.\d{2}.–\d{2}.\d{2}.\d{2}", line)) is not None:
            logger.info("old date format")
            date_string = matching.group()
            date_string = date_string[7:]
            date: dt.datetime = dt.datetime.strptime(date_string, "%d.%m.%y")
            # return monday of that day
            return get_monday_and_friday(date)[0]

        if "MENÜPLAN" in line:
            break
        menüplan += 1

    # check if menüplan wasn't found
    if menüplan == len(lines):
        return None

    # line of date = menüplan + 1
    date_line: str = lines[menüplan + 1]

    # get where date starts
    space_counter: int = 0
    index: int = 0
    for i, char in enumerate(date_line):
        if char == " ":
            space_counter += 1
        if space_counter == 2:
            index = i
            break

    # get date string
    date_string = date_line[index + 1:-1].replace(" ", "")

    logger.debug(f"converting to datetime")
    # create datetime object (friday)
    date: dt.datetime = dt.datetime(year=int(date_string[-4:]),
                                    month=int(date_string[3:5]),
                                    day=int(date_string[:2]))

    logger.debug(f"converting to monday of week")
    # return monday of that day
    return get_monday_and_friday(date)[0]


def strip_pdf(text: List[str]) -> None:
    """
    Removes redundant information on the top and bottom of file, as
    well as stripping each line in the text.
    """
    while "MO" not in text[0]:
        text.pop(0)

    # move MO to start of line
    while text[0][:2] != "MO":
        text[0] = text[0][1:]

    info: bool = False
    while text[-1][0] == " " or text[-1] == "Die ALLERGENE sind im Speisesaal auf einem Aushang ersichtlich." \
            or (not info) or text[-1] == "Das campusM  Team wünscht  " or text[-1] == "FROHE WEIHNACHTEN!  ":
        if "INFO" in text[-1]:
            info = True
        text.pop(-1)

    for i in range(len(text)):
        text[i] = text[i].strip()


def split_weekdays(text: List[str]) -> List[List[str]]:
    """
    Takes in all the weekdays in a List of strings and splits each
    day into its own List.
    """
    days: List[List[str]] = []

    for i in range(len(text)):
        if text[i] != "":
            if text[i][:2] in ("MO", "DI", "MI", "DO", "FR"):
                days.append([])
                # dont include weekdays in days, also remove their whitespace
                days[-1].append(text[i][3:])

            else:
                days[-1].append(text[i])

    return days


def get_days(path: str) -> List[Day]:
    """
    Supply a path to a menu and you get
    the text of the days.
    """
    # read the text
    text: str = read_pdf(path)
    # make a list out of the string
    lines: List[str] = text.splitlines()
    # remove all the clutter
    strip_pdf(lines)
    # get the days
    week: List[List[str]] = split_weekdays(lines)

    return Day.get_weekdays(week, read_date(path))
