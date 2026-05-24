import re
from urllib.parse import urlparse
from .utils import sanitize_text

_URL_PATTERN = (
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def _extract_domain(url):
    try:
        domain = urlparse(url).netloc
        return domain or "Unknown"
    except Exception:
        return "Unknown"


def _extract_urls(msg):
    urls = set()
    for part in msg.walk() if msg.is_multipart() else [msg]:
        if part.get_content_type() not in ("text/html", "text/plain"):
            continue
        try:
            payload = part.get_payload(decode=True)
            if payload:
                urls.update(
                    re.findall(_URL_PATTERN, payload.decode("utf-8", errors="ignore"))
                )
        except Exception:
            pass
    return urls


def parse_links(msg, mail_date):  # imported by init
    return [
        {
            "url": url,
            "domain": _extract_domain(url),
            "mail_date": mail_date,
            "domain_creation_date": "Not Computed",
            "redirect_url": "Not Computed",
        }
        for url in _extract_urls(msg)
    ]


def insert_links(
    cursor, mail_number, links
):  # should replace later by using pandas but it actually works well
    if not links:
        return

    rows = [
        (
            mail_number,
            sanitize_text(link["url"]),
            sanitize_text(link["domain"]),
            sanitize_text(link["mail_date"]),
            sanitize_text(link.get("domain_creation_date")),
            sanitize_text(link.get("redirect_url")),
        )
        for link in links
    ]

    cursor.executemany(
        "INSERT INTO Links (Mail_Number, URL, Domain, Mail_Date, Domain_Creation_Date, Redirect_URL) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
