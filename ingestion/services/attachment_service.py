import os
import hashlib
from .utils import sanitize_text


def _get_magic_number(
    content,
):  # normally very important for fake files, but the dataset nearly have 0 attacks by attachments (was to hard to find all types of attacks)
    return content[:8].hex().upper() if content else "Unknown"


def _get_file_hash(
    content,
):  # at start, I wanted to use it and use antivirus API, but to many problem, it's not free and too long (and it just tell us if it's a threat)
    return hashlib.sha256(content).hexdigest() if content else "Unknown"


def parse_attachments(msg):  # imported by init
    attachments = []

    for part in msg.iter_attachments():
        filename = part.get_filename()
        if not filename:
            continue

        extension = (
            os.path.splitext(filename)[1].lstrip(".") if "." in filename else "Unknown"
        )

        try:
            content = part.get_payload(decode=True)
        except Exception:
            content = None

        if content:
            file_size = len(content)
            file_hash = _get_file_hash(content)
            magic_number = _get_magic_number(content)
        else:
            file_size = 0
            file_hash = "Unknown"
            magic_number = "Unknown"

        attachments.append(
            {
                "filename": sanitize_text(filename),
                "extension": sanitize_text(extension),
                "file_size": file_size,
                "file_hash": sanitize_text(file_hash),
                "magic_number": sanitize_text(magic_number),
                "content": content,
            }
        )

    return attachments


def insert_attachments(cursor, mail_number, attachments):
    if not attachments:
        return

    rows = [
        (
            mail_number,
            att["filename"],
            att["extension"],
            att.get("file_size"),
            att.get("file_hash"),
            att.get("magic_number"),
        )
        for att in attachments
    ]

    cursor.executemany(
        "INSERT INTO Attachments (Mail_Number, Filename, Extension, File_Size_Bytes, File_Hash, Magic_Number) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
