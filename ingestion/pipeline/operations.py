# Operations on the database: build, fill, enrich links, or add new mails
import os
import logging
from .database import initialize_database
from ingestion.config import LABEL_FOLDERS
from ingestion.services import process_email, enrich_links

logger = logging.getLogger(__name__)


def get_existing_filenames(cursor):
    cursor.execute("SELECT Filename FROM Mails")
    return {row[0] for row in cursor.fetchall()}


def _process_folder(cursor, folder_path, label=None):
    # Insert all .eml files from a DIRECTORY. (the directory of the project is mailbox/inbox)
    # label: 'ham'/'spam' for the training dataset, None for general use. (I deleted spam file and ham file
    # in mailbox, so don't use the label parameter since it's not useful to do predictions)
    inserted = 0
    for filename in os.listdir(folder_path):
        if not filename.endswith(".eml"):
            continue
        try:
            process_email(cursor, os.path.join(folder_path, filename), label, filename)
            inserted += 1
        except Exception as e:
            logger.warning(f"{filename} skipped: {e}", exc_info=True)
    return inserted


def build_database(
    cursor, conn
):  # it's actually build from sqlite3 lib, it may be better with pandas and sql, but I didn't know pandas can open and use .db,
    # so it will be used for featuring and model
    initialize_database(cursor)

    total = 0
    for label, folder_path in LABEL_FOLDERS.items():
        if not os.path.exists(folder_path):
            logger.warning(f"Folder not found, skipped: {folder_path}")
            continue
        inserted = _process_folder(cursor, folder_path, label=label)
        logger.info(f"{inserted} '{label}' mails inserted.")
        total += inserted

    conn.commit()
    logger.info(f"{total} emails inserted in total.")
    return total


def add_new_mails(cursor, conn):
    existing = get_existing_filenames(cursor)
    logger.info(f"{len(existing)} mails already in the database.")

    total_inserted = 0
    total_skipped = 0

    for label, folder_path in LABEL_FOLDERS.items():
        if not os.path.exists(folder_path):
            logger.warning(f"Folder not found, skipped: {folder_path}")
            continue

        for filename in os.listdir(folder_path):
            if not filename.endswith(".eml"):
                continue
            if filename in existing:
                total_skipped += 1
                continue
            try:
                process_email(
                    cursor, os.path.join(folder_path, filename), label, filename
                )
                total_inserted += 1
            except Exception as e:
                logger.warning(f"{filename} skipped: {e}", exc_info=True)

    conn.commit()
    logger.info(
        f"{total_inserted} new mails inserted, {total_skipped} already present skipped."
    )
    return total_inserted, total_skipped


def enrich_pending_links(cursor, conn):
    enrich_links(cursor=cursor, conn=conn)
