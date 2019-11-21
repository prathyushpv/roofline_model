import logging
import sys
from datetime import datetime

def create_logger(filename = None):
    if filename is None:
        now = datetime.now()
        filename = "log_" + now.strftime("%m_%d_%Y__%H_%M_%S")
    try:
        logger = logging.getLogger("main_log")
    except OSError:
        pass
    logger.setLevel(logging.DEBUG)
    # create a file handler
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    # create a logging format
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter = MyFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter = MyFormatter()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


# Custom formatter
class MyFormatter(logging.Formatter):
    err_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    info_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    dbg_fmt = "%(message)s"

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = MyFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._fmt = MyFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._fmt = MyFormatter.err_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result