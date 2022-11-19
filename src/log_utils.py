import logging, sys

# https://orcahmlee.github.io/python/python-logging/

# Follow this link: https://stackoverflow.com/a/56944256
grey = "\x1b[38;20m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"

def stripColors(s):
    for term in [grey, yellow, red, bold_red, reset]:
        s = s.replace(term, '')
    return s

class CustomFormatter(logging.Formatter):
    
    format = "[%(asctime)s] (%(levelname)-4s) %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def createLogger(logger_name, log_level=logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.setLevel(log_level)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(log_level)
    ch.setFormatter(CustomFormatter())
    logger.handlers = [ch]
    return logger

