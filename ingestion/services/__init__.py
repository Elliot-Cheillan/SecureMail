from .email_service import parse_email_file, insert_mail
from .link_service import parse_links, insert_links
from .attachment_service import parse_attachments, insert_attachments
from .enrichment_service import enrich_links


def process_email(cursor, filepath, label, filename):
    msg, metadata, content = parse_email_file(filepath)
    mail_number = insert_mail(cursor, metadata, content, label, filename)
    insert_links(cursor, mail_number, parse_links(msg, metadata["date"]))
    insert_attachments(cursor, mail_number, parse_attachments(msg))
