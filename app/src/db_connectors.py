import logging
import sys
from abc import ABC, abstractmethod
from typing import Dict, Literal, Union

import pandas as pd
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError

# Load logger
logger = logging.getLogger(__name__)


class SQLDatabaseManager(ABC):
    """Abstract base class for managing SQL databases."""

    def __init__(self):
        """Initialize the SQLDatabaseManager."""
        self.db_user = config("POSTGRES_USER")
        self.db_password = config("POSTGRES_PASSWORD")
        self.db_host = config("POSTGRES_HOST")
        self.db_port = config("POSTGRES_PORT")
        self.db_name = config("POSTGRES_DATABASE")
        self.db_schema = config("POSTGRES_SCHEMA")

    @abstractmethod
    def connect(self):
        """Connect to the SQL database."""
        raise NotImplementedError("Connect method must be implemented by subclasses")

    @abstractmethod
    def load(self):
        """Load data into the SQL database."""
        raise NotImplementedError("Load method must be implemented by subclasses")

    @abstractmethod
    def close(self):
        """Closes SQL database connection."""
        raise NotImplementedError("Close method must be implemented by subclasses")


class PostgreSQLDatabaseManager(SQLDatabaseManager):
    def __init__(self):
        super().__init__()
        self.engine = None

    def connect(self) -> Union[Engine, None]:
        """Connect to the PostgreSQL database and return the SQLAlchemy Engine object.

        Returns:
            Engine: The SQLAlchemy Engine object representing the PostgreSQL database connection.

        Raises:
            Exception: If there is an error connecting to the database.
        """
        url = f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
        connect_args = {'options': f'-csearch_path={self.db_schema}'}
        isolation_level = "AUTOCOMMIT"
        self.engine = self._create_engine(url, connect_args, isolation_level)

    def make_migrations(self) -> None:
        """Perform database migrations. Creates Database and Tables"""
        if not self.engine:
            self.connect()

        with open("sql/create_database.sql", "r") as sql_file:
            create_database = sql_file.read()

        with open("sql/create_tables.sql", "r") as sql_file:
            create_tables = sql_file.read()

        if self.engine is not None:
            with self.engine.connect() as conn:
                try:
                    conn.execute(create_database)
                    logger.info(f"Database created successfully")
                except ProgrammingError as e:
                    logger.error(
                        f"Error creating Database {self.db_name}: {e}.",
                        exc_info=sys.exc_info(),
                        stack_info=True,
                    )
                try:
                    conn.execute(create_tables)
                    logger.info(f"Tables created successfully")
                except ProgrammingError as e:
                    logger.error(
                        f"Error creating Tables on Schema {self.db_schema}: {e}.",
                        exc_info=sys.exc_info(),
                        stack_info=True,
                    )

    def _create_engine(
        self, url: str, connect_args: Dict, isolation_level: str
    ) -> Union[Engine, None]:
        """Create the SQLAlchemy engine.

        Args:
            url (str): The connection URL for the database.
            connect_args (Dict): Additional connection arguments.
            isolation_level (str): The isolation level for the connection.

        Returns:
            Engine: The SQLAlchemy Engine object representing the database connection.

        Raises:
            Exception: If there is an error creating the engine.
        """
        try:
            engine = create_engine(url, connect_args=connect_args, isolation_level=isolation_level)
            if engine:
                logger.debug("Connected to PostgreSQL database successfully.")
                return engine  # type: ignore
        except Exception as e:
            logger.error(
                f"Error connecting to PostgreSQL database: {e}.",
                exc_info=sys.exc_info(),
                stack_info=True,
            )
            return None

    def load(
        self, df: pd.DataFrame, table_name: str, insert_method: Literal['fail', 'replace', 'append']
    ) -> None:
        """Load data into a specified table in the PostgreSQL database.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to load.
            table_name (str): The name of the table to insert data into.
            insert_method (str): The method to use when inserting data. Valid values are 'fail', 'replace', 'append', 'delete', or 'upsert'.

        Raises:
            Exception: If there is an error loading data into the database.
        """
        if not self.engine:
            self.connect()

        with self.engine.connect() as conn:
            df.to_sql(
                table_name,
                schema=str(self.db_schema),
                con=conn,
                index=False,
                if_exists=insert_method,
            )
            logger.debug(f"Inserted {df.shape[0]} rows to PostgreSQL successfully.")

    def close(self):
        """Close the connection to the PostgreSQL database."""
        if self.engine is not None:
            self.engine.dispose()
            logger.debug("Connection to PostgreSQL database closed.")
