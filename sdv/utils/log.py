import os
import logging
from logging.handlers import TimedRotatingFileHandler

LOGGING_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def setup_logger():
    logger = logging.getLogger("UploadFarm")
    log_level = LOGGING_LEVELS[os.environ.get("SDV_LOGGING_LEVEL", "info")]
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    if not os.path.isdir("logs"):
        os.mkdir("logs")

    log_file = "logs/sdv.log"
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
    file_handler.setLevel(log_level)

    file_handler.suffix = "%Y%m%d"

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


app_logger = setup_logger()
