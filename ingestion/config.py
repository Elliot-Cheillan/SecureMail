import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")

DATASET_DIR = os.path.join(ROOT_DIR, "mailbox")
STORAGE_PATH = os.path.join(ROOT_DIR, "storage")
DB_PATH = os.path.join(STORAGE_PATH, "Mails_datas.db")  # ITS ONLY INFOS NOT FEATURES

LABEL_FOLDERS = {
    "ham": os.path.join(
        DATASET_DIR, "ham"
    ),  # deleted actually but you can recreate it if you want to do a dataset training
    "spam": os.path.join(DATASET_DIR, "spam"),  # same as ham folder
    None: os.path.join(DATASET_DIR, "inbox"),
}

HTTP_CONCURRENCY = 100
RDAP_CONCURRENCY = (
    3  # Really long but don't touch, there is many rate problem if it's over 3.
)
BATCH_SIZE = 2000
