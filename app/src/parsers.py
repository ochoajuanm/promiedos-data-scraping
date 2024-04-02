import logging
import re
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import date, timedelta
from typing import Union

import pandas as pd
from bs4 import ResultSet, Tag

from app.src.exceptions import DetailParseException, GoalsParseException
from app.src.models import Match

# Load logger
logger = logging.getLogger(__name__)


class DataParser(ABC):
    def __init__(self, days_diff: int) -> None:
        """Initialize the DataParser.

        Args:
            days_diff (int): The number of days difference to consider when parsing data.
        """
        self.today_date = date.today()
        self.days_diff = days_diff

    @abstractmethod
    def transform(self) -> pd.DataFrame:
        raise NotImplementedError("Transform method must be implemented by subclasses")


class PromiedosDataParser(DataParser):
    """Class for parsing data from Promiedos."""

    def __init__(self, days_diff: int) -> None:
        """Initialize the PromiedosDataParser.

        Args:
            days_diff (int): The number of days difference to consider when parsing data.
        """
        super().__init__(days_diff)
        self.yesterday = (self.today_date - timedelta(days=self.days_diff)).strftime("%d-%m-%Y")
        self.today = self.today_date.strftime("%d-%m-%Y")

    def _try_get_param(self, element: Tag) -> str:
        """Attempt to extract text from a BeautifulSoup Tag element."""
        try:
            if element is not None:
                return element.text.strip(" ")
        except DetailParseException:
            pass
        except GoalsParseException:
            pass
        return ""

    def _transform_matches(self, tables: ResultSet, period: str) -> Union[pd.DataFrame, None]:
        """Transform the scraped match data into a DataFrame.

        Args:
            tables (Dict): A dictionary containing the scraped match data.
            time (str): The time frame for which the data is being transformed. Valid values are 'yesterday' or 'today'.

        Returns:
            pd.DataFrame: The DataFrame containing the transformed match data.

        Raises:
            KeyError: If a key is not found in the dictionary.
        """
        if period == "yesterday":
            match_date = self.yesterday
        elif period == "today":
            match_date = self.today

        match_rows = []

        for table in tables:
            tournament = table.find("tr", class_="tituloin").text.strip(" ")
            matches = table.find_all("tr", id=re.compile("^\\d{1,3}_?\\d+$"))
            for match in matches:
                match_id = match.get("id")
                match_row = Match(
                    home_team=self._try_get_param(match.find("span", id=re.compile("^t1[\\d_]*$"))),
                    away_team=self._try_get_param(match.find("span", id=re.compile("^t2[\\d_]*$"))),
                    home_goals=self._try_get_param(match.find("td", class_="game-r1")),
                    away_goals=self._try_get_param(match.find("td", class_="game-r2")),
                    tournament=tournament,
                    home_scorers=self._try_get_param(table.find("td", id="g1_" + match_id)),
                    away_scorers=self._try_get_param(table.find("td", id="g2_" + match_id)),
                    details=self._try_get_param(table.find("tr", class_="choy")),
                    match_date=match_date,
                )
                match_rows.append(match_row)
        logger.debug(f"Parsing {len(match_rows)} matches data from {period}...")
        return pd.DataFrame([asdict(match_row) for match_row in match_rows])

    def transform(self, tables: ResultSet, entity: str, time: str) -> Union[pd.DataFrame, None]:
        """Transform the scraped data into a DataFrame.

        Args:
            tables (ResultSet): The ResultSet containing the scraped data.
            entity (str): The entity type to transform. Valid values are 'matches'.
            time (str): The time frame for which the data is being transformed. Valid values are 'yesterday' or 'today'.

        Returns:
            pd.DataFrame: The DataFrame containing the transformed data.

        Raises:
            KeyError: If a key is not found in the dictionary.
        """
        if entity == "matches":
            logger.debug(f"Transforming data from entity '{entity}' on period '{time}'...")
            return self._transform_matches(tables, time)
