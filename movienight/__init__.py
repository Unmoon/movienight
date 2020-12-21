import logging
import sys

root_log = logging.getLogger("movienight")
root_log.setLevel(logging.DEBUG)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
log_handler.setFormatter(log_formatter)
root_log.addHandler(log_handler)
root_log.debug("Logging initialized for '%s'", __name__)
