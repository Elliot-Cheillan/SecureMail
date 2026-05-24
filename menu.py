# Menu and pipeline orchestration for SecureMail
# Training is separate : run model/training.py once to train and save the model.
import os
import sqlite3
import sys


def ask(question, valid_answers):
    while True:
        answer = input(question).strip().lower()
        if answer in valid_answers:
            return answer
        print(f"Invalid answer. Expected: {', '.join(valid_answers)}")


def menu():  # beautiful menu !!
    print("╔══════════════════════════════════╗")
    print("║        SecureMail Pipeline       ║")
    print("╠══════════════════════════════════╣")
    print("║  1. Mail ingestion               ║")
    print("║  2. Feature engineering          ║")
    print("║  3. Inference (scan)             ║")
    print("║  4. Full pipeline  (1 → 2 → 3)   ║")
    print("║  5. Reset Databases.             ║")
    print("║  q. Quit                         ║")
    print("╚══════════════════════════════════╝")
    return ask("\nYour choice (1/2/3/4/5/q): ", ["1", "2", "3", "4", "5", "q"])


def run_ingestion():
    from ingestion.pipeline import setup_ingestion_logger
    from ingestion.cli import run_ingestion

    setup_ingestion_logger()
    run_ingestion()


def run_features():
    from feature_engineering.logger import setup_features_logger
    from feature_engineering.cli import run_features

    setup_features_logger()
    run_features()


def run_inference():
    from model.predict import run_inference
    from model.logger import setup_model_logger

    setup_model_logger()
    run_inference()


def run_all():
    from ingestion.pipeline import setup_ingestion_logger as setup_ingestion_logger
    from ingestion.cli import run_ingestion_full
    from feature_engineering.logger import (
        setup_features_logger as setup_features_logger,
    )
    from feature_engineering.cli import run_features_full

    print(
        "\nDo you want to recreate a database or add new mails from the precedent one ?"
    )
    print("\n1. I want to start from zero")
    print("\n2. I want to add only mails I didn't compute")
    full_pipeline_question = ask("\nYour choice : (1/2)\n", ["1", "2"])
    if full_pipeline_question == "1":
        parameter = "new"
    else:
        parameter = "fill"
    print("\n── Step 1: Mail ingestion ──")
    setup_ingestion_logger()
    run_ingestion_full(parameter)
    print("\n── Step 2: Feature engineering ──")
    setup_features_logger()
    run_features_full(parameter)
    print("\n── Step 3: Inference ──")
    run_inference()


def reset_databases():
    confirm = ask(
        "\nThis will erase all data in all databases. Are you sure? (yes/no): ",
        ["yes", "no"],
    )
    if confirm == "no":
        print("Reset cancelled.")
        return

    from ingestion.config import DB_PATH
    from feature_engineering.config import DATABASE_FEATURES_PATH, DATABASE_FINAL_PATH
    from ingestion.pipeline.database import initialize_database
    from feature_engineering.etl import initialize_features_database

    paths = [DB_PATH, DATABASE_FEATURES_PATH, DATABASE_FINAL_PATH]

    for path in paths:
        if os.path.exists(path):
            with sqlite3.connect(path) as conn:
                conn.execute("VACUUM")
            print(f"VACUUM done — {path}")

    with sqlite3.connect(DB_PATH) as conn:
        initialize_database(conn.cursor())

    initialize_features_database()
    print("All databases reset and vacuumed.")


def run_menu():
    choix = menu()
    if choix == "1":
        run_ingestion()
    elif choix == "2":
        run_features()
    elif choix == "3":
        run_inference()
    elif choix == "4":
        run_all()
    elif choix == "5":
        reset_databases()
    elif choix == "q":
        print("Goodbye.")
        sys.exit(0)
