import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

ROOT_DIR = os.path.dirname(BASE_DIR)

STORAGE_PATH = os.path.join(ROOT_DIR, "Storage")
DATABASE_MAILS_PATH = os.path.join(STORAGE_PATH, "Mails_datas.db")
DATABASE_FEATURES_PATH = os.path.join(STORAGE_PATH, "Features_datas.db")
DATABASE_FINAL_PATH = os.path.join(STORAGE_PATH, "Final_datas.db")

GIBBERISH_PATH = os.path.join(BASE_DIR, "gibberish_tools")
