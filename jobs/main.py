import logging
import logging.config

from app.src.logger import LOGGER_CFG_PATH

# Logger inheritance configuration
logging.config.fileConfig(LOGGER_CFG_PATH)
root_logger = logging.getLogger()
root_logger.propagate = True


if __name__ == "__main__":
    from app.src.etl import run

    run()
