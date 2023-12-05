from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import datetime as dt
import pandas as pd

"""
This package includeswhole analyzation part of
the program.
"""


def get_df() -> pd.DataFrame:
    """
    Returns a dataframe from the excel sheet in analysis/analysis.xlsx
    """
    file_path: str = os.path.realpath(os.path.join(
        os.path.dirname(__file__), "..", "analysis", "analysis.xlsx"))
    try:
        pd.read_excel(file_path)
    except FileExistsError:
        print("file not existing yet")
