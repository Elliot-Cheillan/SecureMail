import os
import sqlite3
import logging
from ingestion.config import DB_PATH
from ingestion.pipeline import build_database, add_new_mails, enrich_pending_links


logger = logging.getLogger(__name__)


def ask(question, valid_answers):
    while True:
        answer = input(question).strip().lower()
        if answer in valid_answers:
            return answer
        print(f"Invalid answer. Expected: {', '.join(valid_answers)}")


def ask_enrichment():
    return (
        ask("\nEnrich pending links now? (yes/no): ", ["yes", "no"]) == "yes"
    )  # TAKES TIME


def menu_db_exists(cursor, conn):
    print("\nA database already exists. What do you want to do?")
    print("  1. Rebuild everything (deletes existing database)")
    print("  2. Enrich pending links only")
    print("  3. Add new mails without overwriting the database")

    choice = ask("\nYour choice (1/2/3): ", ["1", "2", "3"])

    if choice == "1":
        logger.info("Full rebuild requested.")
        build_database(cursor, conn)
        if ask_enrichment():
            enrich_pending_links(cursor, conn)

    elif choice == "2":
        enrich_pending_links(cursor, conn)

    elif choice == "3":
        add_new_mails(cursor, conn)
        if ask_enrichment():
            enrich_pending_links(cursor, conn)


def menu_db_missing(cursor, conn):
    logger.info("No database found. Building...")
    build_database(cursor, conn)
    if ask_enrichment():
        enrich_pending_links(cursor, conn)


def run_ingestion():
    db_exists = os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        if db_exists:
            menu_db_exists(cursor, conn)
        else:
            menu_db_missing(cursor, conn)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        conn.commit()
        raise
    finally:
        conn.close()


def run_ingestion_full(
    new_or_fill,
):  # for the full pipeline, it'll have a different menu
    db_exists = os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    logger.info("It can takes few minutes, be patient...")
    try:
        if new_or_fill == "new":
            logger.info("Building Database...")
            build_database(cursor, conn)
            enrich_pending_links(cursor, conn)
        if new_or_fill == "fill":
            if db_exists:
                logger.info("Adding new mails to database...")
                add_new_mails(cursor, conn)
                logger.info("Enriching new links...")
                enrich_pending_links(cursor, conn)
            else:
                logger.error(
                    "No Database found ! Try to restart the program and build from zero"
                )
    except Exception as e:
        logger.error(f"Fatal error {e}", exc_info=True)
        raise
    finally:
        conn.close()
