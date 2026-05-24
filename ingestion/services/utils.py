def sanitize_text(text):
    if text is None:
        return None
    if isinstance(text, str):
        return text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    return text


# The function is useful and used in all services so it's place here
