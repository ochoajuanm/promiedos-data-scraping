import logging
import sys
import time
from abc import ABC, abstractmethod
from typing import Any, List

from app.src.db_connectors import PostgreSQLDatabaseManager
from app.src.exceptions import ExtractProcessException, LoadProcessException, TransformProcessException
from app.src.parsers import PromiedosDataParser
from app.src.scrapers import PromiedosScraper

logger = logging.getLogger(__name__)


class ETL(ABC):
    """Abstract base class for ETL (Extract, Transform, Load) process."""

    def __init__(self, urls: List[str], entity: str, period: str) -> None:
        """Initialize the ETL process.

        Args:
            urls (List[str]): List of URLs to scrape data from.
            entity (str): Type of entity to extract (e.g., 'matches').
            period (str): Period for which to extract data (e.g., 'yesterday').
        """
        self.urls = urls
        self.entity = entity
        self.period = period
        self.extracted_data = None
        self.transformed_data = None

    @abstractmethod
    def extract(self) -> Any:
        """Extract data from the specified URLs."""
        raise NotImplementedError("Extract method must be implemented by subclasses")

    @abstractmethod
    def transform(self) -> Any:
        """Transform the extracted data."""
        raise NotImplementedError("Transform method must be implemented by subclasses")

    @abstractmethod
    def load(self) -> Any:
        """Load the transformed data into the database."""
        raise NotImplementedError("Load method must be implemented by subclasses")


class PromiedosETL(ETL):
    """ETL process for extracting, transforming, and loading data from Promiedos."""

    def __init__(self, urls: List[str], entity: str, period: str) -> None:
        """Initialize the Promiedos ETL process."""
        super().__init__(urls, entity, period)

    def extract(self) -> None:
        """Extract data from Promiedos."""
        scraper = PromiedosScraper(self.urls)
        try:
            self.extracted_data = scraper.extract(self.entity, self.period)
        except Exception:
            raise ExtractProcessException("Could not extract data from Promiedos")

    def transform(self) -> None:
        """Transform the extracted data."""
        parser = PromiedosDataParser(days_diff=1)
        if self.extracted_data is not None:
            try:
                self.transformed_data = parser.transform(self.extracted_data, self.entity, self.period)
            except Exception:
                raise TransformProcessException("Could not transform data from Promiedos")
        else:
            raise ExtractProcessException("Empty data from Promiedos to transform")

    def load(self) -> None:
        """Load the transformed data into the database."""
        if self.transformed_data is not None:
            try:
                db_manager = PostgreSQLDatabaseManager()
                db_manager.load(self.transformed_data, "partidos", "append")
                db_manager.close()
            except Exception:
                raise LoadProcessException("Empty data from Promiedos to transform")
        else:
            raise TransformProcessException("Empty transformed data from Promiedos to load")


def run():
    """Run the ETL process."""
    # Ejemplo de uso del logger
    init_time = time.time()
    logger.info("Promiedos Data Scraping is starting...")

    # Data to scrape
    urls = ["https://www.promiedos.com.ar/ayer"]
    entity = "matches"
    period = "yesterday"

    # ETL Process
    try:
        etl = PromiedosETL(urls, entity, period)
        etl.extract()
        etl.transform()
        etl.load()

        end_time = round(time.time() - init_time, 2)
        logger.info(f"Promiedos Data Scraping finished successfully. Time elapsed: {end_time} seconds")
    except ExtractProcessException as e:
        logger.error(f"Error extracting Promiedos Data Scraping: {e}", exc_info=sys.exc_info(), stack_info=True)
    except TransformProcessException as e:
        logger.error(f"Error transforming Promiedos Data Scraping: {e}", exc_info=sys.exc_info(), stack_info=True)
    except LoadProcessException as e:
        logger.error(f"Error loading Promiedos Data Scraping: {e}", exc_info=sys.exc_info(), stack_info=True)
    except Exception as e:
        logger.error(f"Error executing Promiedos Data Scraping: {e}", exc_info=sys.exc_info(), stack_info=True)
