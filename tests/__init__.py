import logging

from pathlib import Path


from bullpen.logging import LOGGER, set_log_directory

# Clear all default log handlers and set up a test logfile
LOGGER.handlers.clear()
LOGGER.setLevel(logging.DEBUG)
set_log_directory(Path(__file__).parents[1] / "logs" / "bullpen.test.log")
