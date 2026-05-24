import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

STORAGE_PATH = os.path.join(ROOT_DIR, "storage")
DATABASE_FINAL_PATH = os.path.join(STORAGE_PATH, "Final_datas.db")

SAVED_DIR = os.path.join(BASE_DIR, "saved")
MODEL_PATH = os.path.join(SAVED_DIR, "best_model.pth")
SCALER_PATH = os.path.join(SAVED_DIR, "scaler.pkl")
