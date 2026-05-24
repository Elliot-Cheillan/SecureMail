import logging
import os

LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pipeline.log"
)


def setup_ingestion_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    # DONT DELETE THESES LINES IF YOU DONT WANT TO HAVE ALL THE INFOS FOR ALL CONNECTIONS TO ALL THE WEBSITES WITH REQuESTS (you will not even see the batchs logs)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncwhois").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)

    root.addHandler(stream_handler)
    root.addHandler(file_handler)
