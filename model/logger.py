import logging
import os

LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "scan_results.log"
)


def setup_model_logger():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s")

    # setup two types of handler for this, stream for the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # and this handler is for write only on the log file, useful to not have 13000 prints on the console for the model predictions part
    file_handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root.addHandler(stream_handler)
    root.addHandler(file_handler)
