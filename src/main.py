from typing import List, Tuple, Dict, Optional
import os
import logging
import requests
import PyPDF2
import datetime as dt


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


def get_monday_and_friday():
    today = dt.datetime.today()
    current_weekday = today.weekday()  # Monday is 0 and Sunday is 6

    # Calculate the difference between today and Monday
    days_to_monday = current_weekday
    monday = today - dt.timedelta(days=days_to_monday)

    # Calculate the difference between today and Friday
    days_to_friday = 4 - current_weekday
    friday = today + dt.timedelta(days=days_to_friday)

    return monday, friday


def save_pdf(response: requests.Response) -> Tuple[int, str]:
    monday, friday = get_monday_and_friday()
    path_to_file: str = os.path.join(os.path.dirname(
        __file__), "..", "stored_menus", f"Speiseplan_{monday.strftime('%d_%m')}_{friday.strftime('%d_%m_%y')}.pdf")
    dirpath: str = os.path.dirname(path_to_file)

    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

    if os.path.exists(path_to_file):
        print("File already exists! Aborting.")
        return -1, path_to_file

    with open(path_to_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)

    return 0, path_to_file


def read_pdf(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        # menu only has one page
        text: str = pdf_reader.pages[0].extract_text((0, 90))

    return text


def main():
    url: str = "https://www.campusm.at/download/339/"
    response = requests.get(url, stream=True)

    if response.status_code != 200:
        print(f"Request to {url} failed! Aborting.")
        return 1

    print("Request successful")

    # save the pdf
    code, path = save_pdf(response)
    if code != 0:
        print("some error occured while saving pdf")
        # return code

    # read the text
    text: str = read_pdf(path)
    print(type(text))


if __name__ == "__main__":
    main()
