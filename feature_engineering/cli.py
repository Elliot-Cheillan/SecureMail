import os
from feature_engineering.etl import (
    initialize_features_database,
    inject_all_features,
    inject_final_datas,
)
from feature_engineering.config import DATABASE_FEATURES_PATH
from feature_engineering.logger import setup_features_logger
import logging


def ask(question, valid_answers):
    while True:
        answer = input(question).strip().lower()
        if answer in valid_answers:
            return answer
        print(f"Invalid answer. Expected: {', '.join(valid_answers)}")


def ask_featuring():  # it's not as long as the parsing, it takes like 1 or 2 minutes
    return ask("\nAdd features now? (yes/no): ", ["yes", "no"]) == "yes"


def menu_db_exists():
    print("\nA features database already exists. What do you want to do?")
    print("  1. Rebuild everything (deletes existing database)")
    print("  2. Add features for unprocessed mails")

    choice = ask("\nYour choice (1/2): ", ["1", "2"])

    if choice == "1":
        print("Rebuilding the database.")
        initialize_features_database()
        if ask_featuring():
            inject_all_features("replace")
            inject_final_datas()

    elif choice == "2":
        inject_all_features("append")
        inject_final_datas()


def menu_db_missing():
    print("No database found. Building...")
    initialize_features_database()
    if ask_featuring():
        inject_all_features("replace")
        inject_final_datas()


def run_features():
    setup_features_logger()
    db_exists = os.path.exists(DATABASE_FEATURES_PATH)
    try:
        if db_exists:
            menu_db_exists()
        else:
            menu_db_missing()
    except Exception as e:
        logging.getLogger(__name__).error(f"Fatal error: {e}", exc_info=True)
        raise


def run_features_full(
    new_or_fill,
):  # the running when you choose the full pipeline option in the menu
    setup_features_logger()
    db_exists = os.path.exists(DATABASE_FEATURES_PATH)
    try:
        if new_or_fill == "new":
            initialize_features_database()
            inject_all_features("replace")
            inject_final_datas()
        if new_or_fill == "fill":
            if db_exists:
                inject_all_features("append")
                inject_final_datas()
            else:
                logging.getLogger(__name__).error(
                    f"No Features database found ! Try to restard the program and build from zero"
                )
    except Exception as e:
        logging.getLogger(__name__).error(f"Fatal error : {e}", exc_info=True)
