from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import requests
import PyPDF2
import datetime as dt


"""
Library for reading and writing pdf for Menus.
Call get_days to instantly receive a List[str]
for each day. Then call getter functions from day.py
of a particular day to receive the courses of a day.
"""


def get_monday_and_friday():
    """
    returns datetime objects for the monday and friday dates
    of the current week.
    """
    today = dt.datetime.today()
    current_weekday = today.weekday()  # Monday is 0 and Sunday is 6

    # Calculate the difference between today and Monday
    days_to_monday = current_weekday
    monday = today - dt.timedelta(days=days_to_monday)

    # Calculate the difference between today and Friday
    days_to_friday = 4 - current_weekday
    friday = today + dt.timedelta(days=days_to_friday)

    return monday, friday


def save_pdf(response: requests.Response) -> str:
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
        os.mkdir(dirpath)

    # if the file already exists, make a warning that is will be
    # overridden
    if os.path.exists(path_to_file):
        print("File already exists! Overwriting...")

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
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        # menu only has one page
        text: str = pdf_reader.pages[0].extract_text((0, 90))

    return text


def read_date(pdf_path: str) -> dt.datetime:
    """
    Reads the pdf and returns the date of monday of the week.
    """
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        # menu only has one page
        text: str = pdf_reader.pages[0].extract_text((0, 90))


def strip_pdf(text: List[str]) -> None:
    """
    Removes redundant information on the top and bottom of file, as
    well as stripping each line in the text.
    """
    while text[0][:2] != "MO":
        text.pop(0)

    while text[-1][0] == " " or text[-1] == "Die ALLERGENE sind im Speisesaal auf einem Aushang ersichtlich.  ":
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


def get_days(path: str) -> List[List[str]]:
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
    return split_weekdays(lines)
