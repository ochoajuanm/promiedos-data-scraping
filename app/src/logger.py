import os

# Logging paths
current_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
logs_dir = os.path.abspath(os.path.join(project_dir, "logs"))
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

LOGGER_CFG_FILE = 'logging.conf'
LOGGER_CFG_PATH = os.path.join(project_dir, LOGGER_CFG_FILE)
