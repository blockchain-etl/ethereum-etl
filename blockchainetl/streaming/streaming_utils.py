import logging
import signal
import sys

from blockchainetl.logging_utils import logging_basic_config


def configure_signals():
    def sigterm_handler(_signo, _stack_frame):
        # Raises SystemExit(0):
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)


def configure_logging(filename):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging_basic_config(filename=filename)
