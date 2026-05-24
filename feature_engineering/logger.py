import logging
import os
from logging.handlers import RotatingFileHandler

LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "feature_engineering.log"
)


def setup_features_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_PATH, mode="w", maxBytes=5 * 1024 * 1024, backupCount=1, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root.addHandler(stream_handler)
    root.addHandler(file_handler)
