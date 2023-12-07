from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import os
import sys
import logging
import datetime as dt

from logger import logger


class Day:
    def __init__(self, date: dt.datetime, soup: Optional[str] = None, main: Optional[List[str]] = None,
                 dessert: Optional[str] = None, dinner: Optional[str] = None, text: Optional[List[str]] = None,
                 comment: Optional[str] = None) -> None:
        """
        Constructor for day.
        Provide either all the courses or a text.
        text must be the List[str] containing ONLY the lines relevant for the day!!!!
        (see format in pdf.py get_days())
        """
        self._text: Optional[List[str]] = None
        self.soup: str
        self.main: List[str]
        self.dessert: str
        self.dinner: str

        self.date: dt.datetime = date
        self.comment: str = comment if comment is not None else "none"

        # 4 is min length for one day, EXCEPT: there is no school
        # 4 = 1 soup + dinner, 2 for 2 main courses, 1 for dessert
        if len(text) < 4:
            self.comment = ">>".join(text)

            self.soup: Optional[str] = "none"
            self.main: Optional[List[str]] = ["none"]
            self.dessert: Optional[str] = "none"
            self.dinner: Optional[str] = "none"

            return

        if text is None:
            # if text is None, get the values from the other parameters
            self._text = None
            self.soup = soup
            self.main = main
            self.dessert = dessert
            self.dinner = dinner
        else:
            # otherwise, get values from the text
            self._text = text
            self.soup = self._get_soup()
            # print(self._text)
            self.main = self._get_main()
            if self.main is None:
                raise ValueError(
                    f"Main courses could not be filtered.\ntext=\n{self._text}")
            self.dessert = self._get_dessert()
            self.dinner = self._get_dinner()

    @staticmethod
    def get_weekdays(week: List[List[str]], start_date: dt.datetime) -> List[Day]:
        day_week: List[Day] = []
        date: dt.datetime = start_date
        for day in week:
            try:
                day_week.append(Day(date, text=day))
            except ValueError:
                print(f"{date.strftime('%d%m%Y was skipped! (ValueError)')}")
                logger.warning(
                    f"{date.strftime('%d%m%Y was skipped! (ValueError)')}")
            date = date + dt.timedelta(days=1)

        return day_week

    def _get_soup(self) -> str:
        """
        Soup should always be the first part of the day.
        Split for removing the dinner part.
        """
        return self._text[0].split("  ")[0].strip()

    def _get_dinner(self) -> str:
        """
        Returns the dinner for a day. Does this by assuming that the soup
        only takes up one line and that it is located between the soup and
        Salatbuffet.
        """
        # get first line of dinner (right to soup)
        try:
            dinner: str = self._text[0].split("  ")[1].strip()
        except IndexError:
            # fallback for when dinner is not seperated by two spaces
            logger.warning(f"DINNER COULD NOT BE SEPERATED! text={self._text}")
            dinner: str = self._text[0].split(" ")[-1].strip()

        # get middle lines of dinner (full lines)
        i: int = 1
        while "Salatbuffet" not in self._text[i]:
            dinner += " " + self._text[i]
            i += 1

        # Salatbuffet in day[pntr] => last dinner line reached
        if len(self._text[i]) > 13:  # not only Salatbuffet in line
            # => dinner in this line as well
            dinner += " " + self._text[i].split("  ")[0].strip()

        return dinner.strip()

    def _get_main(self) -> Optional[List[str]]:
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
        for i in range(len(self._text)):
            if "Salatbuffet" in self._text[i]:
                start_index = i + 1
                break

        # lunches are listed from the line after Salatbuffet until
        # the line before the last line
        lunch_slice: List[str] = self._text[start_index:len(self._text) - 1]

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

        elif len(lunch_slice) == 4:
            # the odds of one meal taking up 3 lines are very slim.
            # Therefore, assume, 2 lines for first meal, 2 for second
            lunches.append(lunch_slice[0] + " " + lunch_slice[1])
            lunches.append(lunch_slice[2] + " " + lunch_slice[3])

            return lunches

        elif len(lunch_slice) == 5:
            # now there are 2 smaller segments, 3 meals
            lunches.append(lunch_slice[0])

            min1: str = min(lunch_slice, key=len)
            lunch_slice_minus_smallest = lunch_slice.copy()
            lunch_slice_minus_smallest.remove(min1)
            min2: str = min(lunch_slice_minus_smallest, key=len)

            if lunch_slice[1] == min1 or lunch_slice[1] == min2:
                lunches[0] += " " + lunch_slice[1]
                # next has to be next meal if first has two lines
                lunches.append(lunch_slice[2])
                if lunch_slice[3] == min1 or lunch_slice[3] == min2:
                    lunches[1] += " " + lunch_slice[3]
                    lunches.append(lunch_slice[4])
                else:
                    lunches.append(lunch_slice[3])
                    lunches[2] += " " + lunch_slice[4]

            else:
                # now we know that the next two meals have to be two liners
                lunches.append(lunch_slice[1] + " " + lunch_slice[2])
                lunches.append(lunch_slice[3] + " " + lunch_slice[4])

            return lunches

        elif len(lunch_slice) == 6:
            lunches.append(lunch_slice[0] + " " + lunch_slice[1])
            lunches.append(lunch_slice[2] + " " + lunch_slice[3])
            lunches.append(lunch_slice[4] + " " + lunch_slice[5])

            return lunches

        else:
            logger.warning(
                f"Error at retaining lunch., lunch_slice={lunch_slice}")
            return None

    def _get_dessert(self):
        return self._text[-1]

    @property
    def weekday(self) -> int:
        return self.date.weekday()

    @property
    def main_string(self) -> str:
        if self.main is not None:
            return ";".join(self.main)
        return None

    @property
    def description(self) -> Dict[str, object]:
        """
        Returns all the relevant information for the day
        in a dictionairy.
        """
        return {
            # "date": self.date.strftime("%Y-%m-%d"),
            "soup": self.soup,
            "main": self.main_string,
            "dessert": self.dessert,
            "dinner": self.dinner,
            "comment": self.comment,
        }

    def __repr__(self):
        return f"date    = {self.date}\nsoup    = {self.soup}\nmain    = {self.main_string}\n\
dessert = {self.dessert}\ndinner  = {self.dinner}\ncomment = {self.comment}"

    def __str__(self):
        return f'<Day date="{self.date}" soup="{self.soup}" main="{self.main_string}"\
dessert="{self.dessert}" dinner="{self.dinner}" comment="{self.comment}">'
