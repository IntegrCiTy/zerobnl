import logging

from logging import FileHandler

logger = logging.getLogger("ZEROBNL")
logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(name)s -> %(filename)s :: %(funcName)s :: %(message)s"
)

file_handler = FileHandler("activity.log", "w")

file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

stream_formatter = logging.Formatter("%(levelname)s :: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)
