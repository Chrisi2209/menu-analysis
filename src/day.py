from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import datetime as dt


# GETTERS

def get_soup(day: List[str]) -> str:
    """
    Soup should always be the first part of the day.
    Split for removing the dinner part.
    """
    return day[0].split("  ")[0].strip()


def get_dinner(day: List[str]) -> str:
    """
    Returns the dinner for a day. Does this by assuming that the soup
    only takes up one line and that it is located between the soup and
    Salatbuffet.
    """
    # get first line of dinner (right to soup)
    dinner: str = day[0].split("  ")[1].strip() + " "

    # get middle lines of dinner (full lines)
    i: int = 1
    while "Salatbuffet" not in day[i]:
        dinner += day[i] + " "
        i += 1

    # Salatbuffet in day[pntr] => last dinner line reached
    if len(day[i]) > 13:  # not only Salatbuffet in line
        dinner += day[i].split("  ")[0].strip()

    return dinner.strip()


def get_main(day: List[str]) -> Optional[List[str]]:
    """
    Returns the lunches for the day in a list. It is very hard to find
    out which line belongs to which meal if there are 3 lines for lunch.
    Managed by assigning the shortest line to the one before, assuming that
    the second line of one meal will probably be smaller than the other
    meal which only has one line. Of course there still are exeptions to
    this rules (like when there are 3 meals). These errors need to be 
    corrected manually.
    """
    # a value that is surely out of range for this use case
    start_index: int = 99
    # find salatbuffet line
    for i in range(len(day)):
        if "Salatbuffet" in day[i]:
            start_index = i + 1
            break

    # lunches are listed from the line after Salatbuffet until
    # the line before the last line
    lunch_slice: List[str] = day[start_index:len(day) - 1]

    # SOMEHOW KNOW WHICH LINES BELONG TO THE SAME MEAL
    if len(lunch_slice) == 2:
        # 2 lines just represent the two meals
        return lunch_slice

    lunches: List[str] = []

    if len(lunch_slice) == 3:
        # hard part about this is to find out where the third line belongs to
        lunches.append(lunch_slice[0])

        # create the list for the second meal beforehand
        lunches.append("")

        # 0 if line 1 is smallest, 1 if line 2 is smallest
        index: int = lunch_slice.index(min(lunch_slice[1:], key=len)) - 1

        lunches[index] += " " + lunch_slice[1]

        lunches[1] += lunch_slice[2]
        # strip, because lunches[index] += " " + lunch_slice[1] could add
        # a space at start of line
        lunches[1] = lunches[1].strip()

        return lunches

    if len(lunch_slice) == 4:
        # the odds of one meal taking up 3 lines are very slim.
        # Therefore, assume, 2 lines for first meal, 2 for second
        lunches.append(lunch_slice[0] + " " + lunch_slice[1])
        lunches.append(lunch_slice[2] + " " + lunch_slice[3])

        return lunches

    else:
        print("Error at retaining lunch.")
        return None


def get_dessert(day: List[str]):
    return day[-1]
