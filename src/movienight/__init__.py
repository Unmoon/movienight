import logging
import sys

from .config import read_config

read_config()

root_log = logging.getLogger(__name__)
root_log.setLevel(logging.DEBUG)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
log_handler.setFormatter(log_formatter)
root_log.addHandler(log_handler)
root_log.debug("Logging initialized for '%s'", __name__)
