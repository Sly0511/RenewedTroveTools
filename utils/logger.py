import logging
import logging.handlers
from datetime import datetime

timestamped_log = "logs/{logger_level}_{logger_name}_" + datetime.utcnow().strftime(
    "%Y-%m-%d_%H-%M-%S-%f.log"
)


class ColourFormatter(logging.Formatter):
    """This class formats logs with a color in stdout.

    The goal is to provide logs with color coding for easier readability
    as well as properly format string size for a more table like display"""

    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: logging.Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[32m%(name)-24s\x1b[0m \x1b[37m%(message)s\x1b[0m ",
            "%Y-%m-%d %H:%M:%S",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"
        output = formatter.format(record)
        record.exc_text = None
        return output


class Logger:
    """Custom logger object for streamlined logging.

    This class implements the logging library and provides an automatic way of logging in 3 outputs
    It will output into a INFO log file, a DEBUG log file and into console in a somewhat concise format
    """

    def __init__(self, name, level=logging.INFO):
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name:<24}: {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
        )
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(level)
        self.stream_handler.setFormatter(ColourFormatter())
        self.logger.addHandler(self.stream_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
