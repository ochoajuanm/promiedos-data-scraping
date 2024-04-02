import logging

from app.src.db_connectors import PostgreSQLDatabaseManager

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    db_manager = PostgreSQLDatabaseManager()
    db_manager.connect()
    db_manager.make_migrations()
