import email
import re
from email import policy
from email.utils import parsedate_to_datetime
from datetime import datetime
from bs4 import BeautifulSoup
from .utils import sanitize_text


# DICT FOR DATES : SO MANY MAILS HAVE PROBLEM WITH DATES, so i made a dict to try to catch all possibilities of differents date formats
MONTH_MAP = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}

# tried to extract the date with email lib but it was horrible for some formats so this the solution I found
DATE_PATTERNS = [
    r"(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})",
    r"(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})",
    r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
    r"|January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
]

TIME_PATTERNS = [
    r"(\d{1,2}):(\d{2}):(\d{2})",
    r"(\d{1,2}):(\d{2})\s*(?:AM|PM|am|pm)?",
    r"(\d{1,2})h(\d{2})",
]


def _extract_date(text):  # kinda horrible retrievial but it works
    match = re.search(DATE_PATTERNS[0], text)
    if match:
        return f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"

    match = re.search(DATE_PATTERNS[1], text)
    if match:
        return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"

    match = re.search(DATE_PATTERNS[2], text, re.IGNORECASE)
    if match:
        month = MONTH_MAP.get(match.group(2).lower()[:3], "01")
        return f"{match.group(3)}-{month}-{match.group(1).zfill(2)}"

    return None


def _extract_time(text):  # same here
    for pattern in TIME_PATTERNS:
        match = re.search(pattern, text)
        if match:
            hour = match.group(1).zfill(2)
            minute = match.group(2)
            second = match.group(3) if len(match.groups()) == 3 else "00"
            return f"{hour}:{minute}:{second}"
    return None


def _parse_datetime(date_str):
    if not date_str:
        return "Unknown", "Unknown"

    date_str = str(date_str)

    # some formats I found several times on the dataset, it normally works on 99% of the normal mails
    # Unix timestamp
    match = re.search(r"(\d{9,10})", date_str)
    if match:
        try:
            dt = datetime.fromtimestamp(int(match.group(1)))
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except Exception:
            pass

    # RFC 2822
    for candidate in (date_str, re.sub(r"[^\w\s:+\-/]", " ", date_str)):
        try:
            dt = parsedate_to_datetime(candidate)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except Exception:
            pass

    # ISO 8601
    try:
        dt = datetime.fromisoformat(date_str.strip())
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    except Exception:
        pass

    cleaned = " ".join(date_str.split())
    return _extract_date(cleaned) or "Unknown", _extract_time(cleaned) or "Unknown"


def _extract_received_datetime(msg):
    pattern = (
        r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+(\d{1,2})\s+"
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
        r"(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})"
    )
    for value in msg.get_all("received") or []:
        match = re.search(pattern, value, re.IGNORECASE)
        if match:
            day = match.group(2).zfill(2)
            month = MONTH_MAP.get(match.group(3).lower(), "01")
            year = match.group(4)
            time_ = f"{match.group(5).zfill(2)}:{match.group(6)}:{match.group(7)}"
            return f"{year}-{month}-{day}", time_
    return "Unknown", "Unknown"


def _parse_sender(sender_raw):
    if not sender_raw:
        return "Unknown", "Unknown"

    match = re.search(r"<([^>]+)>", sender_raw)
    if match:
        addr = match.group(1).strip()
        display = sender_raw.replace(f"<{addr}>", "").strip().strip('"').strip()
        return display or "Unknown", addr

    match = re.match(r"^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", sender_raw)
    if match:
        return "Unknown", match.group(1).strip()

    return "Unknown", "Unknown"


def _parse_spf_result(msg):
    # VERY IMPORTANT TO DISTINCT ALL CASES BECAUSE THE SPF AND DKIM ARE EXTREMELY USEFUL TO DETECTS SPAMS
    spf_header = msg.get("Received-SPF")
    if spf_header:
        s = spf_header.lower()
        if "pass" in s:
            return "Pass (Legitimate)"  # it's generally safe
        if "softfail" in s:
            return "SoftFail (Suspect)"  # very weird but not absolutely a threat
        if "fail" in s:
            return "Fail (Threat)"  # absolute scam or spam (literraly a spam mail if it returns this)
        if "neutral" in s:
            return "Neutral (No Info)"  # can't be used very well
        if "none" in s:
            return "None (No Info)"  # not suspect but not trustable, take a look
        if "temperror" in s:
            return "TempError (Temporary Issue)"  # kinda suspect
        if "permerror" in s:
            return "PermError (Config Error)"  # suspect

    auth_results = msg.get("Authentication-Results")
    if auth_results:
        a = auth_results.lower()
        if "spf=pass" in a:
            return "Pass (Legitimate)"
        if "spf=softfail" in a:
            return "SoftFail (Suspect)"
        if "spf=fail" in a:
            return "Fail (Threat)"
        if "spf=neutral" in a:
            return "Neutral (No Info)"
        if "spf=none" in a:
            return "None (No Info)"
        if "spf=temperror" in a:
            return "TempError (Temporary Issue)"
        if "spf=permerror" in a:
            return "PermError (Config Error)"

    return "Missing"  # it's the norm to have spf and dkim in his mail, it's really suspect if it's Missing and it's recent mail


def _parse_dkim_result(msg):
    dkim_sig = msg.get("DKIM-Signature")
    auth_results = msg.get("Authentication-Results")

    if not dkim_sig and not auth_results:
        return "Missing"

    if auth_results:
        a = auth_results.lower()
        if "dkim=pass" in a:
            return "Pass (Legitimate)"  # in most cases it's safe
        if "dkim=fail" in a:
            return "Fail (Modified or Forged)"  # obviously a spam
        if "dkim=neutral" in a:
            return "Neutral (Unverifiable)"  # can't be used
        if "dkim=none" in a:
            return "None (Not Signed)"  # not full safe, not full threat
        if "dkim=temperror" in a:
            return "TempError (Temporary Issue)"  # errors are suspect, take a look
        if "dkim=permerror" in a:
            return "PermError (Config Error)"  # suspect

    return "Present (Not Verified)" if dkim_sig else "Unknown"


def _parse_mailer(msg):

    return (
        msg.get("X-Mailer") or msg.get("User-Agent") or "Missing"
    )  # in most case it's missing idk if it's the email lib that don't know how to parse it correctly


# the content parsing is plain gross, cause scams mails have a disgusting structure and encoding, but it return
# if the content is empty, and replace the links and attachments by a [link] or [attachment]
def _clean_html_content(html):
    if not html:
        return ""
    if "<" not in html:
        return _clean_plain_text(html)
    try:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(["script", "style", "head", "title", "meta"]):
            tag.decompose()
        for img in soup.find_all("img"):
            img.replace_with("[Image]")
        for a in soup.find_all("a"):
            text = a.get_text(strip=True)
            a.replace_with(f"{text} [Lien]" if text else "[Lien]")

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\[Image\]\s*\[Image\]", "[Image]", text)
        text = re.sub(r"\[Lien\]\s*\[Lien\]", "[Lien]", text)
        return text.strip()
    except Exception as e:
        return f"[Error parsing HTML: {e}]"


def _clean_plain_text(plain):
    if not plain:
        return ""
    text = re.sub(r'http[s]?://[^\s<>"]+', "[Lien]", plain)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[Lien\]\s*\[Lien\]", "[Lien]", text)
    return text.strip()


def _parse_content(msg):
    body_html = body_plain = None

    for part in msg.iter_parts() if msg.is_multipart() else [msg]:
        ct = part.get_content_type()
        try:
            if ct == "text/plain" and body_plain is None:
                body_plain = part.get_content()
            elif ct == "text/html" and body_html is None:
                body_html = part.get_content()
        except Exception:
            pass

    if body_html:
        cleaned = _clean_html_content(body_html)
    elif body_plain:
        cleaned = _clean_plain_text(body_plain)
    else:
        cleaned = ""

    if not cleaned or cleaned.isspace() or cleaned.strip() == "[Image]":
        has_images = any(
            p.get_content_type().startswith("image/") for p in msg.iter_parts()
        )
        return (
            "[No text content - Email contains only images]"
            if has_images
            else "[No content]"
        )

    return cleaned


def parse_email_file(filepath=None, file_bytes=None):  # imported by init

    # Here, I added a file_bytes parameter for the web app, cause I didn't expect to create a web app later with this project. So the pipeline
    # is not adapted to receive a file, but open a file in folder. With this parameter I can change the pipeline without modificate the
    # code for all the project. Then we can use a different pipeline if you use the project with the website, or the raw code.

    if file_bytes is None:
        if filepath is None:
            return None
        with open(filepath, "rb") as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
    else:
        msg = email.message_from_bytes(file_bytes, policy=policy.default)

    date, time = _parse_datetime(msg.get("date", ""))
    if date == "Unknown" or time == "Unknown":
        rec_date, rec_time = _extract_received_datetime(msg)
        if date == "Unknown":
            date = rec_date
        if time == "Unknown":
            time = rec_time

    sender_raw = msg.get("From")
    sender_display, sender_email = _parse_sender(sender_raw)

    reply_to_raw = msg.get("Reply-To")
    if reply_to_raw:
        _, reply_to_email = _parse_sender(reply_to_raw)
    else:
        reply_to_email = "Missing"

    try:
        subject = msg.get("subject", "No subject")
    except Exception:
        subject = "No subject"

    metadata = {
        "sender_display": sanitize_text(sender_display),
        "sender_email": sanitize_text(sender_email),
        "reply_to_email": sanitize_text(reply_to_email),
        "date": sanitize_text(date),
        "time": sanitize_text(time),
        "subject": sanitize_text(subject),
        "x_mailer": sanitize_text(_parse_mailer(msg)),
        "spf_result": sanitize_text(_parse_spf_result(msg)),
        "dkim_result": sanitize_text(_parse_dkim_result(msg)),
    }

    return msg, metadata, _parse_content(msg)


def insert_mail(cursor, metadata, content, label, filename):
    cursor.execute(
        """
        INSERT INTO Mails (
            Sender_Display_Name, Sender_Email, Reply_To_Email,
            Date, Time, Subject, X_Mailer, SPF_Result, DKIM_Result,
            Content, Filename, Label
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            metadata["sender_display"],
            metadata["sender_email"],
            metadata["reply_to_email"],
            metadata["date"],
            metadata["time"],
            metadata["subject"],
            metadata["x_mailer"],
            metadata["spf_result"],
            metadata["dkim_result"],
            content,
            filename,
            label,
        ),
    )
    return cursor.lastrowid
